import os
import sys
from flask import Flask, render_template, request
from io import StringIO
import numpy as np
import datetime
from werkzeug.utils import secure_filename
import scriptGetDataForWeb as sns

UPLOAD_FOLDER = 'file_uploaded'
ALLOWED_EXTENSIONS = {'txt', 'log', ''}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


LOADED = False


array = np.array([])
nm_sens = 8
COLORS = ['#4dc9f6', '#f67019', '#f53794', '#537bc4', '#acc236', '#166a8f',	'#00a950', '#58595b', '#8549ba']


@app.route('/')
def index():
    return render_template('index.html', title="Select your data")


@app.route('/submit', methods = ['POST'])
def submit():
    if request.method == 'POST':
        file = request.files['myfile']
        number_process = int(request.form['num_proc'])
        number_sensor = int(request.form['num_sens'])
        global nm_sens
        nm_sens = number_sensor
        if ".txt" in file.filename:
            pass
        elif ".log" in file.filename:
            aa = file.read().decode("utf-8")
            f = StringIO(aa)
            data = sns.run(f, number_process, number_sensor)
            global array
            array = data
            return get_datatime(data)
        else:
            data = sns.decrypte_pck_obj(file.stream)
            return get_datatime(data)


def get_datatime(np_array):
    days = []
    hours = []
    for str in np_array[1:, 0]:
        str=str.split()
        day = str[0:3]
        hour = str[3]
        s = ""
        for i in day:
            s += i+" "
        if s != 'Data ' and s not in days:
            days.append(s)
        if hour not in hours:
            hours.append(hour)
    number_sensor = int((len(np_array[0])-3)/3)
    return render_template("graphics.html", np_array=np_array, days=days, hours=hours, number_sensor=number_sensor, color=COLORS, title="Create your chart")


def get_data(arr, options, sensor):
    date_from = datetime.datetime.strptime(options["data_from"], '%b %d %Y ') # !!IMPORTANT the data has one space at the end of the line
    date_to = datetime.datetime.strptime(options["data_to"], '%b %d %Y ')
    values = []
    which_data = []
    name_field = []
    for id in range(len(sensor)):
        if sensor[id] is not None:
            if options.get("risk") is not None:
                which_data.append(id*3+1)
                name_field.append("Risk_"+str(id+1))
            if options.get("signal") is not None:
                which_data.append(id*3+2)
                name_field.append("Signal_" + str(id + 1))
            if options.get("volt") is not None:
                which_data.append(id*3+3)
                name_field.append("Volt_" + str(id + 1))
    first = True
    labels = []
    for i in which_data:
        tmp_values = []
        id = 1
        for data in arr[1:, i]:
            current_date = datetime.datetime.strptime(arr[id][0], " %b %d %Y %H:%M:%S")
            if date_from.date() <= current_date.date() <= date_to.date():
                tmp_values.append(data)
                if first:
                    labels.append(current_date)
            id = id + 1
        values.append(tmp_values)
        first = False

    return name_field, values, labels


@app.route('/plota', methods = ['POST'])
def plotline():
    data_from = request.form.get('data_da')
    data_to = request.form.get('data_a')
    risk = request.form.get('Risk')
    signal = request.form.get('Signal')
    volt = request.form.get('Volt')
    temp = request.form.get('Temp')
    hum = request.form.get('Hum%')
    sensor = []
    for i in range(1, nm_sens+1):
        sensor.append(request.form.get('sens_'+str(i)))
    data_every = request.form.get('data_sel')
    media = request.form.get('media')
    option = {
        "data_from": data_from,
        "data_to": data_to,
        "risk": risk,
        "signal": signal,
        "volt": volt,
        "temp":   temp,
        "hum": hum,
        "data_every": data_every,
        "media": media
    }
    names, dv, dl = get_data(array, option, sensor)
    print("label len: ", len(dl))
    print("value len: ", len(dv))
    return render_template('lineChart.html', title='line chart', labels=dl, values=dv, names=names, color=COLORS, number_chart=len(dv))


if __name__ == '__main__':
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.debug = True
    app.run()