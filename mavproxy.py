#!/bin/python
#coding=UTF-8

"""
    MavProxy (c) Janne Mäntyharju
    
    This script is used to forward MavLink messages from Ardupilot Mega to the Internet as UDP
    packet and vice versa.
"""

import sys
import urllib2
import ConfigParser
import socket
import time
import fcntl
import struct
import serial

import mavlink

INTERFACE = "wlan0"
SERIAL_PORT = "/dev/ttyO2"
SERIAL_BAUD = 38400

class config:
    def __init__(self,address):
        self.address = address
        self.address = None
        self.port = 0
        
    def update(self):
        try:
            confFile = urllib2.urlopen(sys.argv[1])
        except:
            print "Configuration could not be downloaded"
            return False
            
        conf = ConfigParser.SafeConfigParser()
        conf.readfp(confFile)
        confFile.close()
        
        self.address = conf.get("host", "address")
        self.port = int(conf.get("host", "port"))
        
        return True

def get_ip(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])
    
def main(argv):
    if len(argv) < 2:
        print "Usage: " + argv[0] + " <url address of config file>"
        return 1
    
    conf = config(argv[1])
    mav_upstream = mavlink.MAVLink(None) # parses messages from APM
    mav_downstream = mavlink.MAVLink(None) # parses messages from Mission planner
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setblocking(0)
    try:
        own_ip = get_ip(INTERFACE)
    except:
        print "Interface {0} is not up".format(INTERFACE)
        return 1
    
    sock.bind((own_ip,conf.port))
    
    settings_timer = 0
    ip_timer = 0
    
    ser = serial.Serial(SERIAL_PORT, SERIAL_BAUD, timeout = 0)
    
    while (True):
        # Update settings every 5 mins
        if (time.time() > settings_timer + (5 * 60)):
            settings_timer = time.time()
            conf.update()
        
        # Send own ip every 1 min
        if (time.time() > ip_timer + (1 * 60)):
            ip_timer = time.time()
            print "Connect to", conf.address, conf.port
            msg = mav_upstream.statustext_encode(0, "IP: " + get_ip(INTERFACE))  
            sock.sendto(msg.get_msgbuf(), (conf.address, conf.port))
            
        # Receive data from serial and send forward
        try:
            msg = mav_upstream.parse_char(ser.read(1))
            sock.sendto(msg.get_msgbuf(), (conf.address, conf.port))
            print "Got package from APM: ", str(msg)
        except:
            pass        
        
        # Receive data and push to serial  
        buf=""
        try:
            buf = sock.recv(4096)
        except:
            pass
             
        if len(buf) > 0:
            for c in buf:
                try:
                    msg = mav_downstream.parse_char(c)
                except:
                    pass
                if msg != None:
                    ser.write(msg.get_msgbuf())
                    print "Got package from NET: ", str(msg)    
    
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))