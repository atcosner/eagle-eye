from pathlib import Path

FORMS_PATH = Path(__file__).parent / '..' / 'forms'
JOB_WORKING_DIR_PATH = Path(__file__).parent / '..' / '.program_data'

# Make the job working dir if it does not exist
if not JOB_WORKING_DIR_PATH.exists():
    JOB_WORKING_DIR_PATH.mkdir()
