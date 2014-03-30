from StringIO import StringIO
import serial
import time
ser = serial.Serial('/dev/tty.usbmodem621', 9600)
time.sleep(2)

buf = StringIO()

if False:


	buf.write('LINEAR\n')
	buf.write('0.0\n')
	buf.write('10\n')
	buf.write('0.0\n')
	buf.write('.01\n')
	buf.write('20\n')
	buf.write('50\n')
	buf.write('67\n')
	buf.write('END POUR\n')
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
