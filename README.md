<h1 align="center"><img src="/webserver/static/images/ku_bi_logo.jpg"></h1>

KU BI Collection Form Processor
===============================

This project was created for the  [University of Kansas Biodiversity Institute](https://biodiversity.ku.edu/) to allow for the automatic OCR and digitization of paper collection forms.
While testing and development was done for specific KU collection forms this project was designed to allow for the addition of other form templates.

Optical Character Recognition is supported by the [Google Vision API](https://cloud.google.com/vision?hl=en) but swapping for other handwriting recognition models is possible.

Requirements
-------------
* [Python 3.12](https://www.python.org/)
* A Google Cloud project with the Vision API enabled
  * [Quickstart Guide](https://cloud.google.com/vision/docs/setup)
* [gcloud CLI](https://cloud.google.com/sdk/docs/install)
  * Ensure the following commands return successfully after the installation:
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

Additional Form Support
-----------------------

Attributions
------------
