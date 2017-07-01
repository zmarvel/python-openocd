
# TODO

- Some way to make sure the image flashed on the target matches the loaded
  ELF file
- Disable and enable interrupts. An interrupt could occur during a test.
- How can we work around waiting on locks? We want to be able to test periphs
  over SPI, for example, but as it stands function calls act like ISRs.
