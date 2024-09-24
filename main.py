import logging
import uuid
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, abort, send_file
from pathlib import Path

from src.job_manager import JobManager
from src.util import set_up_root_logger

FORMS_PATH = Path(__file__).parent / 'forms' / 'production'
REFERENCE_IMAGE = FORMS_PATH / 'kt_field_form_v8.png'

app = Flask(
    __name__,
    static_folder='webserver/static/',
    template_folder='webserver/templates/',
)

logger = logging.getLogger(__name__)
manager: JobManager | None = None


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/reference-image')
def reference_image():
    return send_from_directory(
        FORMS_PATH,
        REFERENCE_IMAGE.name
    )


@app.route('/create-job')
def create_job():
    return render_template('create_job.html', job_id=uuid.uuid4())


@app.route('/submit-job', methods=['POST'])
def submit_job():
    if 'job-files' not in request.files or 'job-id' not in request.form:
        logger.error('Missing job parameters')
        return redirect(url_for('submit_job'))

    job = manager.create_job(request.form['job-id'], request.form['job-name'])
    job.save_files(request.files.getlist('job-files'))

    return redirect(url_for('job_status', job_id=job.job_id))


@app.route('/list-jobs')
def list_jobs():
    return render_template('list_jobs.html', jobs=manager.get_html_job_list())


@app.route('/export-results')
def export_results():
    return render_template('export_results.html', jobs=manager.get_exportable_jobs())


@app.route('/job-file/<uuid:job_id>/<int:image_id>/<part_name>')
@app.route('/job-file/<uuid:job_id>/<int:image_id>/<part_name>/<file_name>')
def job_file(job_id: uuid.UUID, image_id: int, part_name: str, file_name: str | None = None):
    # Handle some files not having a part
    if '.' in part_name:
        file_name = part_name
        part_name = ''

    if job := manager.get_job(job_id):
        return send_from_directory(
            job.working_dir / str(image_id) / part_name,
            file_name
        )
    else:
        abort(404)


@app.route('/job-status/<uuid:job_id>')
def job_status(job_id: uuid.UUID):
    if job := manager.get_job(job_id):
        return render_template(
            'job_status.html',
            job_id=job_id,
            job_name=job.job_name,
            job_state=job.get_current_state(),
            state_log=job.get_state_changes(),
        )
    else:
        return render_template('unknown_job.html', job_id=job_id)


@app.route('/job-status/<uuid:job_id>/pre-process')
def job_status_pre_process(job_id: uuid.UUID):
    if job := manager.get_job(job_id):
        return render_template(
            'job_pre_process.html',
            job_id=job_id,
            job_name=job.job_name,
            results_count=len(job.alignment_results),
            results=job.alignment_results,
        )
    else:
        return render_template('unknown_job.html', job_id=job_id)


@app.route('/job-status/<uuid:job_id>/results')
def job_status_results(job_id: uuid.UUID):
    if job := manager.get_job(job_id):
        return render_template(
            'job_results.html',
            job_id=job_id,
            job_name=job.job_name,
            image_count=job.get_processed_results_count(),
            results=job.get_processed_results(),
        )
    else:
        return render_template('unknown_job.html', job_id=job_id)


@app.route('/continue-job/<uuid:job_id>', methods=['POST'])
def continue_job(job_id: uuid.UUID):
    if job := manager.get_job(job_id):
        job.continue_processing()
        return redirect(url_for('job_status', job_id=job.job_id))
    else:
        return render_template('unknown_job.html', job_id=job_id)


@app.route('/job-status/<uuid:job_id>/<int:image_id>/update', methods=['POST'])
def update_job_results(job_id: uuid.UUID, image_id: int):
    job = manager.get_job(job_id)
    if job is None:
        return render_template('unknown_job.html', job_id=job_id)

    job.update_fields(image_id, request.form)
    return redirect(url_for('job_status_results', job_id=job_id, focus_id=image_id))


@app.route('/export-jobs', methods=['POST'])
def export_jobs():
    jobs_to_export = [uuid.UUID(key) for key, value in request.form.items() if value == 'on']
    excel_path = manager.export_jobs(jobs_to_export)
    return send_file(excel_path)


if __name__ == '__main__':
    set_up_root_logger(verbose=False)
    manager = JobManager(reference_image=REFERENCE_IMAGE)

    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True, host='127.0.0.1')
