
# ocd-monitor

Part of this project is a thin Python wrapper around some of OpenOCD's 
functionality, like reading/writing memory and registers. Then, given an ELF
file running on a target, we can find the addresses of symbols, which lets us
call functions and observe their effects.

Fortunately, part of the work is already done. In OpenOCD's tree, an example can
be found in contrib/rpc\_examples/ocd_rpc_example.py that reads/writes memory
and registers.
