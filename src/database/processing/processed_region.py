from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, MappedAsDataclass, relationship

from .. import OrmBase
from ..processed_fields.processed_field_group import ProcessedFieldGroup


class ProcessedRegion(MappedAsDataclass, OrmBase):
    __tablename__ = "processed_region"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)

    local_id: Mapped[int]
    name: Mapped[str]

    linking_identifier: Mapped[int | None]
    human_verified: Mapped[bool] = mapped_column(default=False, init=False)

    # Relationships

    process_result_id: Mapped[int] = mapped_column(ForeignKey("process_result.id"), init=False)
    process_result: Mapped["ProcessResult"] = relationship(init=False, back_populates="regions")

    groups: Mapped[list[ProcessedFieldGroup]] = relationship(init=False, back_populates="processed_region")
