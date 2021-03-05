import os
from flask import Flask, render_template, request
from io import StringIO
from werkzeug.utils import secure_filename
import scriptGetDataForWeb as sns

UPLOAD_FOLDER = 'file_uploaded'
ALLOWED_EXTENSIONS = {'txt', 'log', ''}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


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
        if ".txt" in file.filename:
            print("enter txt")
            pass
        elif ".log" in file.filename:
            print("enter log")
            aa = file.read().decode("utf-8")
            f = StringIO(aa)
            data = sns.run(f, number_process, number_sensor)
            return give_data(data)
        else:
            print("enter pickle")
            data = sns.decrypte_pck_obj(file.stream)
            return render_template("graphics.html", np_array = data)

def give_data(np_array):
    days = []
    for day in np_array[:, 0]:
        day=day.split()
        day = day[0:3]
        s = ""
        for i in day:
            s += i+" "
        if s != 'Data ' and s not in days:
            days.append(s)
    number_sensor = int((len(np_array[0])-3)/3)
    return render_template("graphics.html", np_array=np_array, days=days, number_sensor=number_sensor, title="diocane")

@app.route('/plot', methods = ['POST'])
def line():
    line_labels = labels
    line_values = values
    return render_template('lineChart.html', title='Bitcoin Monthly Price in USD', max=17000, labels=line_labels, values=line_values)


if __name__ == '__main__':
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.debug = True
    app.run()