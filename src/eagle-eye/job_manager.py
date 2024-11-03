import logging
import pandas as pd
import shutil
import uuid
from pathlib import Path
from threading import Thread
from werkzeug.datastructures import FileStorage

from . import JOB_WORKING_DIR_PATH

from .forms import SUPPORTED_FORMS
from .forms.reference import ReferenceForm
from .job import Job, HtmlJobInfo

logger = logging.getLogger(__name__)


class JobThread(Thread):
    def __init__(self, job: Job) -> None:
        super().__init__()
        self.job = job
        self.states = []

    def run(self):
        self.job.progress_to_terminal_state(self.states)


class JobManager:
    def __init__(self):
        self.job_map: dict[uuid.UUID, Job] = {}

        # TODO: Everywhere we get a job out of the map above we need to ensure it is not owned by a thread first
        self.job_threads: dict[uuid.UUID, JobThread] = {}

        self.working_dir: Path = JOB_WORKING_DIR_PATH
        logger.info(f'JobManager working directory: {self.working_dir}')

        # Clean up old submissions
        self._retain_job_files(10)

    @staticmethod
    def get_supported_forms() -> list[ReferenceForm]:
        return SUPPORTED_FORMS

    def _retain_job_files(self, retain_count: int) -> None:
        job_dirs = [path for path in self.working_dir.glob('*') if path.is_dir()]
        sorted_dirs = sorted(job_dirs, key=lambda x: x.stat().st_mtime, reverse=True)
        for dir_path in sorted_dirs[retain_count:]:
            shutil.rmtree(dir_path)

    def job_exists(self, job_id: uuid.UUID) -> bool:
        return job_id in self.job_map

    def get_job(self, job_id: uuid.UUID) -> Job | None:
        return self.job_map.get(job_id, None)

    def get_html_job_list(self) -> list[HtmlJobInfo]:
        return [job.to_html_info() for job in self.job_map.values()]

    def get_exportable_jobs(self) -> list[Job]:
        return [job for job in self.job_map.values() if job.succeeded()]

    def create_job(
            self,
            job_id: str,
            job_name: str,
            reference_form_name: str,
            job_files: list[FileStorage] | None = None,
    ) -> uuid.UUID:
        # Find the reference form
        reference_form: ReferenceForm | None = None
        for form in SUPPORTED_FORMS:
            if form.name == reference_form_name:
                reference_form = form

        if reference_form is None:
            raise RuntimeError(f'Failed to find a reference form with name: "{reference_form_name}"')

        job_uuid = uuid.UUID(job_id)
        self.job_map[job_uuid] = Job(
            parent_directory=self.working_dir,
            job_id=job_uuid,
            reference_form=reference_form,
            job_name=job_name,
        )

        # Save files if we were given then
        if job_files is not None:
            self.job_map[job_uuid].save_files(job_files)

        return job_uuid

    def export_jobs(self, job_ids: list[uuid.UUID]) -> Path:
        dataframes = []
        for job_id in job_ids:
            if job := self.get_job(job_id):
                dataframes.append(job.export_results())
            else:
                logger.warning(f'Did not find job with id: {job_id}')

        excel_path = self.working_dir / 'export.xlsx'
        merged_df = pd.concat(dataframes).reset_index()

        # Clean up the dataframe before we export
        export_columns = [column for column in merged_df.columns.values if column != 'index']
        merged_df.to_excel(excel_path, index=False, columns=export_columns)
        return excel_path

    def start_job_thread(self, job_id: uuid.UUID) -> None:
        job = self.get_job(job_id)
        assert job is not None, f'No job: {job_id}'

        thread = JobThread(job)
        thread.start()
        self.job_threads[job_id] = thread

    def is_job_thread_complete(self, job_id: uuid.UUID) -> bool:
        if job_id not in self.job_threads:
            return True

        thread = self.job_threads[job_id]
        if thread.is_alive():
            return False
        else:
            # Job is finished
            self.job_map[job_id] = thread.job
            self.job_threads.pop(job_id)
            return True

