import serial
from serial.tools import list_ports
import argparse
import time
import threading
import logging

LOGLIST =[
    'LOG VERSIONB ONCE',
    'LOG RXCONFIGB ONCE',
    'LOG RXSTATUSB ONCHANGED',
    'LOG RANGEB ONTIME 1',
    'LOG GPSEPHEMB ONNEW',
    'LOG GLOEPHEMERISB ONNEW',
    'LOG GALFNAVEPHEMERISB ONNEW',
    'LOG GALINAVEPHEMERISB ONNEW',
    'LOG BDSEPHEMERISB ONNEW',
    'LOG QZSSEPHEMERISB ONNEW',
    'LOG NAVICEPHEMERISB ONNEW',
    'LOG BESTGNSSPOSB ONTIME 1',
    'LOG BESTPOSB ONTIME 1',
    'LOG HEADING2B ONNEW',
    'LOG RAWIMUSXB ONNEW',
    'LOG INSPVAXB ONTIME 1',
    'LOG INSCONFIGB ONCHANGED',
    'LOG INSUPDATESTATUSB ONNEW']

def establish_serial_connection(serialport,baudrate):
    # add additional error handling for external use
    # TODO: fix this port check
    if serialport not in list_ports.comports():
        raise ValueError('serial port {} does not exist'.format(serialport))
    if type(baudrate) != int:
        raise TypeError('baud rate must be integer')

def read_from_serial():
    pass

def configure_logging_profile(serialport,baudrate):
    pass

def parse_arguments():
    parser = argparse.ArgumentParser(description='NovAtel Receiver Data Logging')
    parser.add_argument('-c',
                        required=True,
                        metavar='COM24',
                        type=str,
                        help='Computer COM port of NovAtel Receiver connected')
    parser.add_argument('-f',
                        required=True,
                        metavar='filename',
                        type=str,
                        help='filename for logging to be saved')
    parser.add_argument('-b',
                        required=False,
                        metavar=460800,
                        default=460800,
                        choices=[9600,115200,230400,460800],
                        type=int,
                        help='baud rate for serial connection [9600, 115200, 230400, 460800(default)]')
    parser.add_argument('-i',
                        required=False,
                        metavar='EPSON_G320',
                        type=str,
                        help='placeholder for specifying the IMU connected to receiver')
    parser.add_argument('-ip',
                        required=False,
                        metavar='COM2',
                        type=str,
                        help='placeholder for specifying port used for IMU connection [COM1,COM2,COM3,COM4,SPI]')
    parser.add_argument('-la',
                        required=False,
                        metavar=('X','Y','Z'),
                        nargs=3,
                        type=float,
                        help='placeholder for configuring lever arm from IMU Center of Navigation to antenna')
    parser.add_argument('-rbv',
                        required=False,
                        metavar=('X','Y','Z'),
                        nargs=3,
                        type=float,
                        help='placeholder for configuring rotation from IMU body to vehicle frame')
    return parser.parse_args()

def main():
    args = parse_arguments()
    print(type(args.c),args.c)
    print(type(args.f),args.f)
    print(type(args.b),args.b)
    print(type(460800),type(460800)==int)
    print(LOGLIST)
    
    # establish connection
    comport = serial.Serial()
    comport.port = args.c
    comport.baudrate = args.b
    comport.timeout=None
    comport.parity='N'
    comport.stopbits=1
    comport.bytesize=8
    
    # TODO::break current logging and force find COM port at specified baudrate

    # TODO::start read on a separate thread, and write to file continuously
    

    # sending standard SPAN logging profile 
    for log in LOGLIST:
        comport.write((log + '\r').encode())
        time.sleep(0.2)
    
    # read from serial and write to file
    outputFile = open(args.f,'wb')
    incomingData = bytearray()
    try:
        while True:
            if comport.inWaiting():
                incomingData = comport.read(comport.inWaiting())
                if len(incomingData) > 0:
                    outputFile.write(incomingData)
                    incomingData = bytearray()
            else:
                time.sleep(0.1)
    except KeyboardInterrupt:
        outputFile.close()



    


if __name__ == "__main__":
    main()
 