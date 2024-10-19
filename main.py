import logging
import uuid
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, abort, send_file

from src.forms import SUPPORTED_FORMS
from src.job_manager import JobManager
from src.util import set_up_root_logger


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


@app.route('/create-job')
def create_job():
    return render_template(
        'create_job.html',
        job_id=uuid.uuid4(),
        reference_forms=SUPPORTED_FORMS,
    )


@app.route('/submit-job', methods=['POST'])
def submit_job():
    required_params = ['job-id', 'job-name', 'reference-form']
    if not all([param in request.form for param in required_params]) or 'job-files' not in request.files:
        logger.error(f'Missing job parameters: {request.form.keys()}')
        return redirect(url_for('submit_job'))

    auto_progress = 'auto-progress' in request.form

    try:
        job_uuid = manager.create_job(
            request.form['job-id'],
            request.form['job-name'],
            request.form['reference-form'],
            request.files.getlist('job-files')
        )
    except RuntimeError:
        logger.exception('Failed to create job')
        return redirect(url_for('submit_job'))

    if auto_progress:
        manager.start_job_thread(job_uuid)
        return redirect(url_for('job_wait', job_id=request.form['job-id']))

    return redirect(url_for('job_status', job_id=request.form['job-id']))


@app.route('/list-jobs')
def list_jobs():
    return render_template('list_jobs.html', jobs=manager.get_html_job_list())


@app.route('/export-results')
def export_results():
    return render_template('export_results.html', jobs=manager.get_exportable_jobs())


@app.route('/job-reference-image/<uuid:job_id>')
def job_reference_image(job_id: uuid.UUID):
    if job := manager.get_job(job_id):
        return send_file(job.reference_form.path)
    else:
        abort(404)


@app.route('/job-test-image/<uuid:job_id>/<int:image_id>')
def job_test_image(job_id: uuid.UUID, image_id: int):
    if job := manager.get_job(job_id):
        return send_file(job.submitted_images[image_id])
    else:
        abort(404)


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


@app.route('/job-wait/<uuid:job_id>')
def job_wait(job_id: uuid.UUID):
    if not manager.job_exists(job_id):
        return render_template('unknown_job.html', job_id=job_id)

    # Redirect to status if there is no thread
    if manager.is_job_thread_complete(job_id):
        return redirect(url_for('job_status_results', job_id=job_id))
    else:
        # TODO: Not good to reach into the job owned by a thread
        job = manager.get_job(job_id)
        return render_template('job_wait.html', job_id=job_id, job_name=job.job_name)


@app.route('/job-thread-status/<uuid:job_id>')
def job_thread_status(job_id: uuid.UUID):
    return str(manager.is_job_thread_complete(job_id)).lower()


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
        if not job.succeeded():
            return redirect(url_for('job_status', job_id=job_id))

        return render_template(
            'job_results.html',
            job_id=job_id,
            job_name=job.job_name,
            image_count=job.get_processed_results_count(),
            results=job.get_processed_results(),
        )
    else:
        return render_template('unknown_job.html', job_id=job_id)


@app.route('/progress-job/<uuid:job_id>', methods=['POST'])
def progress_job(job_id: uuid.UUID):
    if job := manager.get_job(job_id):
        job.progress_processing()
        return redirect(url_for('job_status', job_id=job.job_id))
    else:
        return render_template('unknown_job.html', job_id=job_id)


@app.route('/regress-job/<uuid:job_id>', methods=['POST'])
def regress_job(job_id: uuid.UUID):
    if job := manager.get_job(job_id):
        job.regress_processing()
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
    set_up_root_logger(verbose=True)
    manager = JobManager()

    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True, host='127.0.0.1')
