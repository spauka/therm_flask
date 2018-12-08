import os, os.path
import sys
import re
import time, datetime
import csv, json
import urllib.request, urllib.error
import serial

FRIDGE = 'Big_Fridge'
SUPPL = 'PV'
SERIAL = "COM35" #NEED TO CHANGE THIS



class PV(object):
    def __init__(self, port=SERIAL): #giving the front panel a serial port 
        self.c = serial.Serial(port, baudrate=9600, timeout=1)

    def query(self, query): #this is the query function
    	# Check that there are no weird characters in the query
        # Write the query to the serial port
        self.c.write(query.encode())
        returnval = self.c.readline() #this check that the maxigauge is acknowledging the signal
        #now it should return 5 if it has successfully received the ENQ, and 21 if it doesn't work
        if returnval[0] != 6:
            raise SystemError("Maxigauge does not acknowledge your request")
        # Read a line from the serial port (result of the query)
        self.c.write(bytes([5])) #5 is the signal that the Maxigauge interprets as ENQ - enquiry - yes, I do want to know the answer to the question I just asked you
        #maxigauage will then send back signal and you can read this out
        result = self.c.readline()
        result = result.decode()
        result = result.strip()
        result = result.split(",")
        return result


    def pressures(self):
    	# Query the maxigauge's pressures for each channel and records it
        Pressure = []
        for i in range(6):
            result = self.query("PR%d\r\n" % (i+1)) #gets the pressures from all the channels
            result = result[1]
            Pressure.append(result)
        return Pressure

# Post the data to the website
def post(data):
    URL = 'http://www.physics.usyd.edu.au/~spauka/therm_flask/%s/%s/' % (FRIDGE,SUPPL)
    data['Time'] = data['Time'].timestamp()
    print("Updating at %r" % (data['Time'],))
    while True:
        try:
            request = urllib.request.urlopen(URL, urllib.parse.urlencode(data).encode('utf-8'))
            response = request.read().decode('utf-8')
            request.close()
            return response
        except urllib.error.URLError:
            print("URLOpen Error")
            time.sleep(0.1)
            continue

if __name__ == '__main__':
    interval = 10

    if len(sys.argv) >= 2:
        if sys.argv[1] in ('--help', '-h'):
            print("Usage: %s [-i/--interval=N]")
            exit(0)
        if re.match("(--interval|-i)", sys.argv[1]):
            interval = re.findall("(--interval|-i)=?([0-9]+)", sys.argv[1])
            if interval:
                interval = int(interval[1])
            else:
                interval = int(sys.argv[2])

    post({'Time': datetime.datetime.now() - datetime.timedelta(0, 1)})
    # Create an instance of the front panel, i.e. connect to the front panel
    gauge = PV()
    
    while True:
        try:
            # Read pressures from the front panel
            pressures = gauge.pressures()
        except SystemError:
            print("Failed to read values from GHS")
            continue
        data = {'Time': datetime.datetime.now(),
                'OVC': pressures[2],
                'IVC': pressures[3],
                'PROBE': pressures[5],
                'STILL': pressures[4]}
        print(post(data))

        time.sleep(interval)
