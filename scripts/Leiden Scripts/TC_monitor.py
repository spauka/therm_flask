import os, os.path
import sys
import re
import time, datetime
import csv, json
import urllib.request, urllib.error

PATH = "C:\\avs-47\\"
PATTERN = r'LogAVS_Reilly-DR__([0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{2}-[0-9]{2}-[0-9]{2})\.dat'
FRIDGE = 'Big_Fridge'

def find_newest():
    newest = datetime.datetime.min
    newest_file = ""
    # Look through all the files in the path
    for filename in os.listdir(PATH):
        match = re.findall(PATTERN, filename)
        if not match:
            continue
        date = match[0]
        date = datetime.datetime.strptime(date, "%Y-%m-%d-%H-%M-%S")

        if date > newest:
            newest_file = filename
            newest = date

    return newest_file

def parse_file(filename, seek=0, oldest=datetime.datetime.min):
    path = os.path.join(PATH, filename)
    fhandle = open(path, 'rU')

    if not seek:
        # trash first 6 lines of log file, these are headers
        for i in range(6):
            fhandle.readline()
    else:
        fhandle.seek(seek)

    while True:
        line = fhandle.readline()
        iseof = (fhandle.tell() == os.fstat(fhandle.fileno()).st_size)
        if not line:
            return (None, fhandle.tell(), iseof)

        data = line.split('\t')

        date = datetime.datetime.strptime(data[0], "%Y-%m-%d %H:%M:%S")
        if date < oldest:
            continue
        else:
            data = {'Time': date,
                    'Four_K_RuO': float(data[10]),
                    'Still_RuO': float(data[11]),
                    'Fifty_mK_RuO': float(data[12]),
                    'MC_CMN': float(data[13]),
                    'MC_PT': float(data[14])}
            for key in data.keys():
                if key == 'Time':
                    continue
                if data[key] > 400000 or data[key] < 0:
                    data[key] = float('NaN')
            return (data, fhandle.tell(), iseof)

def find_oldest():
    URL = 'http://www.physics.usyd.edu.au/~spauka/therm_flask/%s/data/?current' % FRIDGE
    line = urllib.request.urlopen(URL).read().decode('utf-8')
    line = json.loads(line)
    if "Time" not in line:
        return datetime.datetime.min
    else:
        date = datetime.datetime.strptime(line["Time"], "%a %b %d %H:%M:%S %Y")
        print(date)
        return date

def post(data):
    URL = 'http://www.physics.usyd.edu.au/~spauka/therm_flask/%s/data/' % FRIDGE
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
            continue

if __name__ == '__main__':
    if len(sys.argv) == 2:
        if sys.argv[1] in ('--help', '-h'):
            print("Usage: %s [--parse-all]")
            exit(0)
        if sys.argv[1] == '--parse-all':
            #oldest = find_oldest()
            oldest = datetime.datetime(2013, 7, 19, 15, 50, 34)
            print("Parsing all data from date %r" % oldest)
            for filename in os.listdir(PATH):
                if re.findall(PATTERN, filename):
                    print("Parsing file: %s" % filename)
                    seek = 0
                    eof = False
                    while not eof:
                        data, seek, eof = parse_file(filename, seek=seek, oldest=oldest)
                        if seek == 0:
                            post({'Time': data['Time']-datetime.timedelta(0, 1)})
                        print('%r, %s' % (data['Time'], post(data)))
            print('Done')
            exit(0)

    oldest = find_oldest()
    cfile = find_newest()
    seek = 0
    while True:
        filename = find_newest()
        if filename != cfile:
            seek = 0
            cfile = filename

        eof = False
        while not eof:
            data, seek, eof = parse_file(cfile, seek=seek, oldest=oldest)
            if data:
                oldest = data['Time']
                post(data)

        time.sleep(1)

