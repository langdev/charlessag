
from flask import Flask
app = Flask(__name__)

from functools import wraps
from flask import render_template
from flask import request, Response

import database
import auth

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="#langdev charles\' sag"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        req_auth = request.authorization
        if not req_auth or\
            not auth.http_auth(req_auth.username, req_auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

@app.before_request
def before_request():
    pass

@app.route('/')
@requires_auth
def index():
    
    return render_template('base.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7111, debug=True)
