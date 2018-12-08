import os, os.path
import sys
import re
import time, datetime
import csv, json
import urllib.request, urllib.error, http.client
import serial

FRIDGE = 'Red_Fridge'
SUPPL = 'FP'
SERIAL = "COM15"

def find_oldest():
    URL = 'http://www.physics.usyd.edu.au/~spauka/therm_flask/%s/%s/?current' % (FRIDGE,SUPPL)
    line = urllib.request.urlopen(URL).read().decode('utf-8')
    line = json.loads(line)
    if "Time" not in line:
        return datetime.datetime.min
    else:
        date = datetime.datetime.strptime(line["Time"], "%a %b %d %H:%M:%S %Y")
        print(date)
        return date

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
        except (urllib.error.URLError, http.client.BadStatusLine):
            print("URLOpen Error")
            time.sleep(0.1)
            continue

class FP(object):
    def __init__(self, port=SERIAL):
        self.serial = serial.Serial(port, baudrate=9600, timeout=1)
        self.id = self.query("ID?\n")
        if self.id[0] != '0' or len(self.id) != 2:
            raise ValueError("Invalid id for GHS: %r" % (self.id))
        if not re.match("GHS", self.id[1]):
            raise ValueError("Invalid id for GHS: %s" % (self.id[1]))
        self.id = self.id[1].strip()
        print("Connected to GHS: %s" % self.id)

    def query(self, query):
        if not re.match("^[a-zA-Z:]+\?\n$", query):
            raise ValueError("Invalid Query Format")
        self.serial.write(query.encode())
        result = self.serial.readline().decode()
        result = result.strip().split('\t')
        return result

    def adc(self):
        result = self.query("ADC?\n")
        if result[0] == '0':
            values = [int(x) for x in result[1].split(',')]
            pressures = tuple(x*2500.0/4095.0 for x in values[:7])
            flow = (0.061*values[7],)
            return pressures+flow
        else:
            raise SystemError("Error querying ADC Values")

    def avg_adc(self):
        adc = [0,0,0,0,0,0,0,0]
        for i in range(5):
            adc = [x + y for (x,y) in zip(adc, self.adc())]
            time.sleep(0.75)
        adc = [x/5 for x in adc]
        return adc

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

    oldest = find_oldest()
    post({'Time': oldest + datetime.timedelta(0, 1)})
    panel = FP()
    
    while True:
        try:
            adc = panel.avg_adc()
        except SystemError:
            print("Failed to read values from GHS")
            continue
        data = {'Time': datetime.datetime.now(),
                'PProbe': adc[0],
                'POVC': adc[1],
                'PIVC': adc[2],
                'P4': adc[3],
                'P5': adc[4],
                'Dump4': adc[5],
                'Dump3': adc[6],
                'Flow': adc[7]}
        print(post(data))

        time.sleep(interval)
