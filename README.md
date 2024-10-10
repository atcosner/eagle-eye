<h1 align="center"><img src="/webserver/static/images/ku_bi_logo.jpg"></h1>

KU BI Collection Form Processor
===============================

Description
-----------
This project was created for the [University of Kansas Biodiversity Institute](https://biodiversity.ku.edu/) to allow for the automatic OCR and digitization of paper collection forms.
While testing and development was done for specific KU collection forms this project was designed to allow for the addition of other form templates.

Optical Character Recognition is supported by the [Google Vision API](https://cloud.google.com/vision?hl=en) but swapping for other handwriting recognition models is possible.


Features
--------
* Batch processing on a list of scanned forms
* Automatic image alignment with support for +/-10 degrees of rotation in the scanned form
* OCR of text in the form via the Google Vision API
* Handles user corrections of the OCR results via a simple web interface
* Validators to ensure form data complies with pre-specified formats (i.e. times look like HH:MM)
* Export of data into an Excel workbook for further processing


Requirements
-------------
* [Python 3.12](https://www.python.org/)
* A Google Cloud project with the Vision API enabled
  * [Quickstart Guide](https://cloud.google.com/vision/docs/setup)
* [gcloud CLI](https://cloud.google.com/sdk/docs/install)
  * Ensure the following commands run successfully in a terminal after installation:
    1. `gcloud config get-value project`
    2. `gcloud auth print-access-token`

Installation
-------------
1. Clone the repo
    ```commandline
    git clone https://github.com/atcosner/ku-bi-form-processor.git
    ```
2. Open a terminal and change into the `ku-bi-form-processor` directory
    ```commandline
    cd ku-bi-form-processor
    ```
3. Create a Python virtual environment for the project
    ```commandline
    python3 -m venv .venv
    ```
4. Install the required packages via pip
    ```commandline
    python3 -m pip install -r requirements.txt
    ```

Usage
-----
1. Open a terminal and change into the `ku-bi-form-processor` directory
    ```commandline
    cd ku-bi-form-processor
    ```
2. Activate the virtual environment in your terminal
   * Command Prompt: `.venv\Scripts\activate.bat`
   * PowerShell: `.venv\Scripts\Activate.ps1`
3. Start the webserver with the following command
    ```commandline
    python3 main.py
    ```
4. Navigate to the web application with the following URL
   * http://127.0.0.1:5000

Modifying/Extending This Project
-------------------------------
This project was designed to be modified to support additional types of forms and fields depending on what users at
other collections may need. This process involves writing Python which can be learned from a multitude of online
resources including this [tutorial](https://docs.python.org/3/tutorial/index.html) from the Python developers themselves.

### Adding Additional Field Types
1. Define a new field in `src/definitions/base_fields.py` by deriving from `BaseField`
   * Use the existing fields as examples for how to structure the new field.
2. Define the corresponding processed field in `src/definitions/processed_fields.py` by deriving from `ProcessedField`
   * Ensure you define the required `export()`, `validate()`, and `handle_form_update()` functions
3. Add functions in `src/processing.py` to handle creating a `ProcessedField` from your `BaseField`

### Adding Additional Reference Forms
1. Create a new file under `src/defintions` with name that matches the reference form
2. Define all supported fields in the new file
   * Support for multiple copies of the form on a single page can be seen in `src/definitions/ornithology_form_v8.py`
   * Ensure that `BoxBounds` in your fields are slightly smaller than the field itself to help with OCR
3. Create an entry in the `SUPPORTED_FORMS` list in `src/definitions/forms.py` to finalize the form
4. The form should now be selectable on the `Create Job` webpage

### Adding Additional Validators
1. Create a new file under `src/validation` or append to one of the exiting files
   * The files are grouped and named based on the type of field data they need to validate (e.g. text vs checkboxes)
2. Define both the `validate()` and `export()` functions for the new validator
3. Apply it to a `BaseField` in a reference form definition (e.g. `src/definitions/test_form_v1.py`)

### Adding New Export Formats
Currently only exporting to an Excel workbook is supported but this can easily be extended to export the form data in
other formats. The design of the `ProcessedField.export()` function is that it returns a `dict[str, str]` which
represents the columns (dictionary key) and row values (dictionary values) this field wants to export. This data is
built up into a `pandas.DataFrame` by `export_results()` in `src/job.py`. The dataframe then could easily be exported to
any output format.


Attributions
------------
* <a href="https://www.flaticon.com/authors/alfredo-hernandez">Icons created by Alfredo Hernandez - Flaticon</a>


Acknowledgements
---------------
This project would not have been possible without the support of the staff of the [KU Biodiversity Institute](https://biodiversity.ku.edu/)
with special thanks to the following people:
* [Abby Perkins - KU Ornithology Graduate Student](https://github.com/abbycperkins)
* [Lucas DeCicco - KU Ornithology Collections Manager](https://www.lhdecicco.com/)
