from StringIO import StringIO
import serial
import time
ser = serial.Serial('/dev/tty.usbmodem621', 9600)
time.sleep(2)

buf = StringIO()

#"{\"Name\":\"Blanchon\",\"Skills\":[\"C\",\"C++\",\"C#\"],\"Age\":32,\"Online\":true}";

buf.write("{")
buf.write("\"Command\":\"SEQUENCE\",")
buf.write("\"Length\":4,")
buf.write("\"ThetaInit\":[\"15.5\", \"30.0\", \"30.0\", \"30.0\"],")
buf.write("\"ThetaRate\":[\"1.2\", \"3.2\", \"3.2\", \"3.2\"],")
buf.write("\"RadiusInit\":[\"5\", \"6\", \"6\", \"6\"],")
buf.write("\"RadiusRate\":[\"1.2\", \"3.2\", \"3.2\", \"3.2\"],")
buf.write("\"RadiusScale\":[\"1.2\", \"3.2\", \"3.2\", \"3.2\"],")
buf.write("\"Time\":[\"10\", \"5\", \"5\", \"5\"],")
buf.write("\"Pump\":[\"1\", \"0\", \"0\", \"0\"],")
#buf.write("\"Temp\":[\"68\", \"68\"]")
buf.write("}\n")

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
