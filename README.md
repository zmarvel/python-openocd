
# ocd-monitor

Part of this project is a thin Python wrapper around some of OpenOCD's 
functionality, like reading/writing memory and registers. Then, given an ELF
file running on a target, we can find the addresses of symbols, which lets us
call functions and observe their effects.

Fortunately, part of the work is already done. In OpenOCD's tree, an example can
be found in contrib/rpc\_examples/ocd\_rpc\_example.py that reads/writes memory
and registers.

## Todo

1. Call a function with arguments but no return value (e.g. toggle LED)
   - Halt target
   - Configure `debug-halted` event so the host knows when we hit a breakpoint
   - Copy pc into lr
   - Set breakpoint at lr
   - Save r0-r3
   - Prepare arguments
   - Load function address into pc
   - Resume
   - `debug-halted` event occurs
   - Remove breakpoint
   - Resume
2. Call a function for its return value (e.g. get LED value)
   - Halt target
   - Configure `debug-halted` event so the host knows when we hit a breakpoint
   - Copy pc into lr
   - Set breakpoint at lr
   - Save r0-r3
   - Prepare arguments
   - Load function address into pc
   - Resume
   - `debug-halted` event occurs
   - Remove breakpoint
   - Retrieve r0
   - Resume
3. Call a series of functions to perform e.g. a SPI transaction

Event configuration and deconfiguration can happen at the start and end of a
session rather than surrounding every function call as long as each function
call cleans up its breakpoints.

If the function has no return value, we don't need to set a breakpoint if it's
the last function we call in the session (we don't have to wait for its return
to call another function).
