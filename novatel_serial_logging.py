import os
import serial
import argparse
import datetime
import time
import threading
import logging


SUPPORTED_BAUD = [2400, 4800, 9600, 19200, 38400, 57600, 115200, 230400, 460800]

DEFAULT_LOGLIST =[
    'LOG VERSIONB ONCE',
    'LOG RXCONFIGB ONCE',
    'LOG RXSTATUSB ONCHANGED',
    'LOG RANGEB ONTIME 1',
    'LOG RAWEPHEMB ONNEW',
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

INS_CONFIG = [
    'connectimu {} {}',
    'setinsrotation RBV {} {} {} 3 3 3',
    'setinstranslation ANT1 {} {} {} 0.05 0.05 0.05']

def establish_serial_connection(port,baudrate):
    serialport = serial.Serial(port=port)
    serialport.timeout = 5
    serialport.send_break()
    time.sleep(2)
    serialport.send_break()
    time.sleep(2)
    # loop through supported baud rate
    for baud in SUPPORTED_BAUD:
        logging.info('connecting at {}...'.format(baud))
        serialport.baudrate = baud
        # send command to change baud rate
        time.sleep(0.2)
        serialport.flushInput()
        serialport.write('serialconfig {}\r'.format(baudrate).encode())
        time.sleep(0.2)
        # check for response
        if b'<OK' in serialport.read(10):
            logging.info('baud rate changed to {}'.format(baudrate))
            serialport.timeout = None
            PORT_FOUND = True
            break
    
    if PORT_FOUND == False:
        raise ValueError('Serial communication not established.')
    return serialport

def read_from_serial(port, filename):
    outputFile = open(filename,'wb')
    incomingData = bytearray()
    logging.info('start reading from port...')
    try:
        while READ:
            if port.inWaiting():
                incomingData = port.read(port.inWaiting())
                if len(incomingData) > 0:
                    logging.debug(incomingData)
                    outputFile.write(incomingData)
                    outputFile.flush()
                    incomingData = bytearray()
            else:
                time.sleep(0.1)
    except KeyboardInterrupt:
        # TODO::this can be changed to detect serial port exception in the future
        logging.info('KeyboardInterrupt captured in read thread')
    outputFile.close()
    logging.info('END OF READ THREAD.')

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
                        help='specify the IMU connected to receiver')
    parser.add_argument('-ip',
                        required=False,
                        metavar='COM2',
                        type=str,
                        help='port used for IMU connection [COM1,COM2,COM3,COM4,SPI]')
    parser.add_argument('-la',
                        required=False,
                        metavar=('X','Y','Z'),
                        nargs=3,
                        type=float,
                        help='lever arm from IMU Center of Navigation to antenna')
    parser.add_argument('-rbv',
                        required=False,
                        metavar=('X','Y','Z'),
                        nargs=3,
                        type=float,
                        help='rotation from IMU body to vehicle frame')
    return parser.parse_args()

def main():
    global READ
    global PORT_FOUND
    logging.getLogger().setLevel(logging.INFO)

    READ = True
    PORT_FOUND = False
    args = parse_arguments()
    comport = establish_serial_connection(port=args.c.upper(), baudrate=args.b)

    # start read on a separate thread, and write to file continuously
    readthread = threading.Thread(target=read_from_serial, args=(comport,os.path.join(os.getcwd(),args.f),))
    readthread.start()

    # configure INS
    if args.i:
        if not args.ip or not args.la or not args.rbv:
            raise ValueError('Missing Input for Configuring INS: ip/LA/RBV')
        else:
            # TODO::better code can be written but this works for now
            comport.write((INS_CONFIG[0] + '\r').format(args.ip,args.i).encode())
            logging.info('sending '+ INS_CONFIG[0].format(args.ip,args.i))
            comport.write((INS_CONFIG[1] + '\r').format(args.rbv[0],args.rbv[1],args.rbv[2]).encode())
            logging.info('sending '+ INS_CONFIG[1].format(args.rbv[0],args.rbv[1],args.rbv[2]))
            comport.write((INS_CONFIG[2] + '\r').format(args.la[0],args.la[1],args.la[2]).encode())
            logging.info('sending '+ INS_CONFIG[2].format(args.la[0],args.la[1],args.la[2]))
            
    # send default SPAN logging profile 
    for log in DEFAULT_LOGLIST:
        logging.info('sending {}...'.format(log))
        comport.write((log + '\r').encode())
        time.sleep(0.1)

    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        READ = False
        logging.info('Program terminated.')


if __name__ == "__main__":
    main()
 