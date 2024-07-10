import uuid
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__, static_folder='static/')


@app.route('/')
def index():
    return render_template('index.html', instance_id=uuid.uuid4())


@app.route('/file-selector', methods=['GET', 'POST'])
def file_selector():
    if request.method == 'POST':
        print(request)
        print(request.form)
        if 'file' not in request.files:
            print('No file part')
            return redirect(request.url)

        print(request.files['file'])
        return redirect(url_for('index'))
    else:
        return render_template('file_selector.html')


@app.route('/file-upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        print(request)
        print(request.form)
        if 'file' not in request.files:
            print('No file part')
            return redirect(url_for('index'))

        print(request.files['file'])
        return redirect(url_for('index'))

    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''


if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True, host='127.0.0.1')
