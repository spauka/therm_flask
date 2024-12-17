import config

from flask import Flask, request, render_template, render_template_string, Response, make_response, send_from_directory, redirect
from flask_sqlalchemy import SQLAlchemy, get_debug_queries

from temp_log import *

import json
from time import mktime, gmtime
from datetime import datetime, timedelta
from math import isnan, isinf

app = Flask("Thermometry", static_url_path="/static")
app.debug = False
app.config['SQLALCHEMY_DATABASE_URI'] = config.db
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config.track_modifications
app.config['SQLALCHEMY_RECORD_QUERIES'] = True

db.init_app(app)

@app.after_request
def after_request(response):
    if app.debug:
        for query in get_debug_queries():
            print("Query: %s\n\tParameters: %s\n\tDuration: %fs\n\tContext: %s\n" % (query.statement, query.parameters, query.duration, query.context))
    return response

@app.route('/')
def index():
    return redirect('/static/index.html', code=301)

@app.route('/<fridge_name>/<data_type>/', defaults={'sensor': None}, methods=['GET', 'POST'])
@app.route('/<fridge_name>/<data_type>/<sensor>')
def get_data(fridge_name, data_type, sensor):
    # First pull up the relevant fridge
    try:
        fridge = Fridges.get_fridge(fridge_name)
    except KeyError:
        r = Response(render_template_string("Unable to find fridge {{fridge}}.", fridge=fridge_name))
        r.status_code = 404
        return r

    # Are we looking for a supplementary field?
    if data_type != 'data':
        sup = fridge.supplementary.filter_by(name=data_type)
        sup = sup.first()
        if sup is None:
            r = Response(render_template_string('Unable to find supplementary set {{suppl}}.', suppl=data_type))
            r.status_code = 404
            return r
        source = sup
    else:
        sup = None
        source = fridge

    # Check whether we are trying to put new data in to the database
    if request.method == 'POST':
        return Response(insert_data(fridge, sup))

    if 'count' in request.args:
        try:
            count = int(request.args['count'])
        except ValueError:
            count = 1000
    else:
        count = 1000

    if any(x in ['legacy', 'single'] for x in request.args): # We only support fridges for this type of request
        data_raw = fridge[-count:]
        data = []
        for row in data_raw:
            data.append((row['Time'],
                         0, row["Four_K_RuO"],
                         0, row["Still_RuO"],
                         0, row["50mK_RuO"],
                         0, row["MC_CMN"],
                         0, row["MC_PT"]))
            if 'single' in request.args:
                data[-1] = data[-1] + (0, row["four_K_PT_front"])
        if 'legacy' in request.args:
            return Response(render_template("data_legacy.csv", data=data), mimetype='text/plain')
        else:
            return Response(render_template("data_single.csv", data=data), mimetype='text/plain')
    elif 'sensors' in request.args:
        data = [{'name': x.display_name, 'column_name': x.column_name} for x in source.sensors.filter_by(visible=1).order_by("view_order")]
    elif 'summary' in request.args:
        data_raw = source[-30:]
        data = []
        for row in data_raw:
            row = dict(row)
            if 'MC_Pt' in row: # Leiden Fridges
                if row['MC_Pt'] > 20000 and row['MC_Pt'] < 500000:
                    data.append(row['MC_Pt'])
                elif row['MC_Speer'] is not None and row['MC_Speer'] < 4000:
                    data.append(row['MC_Speer'])
                else:
                    data.append(row['Four_K_RuO'])
            elif 'MC' in row: # Bluefors Fridges
                if 'Probe' in row and not isnan(row['Probe']):
                    data.append(row['Probe'])
                elif isnan(row['MC']) or row['MC'] > 80.000:
                    if 'Still' in row and row['Still'] < 1.200:
                        data.append(0.007)
                    else:
                        data.append(row['Still'])
                else:
                    data.append(row['MC'])
            elif 'ProbeTemp' in row: # NMR Cryostat
                data.append(float(row['ProbeTemp'] if row['ProbeTemp'] else 0)*1000)
            elif 'Four_K_Pt' in row: # Also leiden
                if row['Four_K_Pt'] is None or row['Four_K_Pt'] < 20000:
                    data.append(row['Four_K_RuO'])
                else:
                    data.append(row['Four_K_Pt'])
            else:
                data.append("MC_Pt in row: %r" % ("MC_Pt" in row))
                data.append("Invalid row: %r" % dict(row))
    elif 'current' in request.args:
        data = source[-1]
        data = dict(data)
        data['Time'] = data['Time'].ctime()
        for key in data.keys():
            if isinstance(data[key], float) and (isinf(data[key]) or isnan(data[key])):
                data[key] = None
    else:
        if 'hourly' in request.args:
            try:
                if not sensor:
                    raise KeyError("Sensor not found")
                data_raw = list(source.hourly_avg(sensor))
            except KeyError:
                return Response("Sensor not found.")
        elif 'start' in request.args or 'stop' in request.args:
            start = datetime.fromtimestamp(float(request.args['start'])/1000)
            stop = datetime.fromtimestamp(float(request.args['stop'])/1000)
            stop += timedelta(1)
            data_raw = list(source.range(start, stop))
        else:
            data_raw = list(source[-count:])
        data = []
        if not data_raw:
            return Response("No data returned")
        if sensor:
            data = [(mktime(x['Time'].replace(tzinfo=None).timetuple())*1000, x[sensor] if x[sensor] and 0 < x[sensor] < 1000000 else None) for x in data_raw]
        else:
            return Response("Sensor not found.")

    response = make_response(json.dumps(data))
    response.mimetype = "application/json"
    response.headers['Access-Control-Allow-Origin'] = "*"
    return response

def insert_data(fridge, sup=None):
    data = {x: y for x, y in request.form.items()}
    if 'Time' in data:
        data['Time'] = datetime.fromtimestamp(float(data['Time']))
    if sup is not None:
        sup.append(**data)
    else:
        fridge.append(**data)
    return 'OK'
