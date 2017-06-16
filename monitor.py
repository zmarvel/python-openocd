
from ocd import OpenOcd
import nm

BUFSIZE = 2048

class Monitor():
    def __init__(self, elf_file):
        self.symbol_list = nm.list_symbols(elf_file)
        self.buffer = bytearray(BUFSIZE)

    def toggle_led(self):
        symbol = nm.find_symbol(self.symbol_list, "toggle_led")
        with OpenOcd() as ocd:
            ocd.halt()
            ocd.call(symbol.address)
            ocd.resume()

    def get_led(self):
        symbol = nm.find_symbol(self.symbol_list, "get_led")
        with OpenOcd() as ocd:
            ocd.halt()
            val = ocd.call(symbol.address)
            ocd.resume()
        return val

    def set_led(self, val):
        # TODO this doesn't prepare any arguments
        if val != 0 and val != 1:
            raise ValueError('expecting 0 or 1')

        symbol = nm.find_symbol(self.symbol_list, "set_led")
        with OpenOcd() as ocd:
            ocd.halt()
            ocd.call(symbol.address)
            ocd.resume()

if __name__ == "__main__":
    from time import sleep

    def print_led(state):
        if state == 0:
            print('LED is off')
        elif state == 1:
            print('LED is on')
        else:
            print('Saw unexpected LED state')

    mon = Monitor("target/build/ch.elf")
    print('monitor initialized')
    sleep(0.1)
    print('calling get_led')
    state = mon.get_led()
    sleep(0.1)
    print_led(state)
    sleep(0.1)

    mon.toggle_led()
    sleep(0.1)

    state = mon.get_led()
    sleep(0.1)
    print_led(state)

