from flask import Flask, render_template

app = Flask(__name__, static_folder='static/')


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True, host='127.0.0.1')
