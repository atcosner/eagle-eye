import logging
import sys
from pathlib import Path
from sqlalchemy.orm import Session

from PyQt6.QtWidgets import QApplication

from src.database import DB_ENGINE
from src.database.copy import copy_reference_form
from src.database.reference_form import ReferenceForm
from src.gui.wizards.reference_form_wizard import ReferenceFormWizard
from src.util.logging import configure_root_logger
from src.util.types import FormLinkingMethod, FormAlignmentMethod

logger = logging.getLogger(__name__)

configure_root_logger(logging.INFO)

app = QApplication(sys.argv)
app.setQuitOnLastWindowClosed(True)

wizard = ReferenceFormWizard()
if wizard.exec():
    # create a new reference form
    logger.info(f'Creating new reference form: {wizard.field("form.name")}')
    with Session(DB_ENGINE) as session:
        alignment_enum = FormAlignmentMethod[wizard.field('form.align_method')]

        new_form = ReferenceForm(
            name=wizard.field('form.name'),
            path=Path(wizard.field('form.file_path')),
            alignment_method=alignment_enum,
            alignment_mark_count=wizard.field('form.align_marks'),
            linking_method=FormLinkingMethod[wizard.field('form.link_method')],
        )

        # if we are copying another form, copy in all the regions and fields
        if wizard.field('form.copy_existing'):
            copy_form = session.get(ReferenceForm, wizard.field('form.existing_id'))
            copy_reference_form(new_form, copy_form, copy_details=False)

        session.add(new_form)
        session.commit()
