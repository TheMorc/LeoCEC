# LeoCEC *(CEC-Tiny-Pro fork)*
Support for the HDMI CEC protocol with minimal hardware, running on an ATMega microprocessor, now with UART support.

I basically made all of this only as a minimal viable product for a HDMI-CEC controller for my new HTPC.
HTPC being a mini PC computer, lacks HDMI-CEC support by default and I had no other stuff lying around,
so I put this mess together from literal scrap.

The code is a fork of [Szymon's code](https://github.com/SzymonSlupik/CEC-Tiny-Pro), with minor modifications:
* It can now listen for commands sent over the serial port, the implementation is literal ass.
* Code got botched so much by me, sorry :/

![alt text](https://github.com/TheMorc/LeoCEC/blob/main/chaos.jpg?raw=true "This is how it looks in the TV")
![alt text](https://github.com/TheMorc/LeoCEC/blob/main/HDMI%20CEC%20to%20Beetle%20Schematic.jpg?raw=true "HDMI CEC to Beetle Schematic")
