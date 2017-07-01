#!/usr/bin/env python3
"""
Thin wrapper around part of OpenOCD's Tcl interface. Supports reading and
writing memory and registers.

Based on OpenOCD RPC example by Andreas Ortmann (ortmann@finf.uni-hannover.de)
"""

import socket
import itertools
from time import sleep


def strtohex(data):
    return map(strtohex, data) if isinstance(data, list) else int(data, 16)


def hexify(data):
    return "<None>" if data is None else ("0x%08x" % data)


def compare_data(a, b):
    for i, j, num in zip(a, b, itertools.count(0)):
        if i != j:
            print("difference at %d: %s != %s" % (num, hexify(i), hexify(j)))


class OCDError(Exception):
    pass


class OpenOCD():
    COMMAND_TOKEN = '\x1a'

    def __init__(self, verbose=False, tcl_ip="127.0.0.1", tcl_port=6666):
        self.verbose = verbose
        self.tcl_ip = tcl_ip
        self.tcl_port = tcl_port
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
        """Send a command string to TCL RPC. Return the result that was read.
        """
        if self.verbose:
            print(cmd)
        data = (cmd + OpenOCD.COMMAND_TOKEN).encode("utf-8")
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
            if bytes(OpenOCD.COMMAND_TOKEN, encoding="utf-8") in chunk:
                break

        if self.verbose:
            print("-> ", data)

        data = data.decode("utf-8").strip()
        data = data[:-1]  # strip trailing \x1a

        return data

    def read_variable(self, address):
        raw = self.send("ocd_mdw 0x%x" % address).split(": ")
        return None if (len(raw) < 2) else strtohex(raw[1])

    def read_memory(self, wordLen, address, n):
        self.send("array unset output")  # better to clear the array before
        self.send("mem2array output %d 0x%x %d" % (wordLen, address, n))

        output = self.send("ocd_echo $output").split(" ")

        return [int(output[2*i+1]) for i in range(len(output)//2)]

    def write_variable(self, address, value):
        assert value is not None
        self.send("mww 0x%x 0x%x" % (address, value))

    def write_memory(self, wordLen, address, n, data):
        array = " ".join(["%d 0x%x" % (a, b) for a, b in enumerate(data)])

        self.send("array unset buffer")  # better to clear the array before
        self.send("array set buffer { %s }" % array)
        self.send("array2mem buffer  0x%x %s %d" % (wordLen, address, n))

    def read_register(self, reg):
        raw = self.send("ocd_reg {} force".format(reg))
        value = raw.split(":")[1].strip()

        return int(value, 16)

    def write_register(self, reg, value):
        self.send("ocd_reg {} {:#x}".format(reg, value))

    def push(self, value):
        sp = self.read_register("sp")
        self.write_register("sp", sp - 4)
        self.write_variable(sp - 4, value)

    def pop(self):
        sp = self.read_register("sp")
        value = self.read_variable(sp)
        self.write_register("sp", sp + 4)
        return value

    def set_breakpoint(self, addr):
        self.send("ocd_bp {:#x} 2".format(addr))

    def delete_breakpoint(self, addr):
        self.send("ocd_rbp {:#x}".format(addr))

    def reset(self, halt=True):
        """Reset the target. The default sends `reset halt` to OpenOCD, but
        specifying `halt=False` will send `reset run`.
        """
        if halt:
            self.send("reset halt")
        else:
            self.send("reset run")

    def curstate(self):
        return self.send("$_TARGETNAME curstate")

    def halt(self):
        self.send("halt")

    def resume(self):
        self.send("resume")

    def set_tcl_variable(self, name, value):
        self.send("set {} {}".format(name, value))

    def get_tcl_variable(self, name):
        self.send("set {}".format(name))

    def call(self, addr, *args):
        """Call the function at `addr`. The target must be halted before calling
        this method, and it must be resumed afterwards.
        """
        if len(args) > 4:
            raise OCDError("A maximum of 4 1-word arguments are accepted")

        addr = addr & 0xfffffffe

        if self.curstate() != "halted":
            raise OCDError("Target must be halted to call function")
        # save caller-save registers
        regnames = ["pc", "lr", "sp", "r0", "r1", "r2", "r3"]
        regs = {reg: self.read_register(reg) for reg in regnames}
        for i, arg in enumerate(args):
            self.write_register("r{}".format(i), arg)

        self.send("set call_done 0")
        self.send(("$_TARGETNAME configure -event halted "
                   "{ set call_done 1 ; echo done }"))
        self.send(("$_TARGETNAME configure -event debug-halted "
                   "{ set call_done 1 ; echo done }"))
        self.write_register("lr", regs["pc"] | 1)
        self.write_register("pc", addr)
        self.set_breakpoint(regs["pc"])
        self.resume()
        while self.send("set call_done") != '1':
            sleep(0.01)

        ret = self.read_register("r0")
        self.send("$_TARGETNAME configure -event halted { }")
        self.send("$_TARGETNAME configure -event debug-halted { }")
        self.delete_breakpoint(regs["pc"])
        for name, val in regs.items():
            self.write_register(name, val)
        return ret
