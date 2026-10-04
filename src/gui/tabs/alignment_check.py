from sqlalchemy.orm import Session

from src.database import DB_ENGINE
from src.database.job import Job

from .processing_step import ProcessingStep
from ..widgets.alignment_check_details import AlignmentCheckDetails
from ..widgets.file.file_status_list import FileStatusItem, ListMode


class AlignmentCheck(ProcessingStep):
    def __init__(self):
        super().__init__(
            step_button_text='Check Alignment',
            details_cls=AlignmentCheckDetails,
        )

    def load_job(self, job: Job | int | None) -> None:
        super().load_job(job)
        if job is None:
            return

        with Session(DB_ENGINE) as session:
            job = session.get(Job, job) if isinstance(job, int) else job
            self._job_db_id = job.id

            # TODO: Should this have its own ListMode?
            self.file_list.load_job(ListMode.PRE_PROCESS, job)

        # Run GUI updates based if all our items are complete
        self.update_control_state()

    def start_worker(self, item: FileStatusItem) -> None:
        # TODO: Nothing to process yet, this step only views the alignment results
        pass
