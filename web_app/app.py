from flask import Flask, render_template, request, send_file
from io import StringIO
import numpy as np
import datetime
import scriptGetDataForWeb as sns
import random

UPLOAD_FOLDER = 'file_uploaded'
ALLOWED_EXTENSIONS = {'txt', 'log', ''}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

FILE_LOG_SEEK = 0
nm_process = 8

array = np.array([])
nm_sens = 8
COLORS = ['#4dc9f6', '#f67019', '#f53794', '#537bc4', '#acc236', '#166a8f', '#00a950', '#58595b', '#8549ba']


@app.route('/')
def index():
    return render_template('index.html', title="Select your data")


@app.route('/progress')
def yy():
    try:
        f = open(sns.file_log, "r")
        aa = []
        for _ in range(nm_process + 2):
            aa.append("")
        line = f.readline()
        while line:
            spl = line.split()
            try:
                if spl[0] == "COSTRUCTION":
                    aa[nm_process + 1] = line
                elif spl[0] == "PROCESS":
                    aa[int(spl[1])] = line
            except Exception as e:
                pass
            line = f.readline()
        f.close()
        strr = ""
        for a in aa:
            strr = strr + a + "<br>"
    except:
        # print("second exc")
        strr = "wait few minutes, the server is loading the datas"
    return strr


@app.route('/moreInfo')
def indexs():
    return render_template('popup.html', title="progression")


@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        file = request.files['myfile']
        number_process = int(request.form['num_proc'])
        global nm_process
        nm_process = number_process
        number_sensor = int(request.form['num_sens'])
        global nm_sens
        nm_sens = number_sensor
        if file.filename != '':
            if ".txt" in file.filename:
                aa = file.read().decode("utf-8")
                f = StringIO(aa)
                # data = sns.run(f, number_process, number_sensor, "txt")
                # data = np.loadtxt(f, delimiter='\t', dtype="str")
                data = np.genfromtxt(f, delimiter='\t', dtype="str", autostrip=True)
                if data is None:
                    return "Wrong format file, please reload page"
                global array
                array = data
                return get_datatime()
            elif ".log" in file.filename:
                aa = file.read().decode("utf-8")
                f = StringIO(aa)
                data = sns.run(f, number_process, number_sensor, "log")
                if data is None:
                    return "Wrong format file, please reload page"
                array = data
                return get_datatime()
            else:
                try:
                    data = sns.decrypte_pck_obj(file.stream)
                except Exception as e:
                    print(e)
                    data = None
                if data is None:
                    return "Wrong format file, please reload page"
                array = data
                return get_datatime()
        else:
            return render_template('index.html', title="Select your data")


def get_datatime():
    days = []
    hours = []
    for str in array[1:, 0]:
        str = str.split()
        day = str[0:3]
        # hour = str[3]
        s = ""
        for i in day:
            s += i + " "
        if s != 'Data ' and s not in days:
            days.append(s)
        # if hour not in hours:
        #   hours.append(hour)
    number_sensor = int((len(array[0]) - 3) / 3)
    return render_template("graphics.html", days=days, hours=hours, number_sensor=number_sensor, color=COLORS,
                           title="Create your chart")


def get_data(arr, options, sensor):
    date_from = datetime.datetime.strptime(options["data_from"], '%b %d %Y ')  # !!IMPORTANT the data has one space at the end of the line
    date_to = datetime.datetime.strptime(options["data_to"], '%b %d %Y ')
    data_every = int(options.get("data_every"))
    evr = [1, 5, 60, 300, 1440]
    media = options.get("media")
    if media is not None:
        nm = "_average"
    else:
        nm = ""
    values = []
    which_data = []
    name_field = []
    for id in range(len(sensor)):
        if sensor[id] is not None:
            if options.get("risc") is not None:
                which_data.append(id * 3 + 1)
                name_field.append("Risc_" + str(id + 1) + nm)
            if options.get("signal") is not None:
                which_data.append(id * 3 + 2)
                name_field.append("Signal_" + str(id + 1) + nm)
            if options.get("volt") is not None:
                which_data.append(id * 3 + 3)
                name_field.append("Volt_" + str(id + 1) + nm)
    if options.get("temp") is not None:
        which_data.append(nm_sens * 3 + 1)
        name_field.append("Temp" + nm)
    if options.get("hum") is not None:
        which_data.append(nm_sens * 3 + 2)
        name_field.append("Hum%" + nm)

    first = True
    labels = []
    for i in which_data:
        tmp_values = []
        id = 1
        take = 1
        med = 0
        for data in arr[1:, i]:
            if media is not None and data != "NaN":
                med = med + round(float(data), 1)
            if data == "NaN":
                take = take - 1
            else:
                if take >= evr[data_every]:
                    take = 0
                    # print(array[:,0])
                    try:
                        current_date = datetime.datetime.strptime(arr[id][0], " %b %d %Y %H:%M:%S")
                    except:
                        try:
                            current_date = datetime.datetime.strptime(arr[id][0], "%b %d %Y %H:%M:%S")
                        except Exception as e:
                            print(e)
                    if date_from.date() <= current_date.date() <= date_to.date():
                        if media is not None:
                            tmp_values.append(round(float(med / evr[data_every]), 1))
                            med = 0
                        else:
                            tmp_values.append(data)
                        if first:
                            labels.append(current_date)
            id = id + 1
            take = take + 1
        values.append(tmp_values)
        first = False
    return name_field, values, labels


def gen_color():
    COLORS.append("#" + ''.join([random.choice('0123456789ABCDEF') for j in range(6)]))
    return True


@app.route('/chart', methods=['POST'])
def plotline():
    data_from = request.form.get('data_da')
    data_to = request.form.get('data_a')
    risc = request.form.get('Risc')
    signal = request.form.get('Signal')
    volt = request.form.get('Volt')
    temp = request.form.get('Temp')
    hum = request.form.get('Hum%')
    sensor = []
    for i in range(1, nm_sens + 1):
        sensor.append(request.form.get('sens_' + str(i)))
    data_every = request.form.get('data_sel')
    media = request.form.get('media')
    option = {
        "data_from": data_from,
        "data_to": data_to,
        "risc": risc,
        "signal": signal,
        "volt": volt,
        "temp": temp,
        "hum": hum,
        "data_every": data_every,
        "media": media
    }
    names, dv, dl = get_data(array, option, sensor)
    print("label len: ", len(dl))
    print("value len: ", len(dv))
    random.shuffle(COLORS)
    while len(dv) > len(COLORS):
        gen_color()
    return render_template('lineChart.html', title='line chart', labels=dl, values=dv, names=names, color=COLORS,
                           number_chart=len(dv))


@app.route('/download/array_pickle', methods=['GET', 'POST'])
def down_pickle():
    path = "file_uploaded/array_pickle"
    sns.create_pck_obj(array, "array_pickle")
    return send_file(path, as_attachment=True)


@app.route('/download/array_txt', methods=['GET', 'POST'])
def down_txt():
    path = "file_uploaded/data_txt.txt"
    sns.create_table_txt(array, "data_txt.txt")
    return send_file(path, as_attachment=True)


if __name__ == '__main__':
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.debug = True
    app.run(host='0.0.0.0')
