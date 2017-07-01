
import ocd
import nm

BUFSIZE = 2048


class Target():
    def __init__(self, openocd, elf_file):
        self.ocd = openocd
        self.symbol_table = nm.SymbolTable(elf_file)
        self.buffer = bytearray(BUFSIZE)

    def call(self, function, halt=False, resume=False):
        """Lookup the functions address in the provided ELF file using
        `self.symbol_table` and call it using OpenOCD
        """
        addr = self.symbol_table.lookup_address("toggle_led")

        if halt:
            self.ocd.halt()
        val = self.ocd.call(addr)
        if resume:
            self.ocd.resume()
        return val

    def toggle_led(self):
        self.call("toggle_led")

    def get_led(self):
        val = self.call("get_led")
        return val

    def set_led(self, val):
        if val != 0 and val != 1:
            raise ValueError("expecting 0 or 1")
        self.call("set_led")


if __name__ == "__main__":
    from time import sleep

    def print_led(state):
        if state == 0:
            print("LED is off")
        elif state == 1:
            print("LED is on")
        else:
            print("Saw unexpected LED state")

    with ocd.OpenOCD() as openocd:
        mon = Target(openocd,
                     "/home/zack/src/acceltag_chibios/firmware/build/ch.elf")
        state = mon.get_led()
        print_led(state)
        for _ in range(10):
            mon.toggle_led()
            sleep(0.1)

        state = mon.get_led()
        print_led(state)
        sleep(2)
        mon.set_led(0)
        sleep(2)
        mon.set_led(1)
        sleep(2)
        mon.set_led(0)
        sleep(2)
