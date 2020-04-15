import requests
import json

from flask import Flask
# from flask import Blueprint
# from flask import flash
# from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for


app = Flask(__name__)
app.secret_key = b'mWW!XTo*D%87b2Ig'


# postapi_host = os.environ.get('POSTAPI_HOST', 'localhost')
# postapi_port = os.environ.get('POSTAPI_PORT', '8082')

# userapi_host = os.environ.get('POSTAPI_HOST', 'localhost')
# userapi_port = os.environ.get('POSTAPI_PORT', '8081')
# app.config["BASE_URI"] = 'http://{}:{}/api'.format(
#     postapi_host, postapi_port)

app.config["POST_BASE_URI"] = 'http://localhost:8082/api'
app.config["USER_BASE_URI"] = 'http://localhost:8081/api'


@app.route('/')
def index():
    """ Retrieve a list of latest messages via the backend API order by creation date"""

    url = '{}/posts'.format(app.config["POST_BASE_URI"])
    response = requests.get(url, timeout=3)

    app.logger.info('Get %s with response status code %s',
                    url, response.status_code)
    # app.logger.info('Get %s with response text %s', url, response.text)

    posts = json.loads(response.text)['data']

    # TODO pagination
    return render_template('index.html', posts=posts)


@app.route('/home')
def home():
    """ List all the posts of the user """
    if 'username' in session:

        user_id = session['user_id']
        url = '{}/userposts/{}'.format(app.config["POST_BASE_URI"], user_id)
        response = requests.get(url, timeout=3)
        # app.logger.info('Get %s with response status code %s',
        #                 url, response.status_code)
        # app.logger.info('Get %s with response text %s', url, response.text)
        posts = json.loads(response.text)['data']

        return render_template('home.html', posts=posts)

    return render_template('login.html')


@app.route('/post', methods=['GET', 'POST'])
def post():
    """ Create a Post, and refresh the current home page"""
    if request.method == 'POST':
        if 'username' not in session:
            return render_template('login.html')

        message = request.form['message']
        username = session['username']
        user_id = session['user_id']

        # Use backend post api - Post
        body = {'user_id': user_id, 'username': username, 'message': message}
        url = '{}/posts'.format(app.config["POST_BASE_URI"])
        response = requests.post(url=url,
                                 json=body,
                                 headers={'content-type': 'application/json'},
                                 timeout=3)

        app.logger.info('Get %s with response status code %s',
                        url, response.status_code)
        app.logger.info('Get %s with response text %s', url, response.text)

        return redirect(url_for('home'))
    return render_template('login.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """ Verify the login info,
    if login sucessful, return to home page.
    else return error message
    """

    msg = ''

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        app.logger.info('Login Username %s', username)
        app.logger.info('Login Password %s', username)

        # Use User API to verify the login info
        body = {'username': username, 'password': password}
        url = '{}/auth'.format(app.config["USER_BASE_URI"])
        response = requests.post(url=url,
                                 json=body,
                                 headers={'content-type': 'application/json'},
                                 timeout=3)

        app.logger.info('Get %s with response status code %s',
                        url, response.status_code)
        app.logger.info('Get %s with response text %s', url, response.text)

        # Login successful, add session info
        if response.status_code == 200:

            profile = json.loads(response.text)['data']
            app.logger.info('Returned profile %s', profile)

            session['username'] = username
            session['user_id'] = profile['user_id']
            session['profile'] = profile

            return redirect(url_for('home'))

        else:
            msg = 'Invalid username or password'

    return render_template('login.html', msg=msg)


@app.route('/logout')
def logout():
    """Clear the current session."""
    session.clear()
    return redirect(url_for("index"))


@app.route('/register', methods=['GET', 'POST'])
def register():
    """ Use backend User api to create an user account. """
    msg = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        app.logger.info('Register Username %s', username)
        app.logger.info('Register Password %s', username)

        body = {'username': username, 'password': password}
        url = '{}/user'.format(app.config["USER_BASE_URI"])
        response = requests.post(url=url,
                                 json=body,
                                 headers={'content-type': 'application/json'},
                                 timeout=3)

        app.logger.info('Register response %s', response)
        app.logger.info('Register response status code %s',
                        response.status_code)
        app.logger.info('Register response text %s', response.text)

        msg = json.loads(response.text)['message']
        app.logger.info('Register response message %s', msg)

        # If regiestered successfull, return to login page
        if response.status_code == 201:
            return redirect(url_for('login'))

    return render_template('register.html', msg=msg)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
