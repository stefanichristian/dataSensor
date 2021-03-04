import os
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage
import scriptGetData as sns

UPLOAD_FOLDER = 'file_uploaded'
ALLOWED_EXTENSIONS = {'txt', 'log'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/submit', methods = ['POST'])
def submit():
    if request.method == 'POST':
        file = request.files['myfile']
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        number_process = int (request.form['num_proc'])
        number_sensor = int(request.form['num_sens'])
        #print("file type: ", str(myfilelog))
        sns.run("file_uploaded/aa.txt", number_process, number_sensor)
        return 'file uploaded successfully'

if __name__ == '__main__':
    app.debug = True
    app.run()