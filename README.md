
# ocd-monitor

Part of this project is a thin Python wrapper around some of OpenOCD's 
functionality, like reading/writing memory and registers. Then, given an ELF
file running on a target, we can find the addresses of symbols, which lets us
call functions and observe their effects.

# Test cases

A use case for this project is automated testing on a target. `test_case.py`
provides an example using Python's unittest mostly as a test-runner. If OpenOCD
is listening, you can run the example from the project root with
```
$ python3 -m unittest test_case
```
Just make sure to modify the path to match the location of the elf file which
is loaded on the target.

# ChibiOS notes

This project is being developed with a target running ChibiOS 17.6.x. Since
function calls are performed by looking up a symbol in the output of `nm`
with the provided ELF file, functions that do not appear in the symbol table,
such as macros, inline functions, and even because of optimizations cannot be
called. I had to build ChibiOS with `make USE_LINK_GC=no USE_LTO=no`.

Currently if a function on the target is called with this API, it should avoid
waiting on resources that might be locked, like an ISR would do. The API also
makes no attempt to disable interrupts, but it will in the future.
