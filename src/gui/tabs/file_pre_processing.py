from PyQt6.QtCore import pyqtSlot
from sqlalchemy.orm import Session

from src.database import DB_ENGINE
from src.database.job import Job
from src.processing.pre_process_worker import PreProcessingWorker
from src.util.status import FileStatus
from src.util.types import FileDetails

from .processing_step import ProcessingStep
from ..widgets.file.file_status_list import FileStatusItem
from ..widgets.pre_processing_details import PreProcessingDetails


class FilePreProcessing(ProcessingStep):
    def __init__(self):
        super().__init__(
            step_button_text='Pre-Process Files',
            details_cls=PreProcessingDetails,
        )

    def load_job(self, job: Job | int | None) -> None:
        super().load_job(job)
        if job is None:
            return

        # Check if any of our files had a pre-process result
        with Session(DB_ENGINE) as session:
            job = session.get(Job, job) if isinstance(job, int) else job
            self._job_db_id = job.id

            # Check if any of the files have a pre-processing result
            any_pre_process = any([(input_file.pre_process_result is not None) for input_file in job.input_files])

            # If any files had a pre-processing result, add them all
            if any_pre_process:
                for input_file in job.input_files:
                    # Determine the initial status
                    initial_status = FileStatus.PENDING
                    if input_file.pre_process_result is not None:
                        if input_file.pre_process_result.successful_alignment:
                            initial_status = FileStatus.SUCCESS
                        else:
                            initial_status = FileStatus.FAILED

                    self.file_list.add_file(
                        file=FileDetails(
                            db_id=input_file.id,
                            path=input_file.path,
                        ),
                        initial_status=initial_status,
                    )

        # Run GUI updates based if all our items are complete
        self.update_control_state()

    @pyqtSlot(list)
    def add_files(self, files: list[FileDetails]) -> None:
        self.file_list.add_files(files)
        self.update_control_state()

    def start_worker(self, item: FileStatusItem) -> None:
        worker = PreProcessingWorker(self._job_db_id, item.get_details(), self.thread_mutex)
        worker.updateStatus.connect(self.worker_status_update)
        worker.processingComplete.connect(self.worker_complete)
        
        super().start_thread(item, worker)
