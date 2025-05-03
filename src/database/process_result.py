from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, MappedAsDataclass, relationship, attribute_keyed_dict

from . import OrmBase
from .processed_region import ProcessedRegion


class ProcessResult(MappedAsDataclass, OrmBase):
    __tablename__ = "process_result"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    input_file_id: Mapped[int] = mapped_column(ForeignKey("input_file.id"), init=False)

    validated: Mapped[bool] = mapped_column(default=False, init=False)

    # Relationships

    input_file: Mapped["InputFile"] = relationship(init=False, back_populates="process_result")
    regions: Mapped[dict[int, ProcessedRegion]] = relationship(
        init=False,
        collection_class=attribute_keyed_dict("local_id"),
        back_populates="process_result",
    )
