#!/usr/bin/env python

'''
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
' 3.  This source code may not be re-distributed or published without expressed,
' written permission from Pyramid Technologies, Inc.
'
' 4.  This copyright notice and agreement must not be deleted from the source
' code if any or all of PTI's source code is integrated into the user's application.
'
' 5.  Permission to use this software will be revoked if it is used in a way
' that is deemed damaging to PTI, or used for purposes which are illegal
' or damaging to others, or otherwise not representing the intended, proper
' use it was designed for.
'***********************************************************************

'Overview:
'
'This software provides a framework for interfacing a Linux device 
'(e.g. Raspberry Pi) to a Pyramid Bill Acceptor configured for RS-232.
'It is intended for users who want to get up and running quickly with
'kiosk or other PC applications requiring a bill acceptor interface.
'
'This application (as provided by PTI) contains fully functional
'serial communications.  The information received from the bill
'acceptor is translated into an organized set of global variables.
'Simply monitor the states of these variables to determine what
'events have taken place with the bill acceptor, and then take
'whatever action is appropriate for your system. Similarly, a set
'of global variables controls the messages sent by the PC to the
'bill acceptor. This simplification allows you to focus on your
'kiosk application without concern for the low-level routines
'which carry out the details of the RS-232 Interface.
'
'Although the low-level communication code is written for you,
'it is still important to understand what the RS232 interface
'does.  A basic understanding of states, events, and the polling
'process will help you integrate this code into your end application.
'The RS232 Interface Specification is located online at:
'http://www.pyramidacceptors.com/files/RS_232.pdf

'''

import serial, time, binascii, sys

### Globals ###
#Change this value to modify polling rate. Currently 100 ms
PollRate = 0.1
    
### Main  Routine ###   
def main(portname):

    print "Starting Master on Port {:s}".format(portname)
    
    ser = serial.Serial(
        port=portname,
        baudrate=9600,
        bytesize=serial.SEVENBITS,
        parity=serial.PARITY_EVEN,
        stopbits=serial.STOPBITS_ONE
    )
    
    ack = 0
    credit = 0
    lastState = ''
    billCount = bytearray([0,0,0,0,0,0,0,0])
    escrowed = False

    while ser.isOpen():
    
        # basic message   0      1      2      3      4      5      6      7
        #               start,   len,   ack, bills,escrow,resv'd,  end, checksum
        msg = bytearray([0x02,  0x08,  0x10,  0x7F,  0x10,  0x00,  0x03,  0x00])
        
        msg[2] = 0x10 | ack
        ack ^= 1
            
        # If escrow, stack the note
        if (escrowed):
            msg[4] |= 0x20
    
        # Set the checksum
        msg[7] = msg[1] ^ msg[2]
        for b in xrange(3,3):
            msg[7] ^= msg[b]
    
    
        ser.write(msg)
        time.sleep(0.1)
    
        out = ''
        while ser.inWaiting() > 0:
            out += ser.read(1)
        if (out == ''): continue
        
    
        #The following states are true if the value is [1], otherwise [0]:
        status = ""
        if (ord(out[3]) & 1): status += " IDLING " 		 #Acceptor is idling (waiting)
        if (ord(out[3]) & 2): status += " ACCEPTING "  	 #Acceptor pulling in new bill
        if (ord(out[3]) & 4):
            status += " ESCROWED "				         #Bill is stopped in escrow
            escrowed = True
        else:
            escrowed = False
            
        if (ord(out[3]) & 8): status += " STACKING "	 #Valid bill feeding into cassette (or to rear for stackerless)
        if (ord(out[3]) & 0x10): status += " STACKED "	 #Valid bill now in cassette (or cleared back of unit for stackerless)
        if (ord(out[3]) & 0x20): status += " RETURNING " #Bill is being returned to the user
        if (ord(out[3]) & 0x40): status += " RETURNED "	 #Bill has finished being returned to the user
            
        if (ord(out[4]) & 1): status += " CHEATED "	 	 #Acceptor suspects cheating
        if (ord(out[4]) & 2): status += " REJECTED "	 #Bill was rejected
        if (ord(out[4]) & 4): status += " JAMMED "		 #Bill is jammed in Acceptor
        if (ord(out[4]) & 8): status += " FULL "		 #Cassette is full (must be emptied)
        if (ord(out[4]) & 0x10) != 0x10: status += " CASSETTE MISSING"
            
        # Only update the status if it has changed
        if (lastState != status):
            print 'Acceptor status:',status
            lastState = status

        print ", ".join("0x{:02x}".format(ord(c)) for c in out)
        
        # Print credit(s)  
        credit = ord(out[5]) & 0x38
        if(credit == 0): credit = 0
        if(credit == 8): credit = 1
        if(credit == 0x10): credit = 2
        if(credit == 0x18): credit = 3
        if(credit == 0x20): credit = 4
        if(credit == 0x28): credit = 5
        if(credit == 0x30): credit = 6
        if(credit == 0x38): credit = 7
            
        if(credit != 0):
            if(ord(out[3]) & 0x10):
                print "Bill credited: Bill#", credit
                billCount[credit] += 1
                print "Acceptor now holds:",binascii.hexlify(billCount)
                
        time.sleep(PollRate)    
        
    print "port closed"
    ser.close()        
    
if __name__ == "__main__":
    main(sys.argv[1])