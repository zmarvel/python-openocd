
from collections import namedtuple
import subprocess
import re

Symbol = namedtuple('Symbol', ['name', 'type', 'address'])

def list_symbols(elf_file):
    proc = subprocess.run(['nm', elf_file], stdout=subprocess.PIPE)

    return proc.stdout.decode()

def find_symbol(nm_output, symbol_name):
    result = re.search('^([0-9a-f]+) ([A-z]) {}$'.format(symbol_name),
            nm_output, flags=re.MULTILINE)
    if result is None:
        return None
    else:
        return Symbol(name=symbol_name, type=result.group(2),
                address=int(result.group(1), 16))

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description=(
        'Find a symbol\'s address in an ELF file'
        ))
    parser.add_argument('elf_file', type=str)
    parser.add_argument('symbol_name', type=str)
    args = parser.parse_args()

    symbol_list = list_symbols(args.elf_file)
    symbol = find_symbol(symbol_list, args.symbol_name)
    print(symbol)
