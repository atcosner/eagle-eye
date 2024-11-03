import os

from .util import set_up_root_logger
from .webserver import app

debug_mode = False
if 'EAGLE_EYE_DEV' in os.environ:
    debug_mode = True
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True

set_up_root_logger(debug_mode)
app.run(debug=debug_mode, host='127.0.0.1')
