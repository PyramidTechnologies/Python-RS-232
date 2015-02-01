# -*- coding: utf-8 -*-
"""
Created on Sun Feb 01 13:45:57 2015

@author:

--------------------------------------------------------------------
'***********************************************************************
'*      Pyramid Technologies, Inc.  RS-232 Interface Program           *
'*               Copyright 2014 Pyramid Technologies, Inc.             *
'***********************************************************************
'If you have purchased PTI Bill Acceptors, we hope that you
'can use this source code to assist you with your kiosk or vending
'application, and that it is a positive and profitable experience for you.
'
'You may use and integrate this source code freely, provided
'the terms and conditions are adhered to.
'By using this software, you agree to the following terms and conditions:
'
' 1.  This software is provided "as is" to the user.  PTI assumes no
' responsibility for any damages which may result from the use or misuse
' of this software.  The user is entirely responsible for any consequences
' resulting from the integration of this source code into the user's system.
'
' 2.  Although PTI will likely choose to provide technical support for the
' use of this source code, PTI is not obligated to do so.
'
' 3.  This source code may not be re-distributed or published without
'   expressed,  written permission from Pyramid Technologies, Inc.
'
' 4.  This copyright notice and agreement must not be deleted from the source
' code if any or all of PTI's source code is integrated into the user's
'   application.
'
' 5.  Permission to use this software will be revoked if it is used in a way
' that is deemed damaging to PTI, or used for purposes which are illegal
' or damaging to others, or otherwise not representing the intended, proper
' use it was designed for.
'***********************************************************************
"""

from threading import Thread
import serial, time, binascii

### Globals ###
#Change this value to modify polling rate. Currently 100 ms
POLL_RATE = 0.1


class Host(object):
    """
    An RS-232 master interface. A master operates with a RS-232
    slave for the purpose of accepting money in exchange for goods or services.
    """


    state_dict = {1:"Idling ", 2:"Accepting ", 4:"Escrowed ", 8:"Stacking ",
                  16:"Stacked ", 32:"Returning", 64:"Returned",
                  17:"Stacked Idling ", 65:"Returned Idling "}
    event_dict = {0:"", 1:"Cheated ", 2:"Rejected ", 4:"Jammed ", 8:"Full "}

    def __init__(self):
        # Set to False to kill
        self.running = True
        self.bill_count = bytearray([0, 0, 0, 0, 0, 0, 0, 0])

        self.ack = 0
        self.credit = 0
        self.last_state = ''
        self.escrowed = False
        self.verbose = False

        # Background worker thread
        self._serial_thread = None

    def start(self, portname):
        """
        Start Host in a non-daemon thread

        Args:
            portname -- string name of the port to open and listen on

        Returns:
            None

        """
        self._serial_thread = Thread(target=self._serial_runner,
                                     args=(portname,))
        # Per https://docs.python.org/2/library/threading.html#thread-objects
        # 16.2.1: Daemon threads are abruptly stopped, set to false for proper
        # release of resources (i.e. our comm port)
        self._serial_thread.daemon = False
        self._serial_thread.start()


    def stop(self):
        """
        Blocks until Host can safely be stopped

        Args:
            None

        Returns:
            None
        """
        self.running = False
        self._serial_thread.join()

    def parse_cmd(self, cmd):
        """
        Applies the given command to modify the state/event of
        this Host

        Args:
            cmd -- string arg

        Returns:
            Int -- 0 if okay, 1 to exit, 2 to quit
        """
        if cmd is 'Q':
            return 1
        if cmd is '?' or cmd is 'H':
            return 2

        if cmd is 'V':
            self.verbose = not self.verbose

        return 0

    def _serial_runner(self, portname):
        """
        Polls and interprets message from slave acceptor over serial port
        using global poll rate

        Args:
            portname -- string portname to open

        Returns:
            None
        """

        ser = serial.Serial(
            port=portname,
            baudrate=9600,
            bytesize=serial.SEVENBITS,
            parity=serial.PARITY_EVEN,
            stopbits=serial.STOPBITS_ONE
        )

        while ser.isOpen() and self.running:

            # basic message   0      1      2      3      4      5    6      7
            #               start, len,  ack, bills,escrow,resv'd,end, checksum
            msg = bytearray([0x02, 0x08, 0x10, 0x7F, 0x10, 0x00, 0x03, 0x00])

            msg[2] = 0x10 | self.ack
            self.ack ^= 1

            # If escrow, stack the note
            if self.escrowed:
                msg[4] |= 0x20

            # Set the checksum
            msg[7] = msg[1] ^ msg[2]
            for byte in xrange(3, 3):
                msg[7] ^= msg[byte]


            ser.write(msg)
            time.sleep(0.1)

            out = ''
            while ser.inWaiting() > 0:
                out += ser.read(1)
            if out == '':
                continue


            # With the exception of Stacked and Returned, only we can
            # only be in one state at once
            status = Host.state_dict[ord(out[3])]
            self.escrowed = ord(out[3]) & 4
            if ord(out[3]) & 0x10:
                status += " STACKED "
            if ord(out[3]) & 0x40:
                status += " RETURNED "

            # If there is no match, we get an empty string
            status += Host.event_dict[ord(out[4]) & 1]
            status += Host.event_dict[ord(out[4]) & 2]
            status += Host.event_dict[ord(out[4]) & 4]
            status += Host.event_dict[ord(out[4]) & 8]
            if ord(out[4]) & 0x10 != 0x10:
                status += " CASSETTE MISSING"

            # Only update the status if it has changed
            if self.last_state != status:
                print 'Acceptor status:', status
                self.last_state = status

            if self.verbose:
                print ", ".join("0x{:02x}".format(ord(c)) for c in out)

            # Print credit(s)
            credit = (ord(out[5]) & 0x38) >> 3

            if credit != 0:
                if ord(out[3]) & 0x10:
                    print "Bill credited: Bill#", credit
                    self.bill_count[credit] += 1
                    print "Acceptor now holds:", binascii.hexlify(self.bill_count)

            time.sleep(POLL_RATE)

        print "port closed"
        ser.close()

