# LabMon
A python package for logging, monitoring and displaying parameters
for fridges and other equipment in a lab environment.

## File Layout
```
/home/user/Projects/flask-tutorial
├── html/ - Static pages to display thermometry
│   ├── js
│   │   ├── app.config.js - Config file for static application
├── labmon/ - Flask based python package to save and restore data
├── scripts/ - Scripts to run on equipment to upload data
├── tests/ - Test files
├── pyproject.toml
└── labmon_config.json - Template config file for labmon
```

## Installing Monitoring
To install monitoring, first install labmon as a module on the computer that
hosts the log files or fridge monitoring/control software. If you use conda or
other similar package manager, set up a new environment for labmon. Then, we can
use pip to install the labmon package:
```console
$ pip install git+https://github.com/spauka/therm_flask.git
```

The first time you run the monitor, it will create a labmon_config.json file
in your home directory. You can start the monitoring software by running the following
command:
```console
$ python -m labmon.upload
Config file doesn't exist. Creating new file at /Users/{username}/qcodes/labmon_config.json.
Created config file at /Users/{username}/qcodes/labmon_config.json.
Please fill in details and start again.
```

Edit the file to fill in the fridge details and enable the uploader. A snippet of the relevant
part of the config file is shown below with an example configuration for a BlueFors_LD fridge:
```json
{
  ...
  "UPLOAD": {
    "ENABLED": true,
    "MOCK": true,
    "BASE_URL": "https://qsyd.sydney.edu.au/data",
    "FRIDGE": "BlueFors_LD",
    "ENABLED_UPLOADERS": [
      "BlueFors"
    ],
    "BLUEFORS_CONFIG": {
      "LOG_DIR": "C:\\BlueFors_Logs",
      "MAX_AGE": 180.0,
      "SENSORS": {
        "Fifty_K": 1,
        "Four_K": 2,
        "Magnet": 3,
        "Still": 5,
        "MC": 6
      },
      "UPLOAD_COMPRESSORS": true,
      "NUM_COMPRESSORS": 1,
      "COMPRESSOR_BOUNCE_N": 15,
      "UPLOAD_MAXIGAUGE": true
    }
  }
  ...
}
```
Note that `UPLOAD.ENABLED` is set to true and the fridge name is filled in. If you have additional sensors you wish
to upload, you can add them to the list of sensors along with the channel on the temperature controller.

If you have a fridge with more than 1 compressor, you can increase the number here. By default, we log the
pressure gauge and compressors as well as the fridge temperatures.

Next, when you run the command again, it should begin to upload data:
```console
$ python -m labmon.upload
2025-02-07 15:48:04,055 - INFO:httpx - HTTP Request: GET https://qsyd.sydney.edu.au/data/BlueFors_LD?current= "HTTP/2 200 OK"
2025-02-07 15:48:04,078 - INFO:labmon.uploaders.uploader - Latest data for fridge BlueFors_LD was 2025-02-07T16:46:10+11:00.
...
```