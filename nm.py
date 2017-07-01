"""Look up symbols in an ELF file.
"""
from collections import namedtuple
import subprocess
import re

Symbol = namedtuple('Symbol', ['name', 'type', 'address'])


symbol_regex = re.compile('^([0-9a-f]+) ([A-z]) ([A-z0-9_.\$]+)$',
                          flags=re.MULTILINE)


def list_symbols(elf_file):
    proc = subprocess.run(['nm', elf_file], stdout=subprocess.PIPE)
    text = proc.stdout.decode()
    return symbol_regex.findall(text)


def find_symbol(nm_output, symbol_name):
    result = re.search('^([0-9a-f]+) ([A-z]) {}$'.format(symbol_name),
                       nm_output, flags=re.MULTILINE)
    if result is None:
        return None
    else:
        return Symbol(name=symbol_name, type=result.group(2),
                      address=int(result.group(1), 16))


class SymbolTable():
    """On initialization, loads an ELF file to make looking up symbol addresses
    and types by name easy.
    """
    def __init__(self, elf_file):
        self.elf_file = elf_file
        self._table = {}
        """An internal dict mapping symbol names to their address and type as
        a tuple (int, str).
        """
        self._load_table()

    def _load_table(self):
        """Assumes `self.elf_file` has already been loaded and `self._table`
        has been initialized as an empty dict.
        """
        for tup in list_symbols(self.elf_file):
            self._table[tup[2]] = (int(tup[0], 16), tup[1])

    def lookup(self, name):
        return self._table[name]

    def lookup_address(self, name):
        addr, type = self._table[name]
        return addr

    def lookup_type(self, name):
        addr, type = self._table[name]
        return type


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description=(
        'Find a symbol\'s address in an ELF file'
    ))
    parser.add_argument('elf_file', type=str)
    parser.add_argument('symbol_name', type=str)
    args = parser.parse_args()

    symbol_table = SymbolTable(args.elf_file)
    symbol = symbol_table.lookup(args.symbol_name)
    print(symbol)
