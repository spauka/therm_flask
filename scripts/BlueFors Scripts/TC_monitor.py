import os, os.path
import sys
import re
import time, datetime
import csv, json
import urllib.request, urllib.error

PATH = "C:\\BlueFors logs"
FOLDER_PATTERN = r"([0-9]{2})-([0-9]{2})-([0-9]{2})"
FRIDGE = 'BlueFors_QT1'
SENSORS = ((1, "Fifty_K"),
           (2, "Four_K"),
           (3, "Magnet"),
           (5, "Still"),
           (6, "MC"),
           (9, "Probe"))

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
    
# Parse the file and returns the next set of sensor values
# Select time from the last sensor read (Normally MC)
def parse_file(folder, channels, seek=None, oldest=datetime.datetime.min):
    ch1 = channels[-1][0] # get the number of the last valid channel
    path = os.path.join(PATH, folder, "CH%d T %s.log"%(ch1, folder))
    try:
        fhandle = open(path, 'rU')
    except FileNotFoundError:
        return (None, seek, True)
    if seek:
        fhandle.seek(seek[-1]) # Seek the first channel
    else:
        seek = [0]*len(channels) # Initialize list with [channels] zeros
    while True:
        line = fhandle.readline().strip() # Read the next line of the last channel file
        iseof = (fhandle.tell() == os.fstat(fhandle.fileno()).st_size)
        if not line:
            return (None, seek, iseof)

        data = line.split(',')

        # Read out the next date
        try:
            date = datetime.datetime.strptime(data[0]+" "+data[1], "%d-%m-%y %H:%M:%S")
        except (IndexError, ValueError):
            # Couldn't extract time, skip line
            return (None, seek, iseof)
        if date < oldest:
            continue
        else:
            # Read in all the previous sensors
            data = {'Time': date}
            for i, channel in enumerate(channels):
                try:
                    s_path = os.path.join(PATH, folder, "CH%d T %s.log"%(channel[0], folder))
                    s_fhandle = open(s_path, 'rU')
                    s_fhandle.seek(seek[i])
                    line = s_fhandle.readline().strip(' \n\r\x00')
                    seek[i] = s_fhandle.tell()
                    line = line.split(",")
                    if line and len(line) == 3:
                        s_date = datetime.datetime.strptime(line[0]+" "+line[1], "%d-%m-%y %H:%M:%S")
                        temp = float(line[2])
                        # Check that the time is not too far in the past, if it is try to fast forward
                        s_eof = False
                        while date - s_date > datetime.timedelta(seconds=90):
                            line = s_fhandle.readline().strip()
                            seek[i] = s_fhandle.tell()
                            line = line.split(",")
                            if line and len(line) == 3:
                                s_date = datetime.datetime.strptime(line[0]+" "+line[1], "%d-%m-%y %H:%M:%S")
                                temp = float(line[2])
                            else:
                                # If we hit the end of the file and we are still in the past, move to the next sensor
                                s_eof = True
                                break
                        if s_eof:
                            # We hit the end of the file in the past. Move on to next sensor.
                            print("Skipping sensor: %s"%(channel[1]))
                            continue
                        # Check that this record is not more than 1.5 minutes out from the first one
                        if abs(s_date - date) > datetime.timedelta(seconds=90): 
                            data[channels[i][1]] = float('NaN')
                        elif temp > 400000 or temp <= 0:
                            data[channels[i][1]] = float('NaN')
                        else:
                            data[channels[i][1]] = float(line[2])
                    else:
                        data[channels[i][1]] = float('NaN')
                except FileNotFoundError:
                    data[channels[i][1]] = float('NaN')
            return (data, seek, iseof)

def find_oldest():
    URL = 'https://qphys1114.research.ext.sydney.edu.au/therm_flask/%s/data/?current' % FRIDGE
    try:
        line = urllib.request.urlopen(URL).read().decode('utf-8')
    except urllib.error.HTTPError:
        return datetime.datetime.min
    line = json.loads(line)
    if "Time" not in line:
        return datetime.datetime.min
    else:
        date = datetime.datetime.strptime(line["Time"], "%a %b %d %H:%M:%S %Y")
        print(date)
        return date

def post(data):
    URL = 'https://qphys1114.research.ext.sydney.edu.au/therm_flask/%s/data/' % FRIDGE
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
            oldest = find_oldest()
            print("Parsing all data from date %r" % oldest)
            for filename in os.listdir(PATH):
                if re.findall(FOLDER_PATTERN, filename):
                    print("Parsing file: %s" % filename)
                    seek = None
                    eof = False
                    while not eof:
                        data, seek, eof = parse_file(filename, SENSORS, seek=seek, oldest=oldest)
                        if seek == 0:
                            print(post({'Time': data['Time']-datetime.timedelta(0, 1)}))
                        if data:
                            print('%r, %s' % (data['Time'], post(data)))
            print('Done')
            #time.sleep(10)
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
            data, seek, eof = parse_file(cfile, SENSORS, seek=seek, oldest=oldest)
            if data:
                oldest = data['Time']
                print(post(data))

