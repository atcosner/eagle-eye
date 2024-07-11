import uuid
from flask import Flask, render_template, request, redirect, url_for, make_response

from processing.job_manager import JobManager
from processing.util import set_up_root_logger

app = Flask(
    __name__,
    static_folder='webserver/static/',
    template_folder='webserver/templates/',
)

manager: JobManager | None = None


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/create-job')
def create_job():
    return render_template('create_job.html', job_id=uuid.uuid4())


@app.route('/submit-job', methods=['POST'])
def submit_job():
    if 'job-files' not in request.files or 'job-id' not in request.form:
        print('Missing job parameters')
        return redirect(url_for('submit_job'))

    job = manager.create_job(request.form['job-id'])
    job.save_files(request.files.getlist('job-files'))

    return redirect(url_for('job_status', job_id=job.job_id))


@app.route('/job-status/<uuid:job_id>')
def job_status(job_id: str):
    return render_template('job_status.html', job_id=job_id)


if __name__ == '__main__':
    set_up_root_logger(verbose=True)
    manager = JobManager()

    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True, host='127.0.0.1')
