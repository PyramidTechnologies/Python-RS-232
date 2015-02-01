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
' code if any or all of PTI's source code is integrated into the user's
'   application.
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

import host
import sys


### Main  Routine ###
def main(portname):
    """
    Starts the Master RS-232 service
    """

    cmd_table = '''

    H or ? to show Help
    Q or CTRL+C to Quit

    V - Enable Verbose mode
    '''

    print "Starting RS-232 Master on port {:s}".format(portname)
    master = host.Host()
    master.start(portname)


    # Loop until we are to exit
    try:
        print cmd_table
        while master.running:

            cmd = raw_input()
            result = master.parse_cmd(cmd)
            if result is 0:
                pass
            elif result is 1:
                master.stop()
            elif result is 2:
                print cmd_table

    except KeyboardInterrupt:
        master.running = False

    print '\n\nGoodbye!'
    print 'Port {:s} closed'.format(portname)


if __name__ == "__main__":
    main(sys.argv[1])
