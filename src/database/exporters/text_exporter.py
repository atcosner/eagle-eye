from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, MappedAsDataclass, relationship

from .. import OrmBase


class TextExporter(MappedAsDataclass, OrmBase):
    __tablename__ = "text_exporter"
    id: Mapped[int] = mapped_column(init=False, primary_key=True)

    no_export: Mapped[bool] = mapped_column(default=False, nullable=False)

    export_field_name: Mapped[str | None] = mapped_column(default=None)
    prefix: Mapped[str | None] = mapped_column(default=None)
    suffix: Mapped[str | None] = mapped_column(default=None)

    strip_value: Mapped[bool] = mapped_column(default=True, nullable=False)

    # Relationships

    text_field_id: Mapped[int] = mapped_column(ForeignKey("text_field.id"), init=False, nullable=True)
    text_field: Mapped["TextField"] = relationship(init=False, back_populates="text_exporter")

    multiline_text_field_id: Mapped[int] = mapped_column(ForeignKey("multiline_text_field.id"), init=False, nullable=True)
    multiline_text_field: Mapped["MultilineTextField"] = relationship(init=False, back_populates="text_exporter")
