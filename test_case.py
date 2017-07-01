
from time import sleep
import unittest
import nm
import ocd
import target


class OCDTestCase(unittest.TestCase):
    """Example test case. Note that OpenOCD must be attached to the target; if
    the connection fails, an exception will be raised."""
    def setUp(self):
        self.elf_file = "/home/zack/src/acceltag_chibios/firmware/build/ch.elf"
        self.symbol_table = nm.SymbolTable(self.elf_file)
        self.openocd = ocd.OpenOCD().__enter__()
        self.target = target.Target(self.openocd, self.elf_file)

    def tearDown(self):
        if self.openocd.curstate() != "running":
            self.openocd.resume()
        self.openocd.__exit__(None, None, None)

    def test_led_functions(self):
        self.openocd.reset(halt=False)
        sleep(1)
        self.openocd.halt()

        initial_state = self.target.get_led()
        self.target.toggle_led()
        new_state = self.target.get_led()
        self.assertGreaterEqual(initial_state, 0)
        self.assertLessEqual(initial_state, 1)
        self.assertGreaterEqual(new_state, 0)
        self.assertLessEqual(new_state, 1)
        if initial_state == 0:
            self.assertEqual(new_state, 1)
        elif initial_state == 1:
            self.assertEqual(new_state, 0)

        self.openocd.resume()
