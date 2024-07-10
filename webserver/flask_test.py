import uuid
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__, static_folder='static/')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/create-job')
def create_job():
    return render_template('create_job.html', instance_id=uuid.uuid4())


@app.route('/submit-job', methods=['POST'])
def submit_job():
    if 'job-files' not in request.files:
        print('No file part')
        return redirect(url_for('index'))

    for file in request.files.getlist('job-files'):
        print(file.filename)

    return redirect(url_for('index'))
