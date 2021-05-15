import os
import serial
import argparse
import datetime
import time
import threading
import logging

# test comment

SUPPORTED_BAUD = [2400, 4800, 9600, 19200, 38400, 57600, 115200, 230400, 460800]

DEFAULT_LOGLIST =[
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

def establish_serial_connection(port,baudrate):
    serialport = serial.Serial(port=port)
    serialport.open()
    serialport.send_break()
    time.sleep(0.2)
    serialport.send_break()
    # loop through supported baud rate
    for baud in SUPPORTED_BAUD:
        logging.info('connecting at {}...'.format(baud))
        serialport.baudrate = baud
        # send command to change baud rate
        time.sleep(0.2)
        serialport.write('serialconfig {}\r'.format(baudrate).encode())
        # check for response
        if b'<OK' in serialport.read(10):
            logging.info('baud rate changed to {}'.format(baudrate))
            break

    return serialport

def read_from_serial(port, filename):
    outputFile = open(filename,'wb')
    incomingData = bytearray()
    try:
        while True:
            if port.inWaiting():
                incomingData = port.read(port.inWaiting())
                if len(incomingData) > 0:
                    outputFile.write(incomingData)
                    outputFile.flush()
                    incomingData = bytearray()
            else:
                time.sleep(0.1)
    except KeyboardInterrupt:
        if len(incomingData) > 0:
            outputFile.write(incomingData)
            outputFile.flush()
        outputFile.close()

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
                        required=False,
                        metavar='filename',
                        default=datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S') + '.log',
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
    comport = serial.Serial()
    comport.port = args.c
    comport.baudrate = args.b
    comport.bytesize = 8
    comport.timeout=None
    comport.parity =None
    comport.stopbits=1
    comport.open()
    comport = establish_serial_connection(port=args.c.upper(), baudrate=args.b)

    # start read on a separate thread, and write to file continuously
    readthread = threading.Thread(target=read_from_serial, args=(comport,os.path.join(os.getcwd(),args.f),))
    readthread.start()

    # send default SPAN logging profile 
    for log in DEFAULT_LOGLIST:
        logging.info('sending {}...'.format(log))
        comport.write((log + '\r').encode())
        time.sleep(0.1)
    
    # TODO:: configure INS


    readthread.join()


if __name__ == "__main__":
    main()
 