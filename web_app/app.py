import os
from flask import Flask, render_template, request
from io import StringIO
from werkzeug.utils import secure_filename
import scriptGetDataForWeb as sns

UPLOAD_FOLDER = 'file_uploaded'
ALLOWED_EXTENSIONS = {'txt', 'log', ''}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


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
            return graphics(data)
        else:
            print("enter pickle")
            data = sns.decrypte_pck_obj(file.stream)
            return graphics(data)

def graphics(np_array):
    render_template("grahics.html")

if __name__ == '__main__':
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.debug = True
    app.run()