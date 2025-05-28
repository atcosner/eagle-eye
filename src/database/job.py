import uuid
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, MappedAsDataclass, relationship

from . import OrmBase
from .input_file import InputFile


class Job(MappedAsDataclass, OrmBase):
    __tablename__ = "job"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    reference_form_id: Mapped[int] = mapped_column(ForeignKey("reference_form.id"), init=False, nullable=True)

    name: Mapped[str]
    uuid: Mapped[uuid.UUID]

    # Relationships

    reference_form: Mapped["ReferenceForm"] = relationship(init=False, back_populates="jobs")
    input_files: Mapped[list[InputFile]] = relationship(init=False, back_populates="job")

    #
    # Custom Functions
    #
    def _pre_processing_statuses(self) -> list[bool]:
        # ignore container files
        return [(file.pre_process_result is not None) for file in self.input_files if not file.container_file]

    def _processing_statuses(self) -> list[bool]:
        # ignore container files
        return [(file.process_result is not None) for file in self.input_files if not file.container_file]

    def any_pre_processed(self) -> bool:
        statuses = self._pre_processing_statuses()
        return statuses and any(statuses)

    def all_pre_processed(self) -> bool:
        statuses = self._pre_processing_statuses()
        return statuses and all(statuses)

    def any_processed(self) -> bool:
        statuses = self._processing_statuses()
        return statuses and any(statuses)

    def all_processed(self) -> bool:
        statuses = self._processing_statuses()
        return statuses and all(statuses)

    def get_status_str(self) -> str:
        if not self.input_files:
            return 'Picking Files'

        all_pre_processed = all([(file.pre_process_result is not None) for file in self.input_files])
        all_processed = all([(file.process_result is not None) for file in self.input_files])

        all_verified = True
        for file in self.input_files:
            if file.process_result is None:
                all_verified = False
                continue
            else:
                region_statuses = [region.human_verified for region in file.process_result.regions.values()]
                if not all(region_statuses):
                    all_verified = False
                    continue

        if all_verified:
            return 'Complete'
        elif all_processed:
            return 'Checking Results'
        elif all_pre_processed:
            return 'Processing'
        else:
            return 'Pre-Processing'
