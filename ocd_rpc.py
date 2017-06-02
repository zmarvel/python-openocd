#!/usr/bin/env python3
"""
Thin wrapper around part of OpenOCD's Tcl interface. Supports reading and
writing memory and registers.

Based on OpenOCD RPC example by Andreas Ortmann (ortmann@finf.uni-hannover.de)
"""

import socket
import itertools

def strtohex(data):
    return map(strtohex, data) if isinstance(data, list) else int(data, 16)

def hexify(data):
    return "<None>" if data is None else ("0x%08x" % data)

def compare_data(a, b):
    for i, j, num in zip(a, b, itertools.count(0)):
        if i != j:
            print("difference at %d: %s != %s" % (num, hexify(i), hexify(j)))

class OpenOcd():
    COMMAND_TOKEN = '\x1a'
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.tcl_ip = "127.0.0.1"
        self.tcl_port = 6666
        self.buffer_size = 4096

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __enter__(self):
        self.sock.connect((self.tcl_ip, self.tcl_port))
        return self

    def __exit__(self, type, value, traceback):
        try:
            self.send("exit")
        finally:
            self.sock.close()

    def send(self, cmd):
        """Send a command string to TCL RPC. Return the result that was read."""
        data = (cmd + OpenOcd.COMMAND_TOKEN).encode("utf-8")
        if self.verbose:
            print("<- ", data)

        self.sock.send(data)
        return self._recv()

    def _recv(self):
        """Read from the stream until the token (\x1a) was received."""
        data = bytes()
        while True:
            chunk = self.sock.recv(self.buffer_size)
            data += chunk
            if bytes(OpenOcd.COMMAND_TOKEN, encoding="utf-8") in chunk:
                break

        if self.verbose:
            print("-> ", data)

        data = data.decode("utf-8").strip()
        data = data[:-1] # strip trailing \x1a

        return data

    def read_variable(self, address):
        raw = self.send("ocd_mdw 0x%x" % address).split(": ")
        return None if (len(raw) < 2) else strtohex(raw[1])

    def read_memory(self, wordLen, address, n):
        self.send("array unset output") # better to clear the array before
        self.send("mem2array output %d 0x%x %d" % (wordLen, address, n))

        output = self.send("ocd_echo $output").split(" ")

        return [int(output[2*i+1]) for i in range(len(output)//2)]

    def write_variable(self, address, value):
        assert value is not None
        self.send("mww 0x%x 0x%x" % (address, value))

    def write_memory(self, wordLen, address, n, data):
        array = " ".join(["%d 0x%x" % (a, b) for a, b in enumerate(data)])

        self.send("array unset buffer") # better to clear the array before
        self.send("array set buffer { %s }" % array)
        self.send("array2mem buffer  0x%x %s %d" % (wordLen, address, n))

if __name__ == "__main__":

    def show(*args):
        print(*args, end="\n\n")

    with OpenOcd() as ocd:
        ocd.send("reset")

        show(ocd.send("ocd_echo \"echo says hi!\"")[:-1])
        show(ocd.send("capture \"ocd_halt\"")[:-1])

        # Read the first few words at the RAM region (put starting adress of RAM
        # region into 'addr')
        addr = 0x10000000

        value = ocd.read_variable(addr)
        show("variable @ %s: %s" % (hexify(addr), hexify(value)))

        ocd.write_variable(addr, 0xdeadc0de)
        show("variable @ %s: %s" % (hexify(addr), hexify(ocd.read_variable(addr))))

        data = [1, 0, 0xaaaaaaaa, 0x23, 0x42, 0xffff]
        wordlen = 32
        n = len(data)

        read = ocd.read_memory(wordlen, addr, n)
        show("memory (before):", list(map(hexify, read)))

        ocd.write_memory(wordlen, addr, n, data)

        read = ocd.read_memory(wordlen, addr, n)
        show("memory  (after):", list(map(hexify, read)))

        compare_data(read, data)

        ocd.send("resume")
