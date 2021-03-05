import os
from flask import Flask, render_template, request
from io import StringIO
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage
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
        #filename = secure_filename(file.filename)
        #file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        number_process = int (request.form['num_proc'])
        number_sensor = int(request.form['num_sens'])
        #file = [line.decode("utf-8") for line in file]
        aa = file.read().decode("utf-8")
        f = StringIO(aa)
        sns.run(f, number_sensor, number_sensor)


        #f = file.read()
        #print("asdas",file.readline())
        #print(str(file[0]))
        #print("file type: ", str(myfilelog))
        #sns.run("file_uploaded/aa.txt", number_process, number_sensor)
        #sns.run(file.read(), number_process, number_sensor)
        return render_template('graphics.html')

if __name__ == '__main__':
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.debug = True
    app.run()