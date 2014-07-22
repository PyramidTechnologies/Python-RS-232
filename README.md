Python-RS-232
=============

A Python RS-232 sample that uses the [PySerial library](http://pyserial.sourceforge.net/).

## Requirements

1. A supported bill validator
   - Apex 7000
   - Apex 5000
   - Trilogy *requires RS-232 firmware*
   - Curve *require RS-232 firmware*
2. Communication Harness
   - [Recommended Harness](http://shop.pyramidacceptors.com/usb-rs-232-communication-cable-harness-for-apex-05aa0023/)
   - Or a DB9 RS-232 connection, USB UART cable of your choice

## Setup
1. Install PySerial
2. Ensure you have Python 2 or 3 installed, we use 2.7
3. Ensure you communication cable is recognized by your OS.
   - If you chose the recommended harness, this is plug and play on Windows and Linux
   - On Mac, please see [FTDI Documentation](http://www.ftdichip.com/Support/Documents/InstallGuides/Mac_OS_X_Installation_Guide.pdf)
4. Find the name of the port you are connected to
   - Windows, look in the device manager
   - Linux,Mac,BSD: `ls /dev/tty.*`
5. Run the file and pass the port name as an argument
`python main.py COM4` or `python main.py /dev/tty/USB0`

## Questions
Please [let us know](https://github.com/PyramidTechnologies/Python-RS-232/issues/new).


![](https://googledrive.com/host/0B79TkjL8Nm20QjU0UGhObnBTUE0/logo_2.jpg)
