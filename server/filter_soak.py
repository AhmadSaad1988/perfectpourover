from StringIO import StringIO
import serial
import time
ser = serial.Serial('/dev/tty.usbmodem621', 9600)
time.sleep(2)

buf = StringIO()

brew_temp = '200';

if True:

	# POUR 1
	buf.write('LINEAR\n')
	buf.write('0.0\n') # Theta Initial
	buf.write('75\n') # Theta Rate
	buf.write('0.0\n') # Radius Initial
	buf.write('.01\n') # Radius Rate
	buf.write('20\n') # Radius Scale
	buf.write('9\n') # Time
	buf.write('220\n') # Pump
	buf.write(brew_temp + '\n') # Temp

	# WAIT
	buf.write('LINEAR\n')
	buf.write('0.0\n') # Theta Initial
	buf.write('0\n') # Theta Rate
	buf.write('0.0\n') # Radius Initial
	buf.write('.00\n') # Radius Rate
	buf.write('20\n') # Radius Scale
	buf.write('40\n') # Time
	buf.write('0\n') # Pump
	buf.write(brew_temp + '\n') # Temp


	buf.write('END\n')

	n = ser.write(buf.getvalue())
	if n != len(buf.getvalue()):
	    ser.write(buf.getvalue()[n:])

	ser.flush()
	buf = StringIO()

while True:
    c = ser.read()
    if (c == '\n'):
        print buf.getvalue()
        buf = StringIO()
    else:
    	buf.write(c)
