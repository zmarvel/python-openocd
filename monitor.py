
from time import sleep

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
        if val != 0 and val != 1:
            raise ValueError('expecting 0 or 1')

        symbol = nm.find_symbol(self.symbol_list, "set_led")
        with OpenOcd() as ocd:
            ocd.halt()
            sleep(0.1)
            ocd.call(symbol.address, val)
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

    mon = Monitor("/home/zack/src/acceltag_chibios/firmware/build/ch.elf")
    print('monitor initialized')

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
