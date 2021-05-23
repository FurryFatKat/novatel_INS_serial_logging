# serial_logging_for_novatel_equipment

Note: 
- This script has only been tested with Python 3.7 and it should work with Python 3.7+
- All libraries used are native to Python 3.7+
- This script does not check if the IMU enum entered is supported yet. More to come.

By default, this script will:
- log data to file (<current_datetime>.log if no filename is given)
- request a list of recommended for OEM7 SPAN Data Collection found: https://docs.novatel.com/Waypoint/Content/AppNotes/SPAN_Data_Recommendations.htm

Optionally, use [-i] [-ip] [-la] [-rbv] switches together for configuring INS connected to the OEM7 receiver. For RBV rotation, 3 degrees of standard deviation will be used. For primary lever arm, 5 cm of standard deviation will be used. All four arguments required for configuring INS.



To run this script and see help menu in Linux/Windows:
- Windows Command Prompt: $ python novatel_serial_logging.py -h
- Linux Terminal:         $ python3 novatel_serial_logging.py -h

usage: novatel_serial_logging.py [-h] -c COM24 [-f filename] [-b 460800]
                                 [-i EPSON_G320] [-ip COM2] [-la X Y Z]
                                 [-rbv X Y Z]
  
Example:
- OEM7 NovAtel Receiver connected to computer on COM27. Receiver COM2 is connected to Litef_microIMU. Lever arm from IMU Center of Navigation to Antenna Phase Center is 1, 2, 3 for X, Y, Z axis respectively in IMU Body Frame. Rotation from IMU Body Frame to Vehicle Frame is 0, 90, 0 for X, Y, Z axis respectively.
  - python novatel_serial_logging.py -c COM27 -i LITEF_MICROIMU -ip COM2 -la 1 2 3 -rbv 0 90 0
- OEM7 NovAtel Receiver connected to computer on COM27. No IMU used.
  - python novatel_serial_logging.py -c COM27
