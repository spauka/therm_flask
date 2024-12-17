import os, os.path
import sys
import re
import time, datetime
import csv, json
import urllib.request, urllib.error

PATH = "C:\\BlueFors logs"
FOLDER_PATTERN = r"([0-9]{2})-([0-9]{2})-([0-9]{2})"
FRIDGE = 'BlueFors_QT1'
SUPPL = 'MaxiGauge'

def find_oldest():
    URL = 'https://qphys1114.research.ext.sydney.edu.au/therm_flask/%s/%s/?current' % (FRIDGE,SUPPL)
    try:
        line = urllib.request.urlopen(URL).read().decode('utf-8')
    except urllib.error.HTTPError:
        return datetime.datetime.min
    if line != "No data returned":
        print(line)
        line = json.loads(line)
    else:
        return datetime.datetime.min
    if "Time" not in line:
        return datetime.datetime.min
    else:
        date = datetime.datetime.strptime(line["Time"], "%a %b %d %H:%M:%S %Y")
        print(date)
        return date
    
# Finds the latest folder
def find_newest_folder():
    newest = (0,0,0) # y, m, d
    newest_folder = ""
    # Look through all the folders in the path and find the newest
    for filename in os.listdir(PATH):
        match = re.findall(FOLDER_PATTERN, filename)
        if not match:
            continue
        date = tuple(int(x) for x in match[0])
        if date > newest:
            newest_folder = filename
            newest = date

    return newest_folder

def parse_file(foldername, seek=0, oldest=datetime.datetime.min):
    path = os.path.join(PATH, foldername, "maxigauge %s.log"%(foldername))
    try:
        fhandle = open(path, 'rU')
    except FileNotFoundError:
        return (None, 0, True)

    if seek:
        fhandle.seek(seek)

    while True:
        line = fhandle.readline()
        iseof = (fhandle.tell() == os.fstat(fhandle.fileno()).st_size)
        if not line:
            return (None, fhandle.tell(), iseof)

        data = line.strip().split(',')

        date = datetime.datetime.strptime(data[0] + " " + data[1], "%d-%m-%y %H:%M:%S")
        if date < oldest:
            continue
        else:
            data = {'Time': date,
                    'VC': float(data[5]) if int(data[4]) else float('NaN'),
                    'PStill': float(data[11]) if int(data[10]) else float('NaN'),
                    'Condensing': float(data[17]) if int(data[16]) else float('NaN'),
                    'Backing': float(data[23]) if int(data[22]) else float('NaN'),
                    'Tank': float(data[29]) if int(data[28]) else float('NaN'),
                    'AirBacking': float(data[35]) if int(data[34]) else float('NaN')}
            for key in data.keys():
                if key == 'Time':
                    continue
                if not data[key] or data[key] <= 0:
                    data[key] = float('NaN')
            return (data, fhandle.tell(), iseof)
        
def post(data):
    URL = 'https://qphys1114.research.ext.sydney.edu.au/therm_flask/%s/%s/' % (FRIDGE,SUPPL)
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
    if len(sys.argv) == 2:
        if sys.argv[1] in ('--help', '-h'):
            print("Usage: %s [--parse-all]")
            exit(0)
        if sys.argv[1] == '--parse-all':
            oldest = find_oldest()
            print("Parsing all data from date %r" % oldest)
            for filename in os.listdir(PATH):
                if re.findall(FOLDER_PATTERN, filename):
                    print("Parsing file: %s" % filename)
                    seek = None
                    eof = False
                    while not eof:
                        data, seek, eof = parse_file(filename, seek=seek, oldest=oldest)
                        if data and seek == 0:
                            print(post({'Time': data['Time']-datetime.timedelta(0, 1)}))
                        if data:
                            print('%r, %s' % (data['Time'], post(data)))
            print('Done')
            exit(0)

    oldest = find_oldest()
    cfile = find_newest_folder()
    seek = None
    # Post a blank
    print(post({'Time': oldest}))
    while True:
        time.sleep(1)
        filename = find_newest_folder()
        if filename != cfile:
            seek = None
            cfile = filename
            print("Starting new folder: %s", filename)

        eof = False
        while not eof:
            data, seek, eof = parse_file(cfile, seek=seek, oldest=oldest)
            if data:
                oldest = data['Time']
                print(post(data))


