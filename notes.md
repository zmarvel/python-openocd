
# Notes

## Testing a SPI peripheral

Using SPI is more complicated than toggling an LED. The debugger could attach to
ChibiOS in a number of states, and we could create a deadlock if we aren't
careful. Also, function calls we perform with the debugger could be interrupted.
We can disable interrupts, but we might not want to if we want to use DMA-driven
SPI calls, for example, which rely on interrupts.

A safe strategy is to reset and halt the system at the beginning of the test,
then set a breakpoint somewhere the system is in a known state before resuming
execution---for example, the main thread.

### Testing from the shell

Another strategy is communicating with the ChibiOS shell with a UART adapter.
There are some evident disadvantages:
- The target must have a shell command to support a test.
- The target must have a shell running. Shell support requires a few ChibiOS
  features which would not normally be built, such as heap-allocated threads
  and the mempools API, as well as the shell code itself and any commands.

The main advantage is simplicity. Calling functions across a debug interface
might feel clunky and requires special care. Writing tests in C to run directly
on the target is quicker. Although they replicate the production environment
less closely, they give us a higher chance of catching regressions than no
tests at all.


## Build notes

If running under ChibiOS, make sure `USE_LINK_GC` and `USE_LTO` are set to no in
the Makefile.
