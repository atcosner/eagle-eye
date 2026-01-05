from PyQt6.QtWidgets import QVBoxLayout, QLabel, QGroupBox, QCheckBox

from src.gui.widgets.util.link_label import LinkLabel

from ..util.base_page import BasePage


class ProjectPage(BasePage):
    def __init__(self):
        super().__init__('Eagle Eye | Google Cloud Project')

        self.step_one_box = QGroupBox('Step 1 - Create a Google Cloud Project')
        self.step_two_box = QGroupBox('Step 2 - Enable Billing')
        self.step_three_box = QGroupBox('Step 3 - Enable the Vision API')

        self._set_up_layout()

    def _set_up_step_one(self) -> None:
        project_label = LinkLabel(
            r'Follow this guide to create a '
            r'<a href="https://developers.google.com/workspace/guides/create-project">Google Cloud Project</a>'
        )
        step_check = QCheckBox('I have created a Google Cloud Project')
        self.registerField('step_one.done*', step_check)

        project_layout = QVBoxLayout()
        project_layout.addWidget(project_label)
        project_layout.addWidget(step_check)
        self.step_one_box.setLayout(project_layout)

    def _set_up_step_two(self) -> None:
        billing_label = LinkLabel(
            'Enable '
            '<a href="https://cloud.google.com/billing/docs/how-to/modify-project#enable_billing_for_a_project">Billing</a> '
            'in your Google Cloud Project'
        )
        step_check = QCheckBox('I have enabled billing in my project')
        self.registerField('step_two.done*', step_check)

        project_layout = QVBoxLayout()
        project_layout.addWidget(billing_label)
        project_layout.addWidget(step_check)
        self.step_two_box.setLayout(project_layout)

    def _set_up_step_three(self) -> None:
        enable_vision = LinkLabel(
            'Enable the '
            '<a href="https://cloud.google.com/vision/docs/setup#api">Cloud Vision</a> '
            'API'
        )
        step_check = QCheckBox('I have enabled the Google Vision API')
        self.registerField('step_three.done*', step_check)

        project_layout = QVBoxLayout()
        project_layout.addWidget(enable_vision)
        project_layout.addWidget(step_check)
        self.step_three_box.setLayout(project_layout)

    def _set_up_layout(self) -> None:
        welcome_text = QLabel(
            'Please follow the steps below to set up and configure a Google Cloud Project'
        )
        margins = welcome_text.contentsMargins()
        margins.setBottom(10)
        welcome_text.setContentsMargins(margins)

        self._set_up_step_one()
        self._set_up_step_two()
        self._set_up_step_three()

        layout = QVBoxLayout()
        layout.addWidget(welcome_text)
        layout.addWidget(self.step_one_box)
        layout.addWidget(self.step_two_box)
        layout.addWidget(self.step_three_box)
        self.setLayout(layout)
