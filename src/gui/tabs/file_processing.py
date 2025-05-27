from sqlalchemy.orm import Session

from PyQt6.QtGui import QIcon

from src.database import DB_ENGINE
from src.database.job import Job
from src.processing.process_worker import ProcessWorker
from src.util.resources import GENERIC_ICON_PATH
from src.util.settings import SettingsManager
from src.util.status import FileStatus
from src.util.types import FileDetails

from .processing_step import ProcessingStep
from ..widgets.file.file_status_list import FileStatusItem


class FileProcessing(ProcessingStep):
    def __init__(self):
        super().__init__(
            step_button_text='Process Files',
            details_cls=None,  # TODO: Should we show any details?
        )

        self._check_api_config()

    def _check_api_config(self) -> None:
        valid_config = SettingsManager().valid_api_config()
        self.auto_process.setDisabled(not valid_config)
        self.process_file_button.setDisabled(not valid_config)

        # Update the button icon
        if valid_config:
            self.process_file_button.setToolTip(None)
            self.process_file_button.setIcon(QIcon())
        else:
            self.process_file_button.setToolTip('The Google Vision API is not configured')
            self.process_file_button.setIcon(QIcon(str(GENERIC_ICON_PATH / 'bad.png')))

    def load_job(self, job: Job | int | None) -> None:
        super().load_job(job)
        if job is None:
            return

        with Session(DB_ENGINE) as session:
            job = session.get(Job, job) if isinstance(job, int) else job
            self._job_db_id = job.id

            for input_file in job.input_files:
                # Only add files that have been pre-processed successfully
                if input_file.pre_process_result is None:
                    continue

                # Only add files that were aligned to their reference
                if not input_file.pre_process_result.successful_alignment:
                    continue

                # self.file_list.add_file(
                #     file=FileDetails(
                #         db_id=input_file.id,
                #         path=input_file.path,
                #     ),
                #     # TODO: Failed status?
                #     initial_status=FileStatus.SUCCESS if input_file.process_result is not None else FileStatus.PENDING,
                # )

        # Run GUI updates based if all our items are complete
        self.update_control_state()

    def start_worker(self, item: FileStatusItem) -> None:
        details = item.get_details()
        worker = ProcessWorker(details.path.name, self._job_db_id, details.db_id, self.thread_mutex)
        worker.updateStatus.connect(self.worker_status_update)
        worker.processingComplete.connect(self.worker_complete)

        super().start_thread(item, worker)
