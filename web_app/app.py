import os
import sys
from flask import Flask, render_template, request
from io import StringIO
import numpy as np
from werkzeug.utils import secure_filename
import scriptGetDataForWeb as sns

UPLOAD_FOLDER = 'file_uploaded'
ALLOWED_EXTENSIONS = {'txt', 'log', ''}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


array = np.array([])
nm_sens = 8

labels = [
    'JAN', 'FEB', 'MAR', 'APR',
    'MAY', 'JUN', 'JUL', 'AUG',
    'SEP', 'OCT', 'NOV', 'DEC'
]

values = [
    967.67, 1190.89, 1079.75, 1349.19,
    2328.91, 2504.28, 2873.83, 4764.87,
    4349.29, 6458.30, 9907, 16297
]

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/submit', methods = ['POST'])
def submit():
    if request.method == 'POST':
        file = request.files['myfile']
        number_process = int(request.form['num_proc'])
        number_sensor = int(request.form['num_sens'])
        global nm_sens
        nm_sens = number_sensor
        if ".txt" in file.filename:
            print("enter txt")
            pass
        elif ".log" in file.filename:
            print("enter log")
            aa = file.read().decode("utf-8")
            f = StringIO(aa)
            data = sns.run(f, number_process, number_sensor)
            global array
            array = data
            return get_datatime(data)
        else:
            print("enter pickle")
            data = sns.decrypte_pck_obj(file.stream)
            return render_template("graphics.html", np_array = data)


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
    return render_template("graphics.html", np_array=np_array, days=days, hours=hours, number_sensor=number_sensor, title="diocane")


@app.route('/plot', methods = ['POST'])
def line():
    line_labels = labels
    line_values = values
    return render_template('lineChart.html', title='Bitcoin Monthly Price in USD', max=17000, labels=line_labels, values=line_values)


@app.route('/plota', methods = ['POST'])
def plotline():
    data_from = request.form['data_da']
    data_to = request.form['data_a']
    risk = request.form['Risk']
    signal = request.form['Signal']
    volt = request.form['Volt']
    hum = request.form['Temp']
    temp = request.form['Hum%']
    sensor = []
    for i in range(1, nm_sens+1):
        sensor.append(request.form['sens_'+str(i)])
    data_every = request.form['data_sel']
    media = request.form['media']
    dt = []
    db = []
    i = 1
    for id in array[1:,1]:
        if data_from in array[i][0]:
            dt.append(id)
            ora = array[i][0].split()
            db.append(ora[3])
        i += 1

    print("label: ",db)
    print("value: ",dt)
    line_labels = db
    line_values = dt
    return render_template('lineChart.html', title='first line chart', max=17000, labels=line_labels, values=line_values)


if __name__ == '__main__':
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.debug = True
    app.run()