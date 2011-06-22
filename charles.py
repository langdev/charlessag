
from flask import Flask
app = Flask(__name__)

from functools import wraps
import flask
from flask import render_template
from flask import redirect
from flask import url_for
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
        try:
            database.User.by(name=req_auth.username)
        except:
            user = database.User(name=req_auth.username)
            database.session.add(user)
        return f(*args, **kwargs)
    return decorated

@app.before_request
def before_request():
    pass

@app.route('/')
@requires_auth
def index():
    
    return render_template('base.html')

@app.route('/project')
@app.route('/project/+')
@app.route('/project/<name>')
@requires_auth
def project(name=''):
    if not name: name = '+'
    try:
        proj = database.Project.by(name=name)
    except:
        flask.abort(404)
    return render_template('project.html', project=proj)

@app.route('/project/<name>/add-project', methods=['POST'])
@requires_auth
def project_add_subproj(name):
    proj = database.Project.by(name=name)
    childname = request.form['name']
    child = database.Project(childname, proj.id)
    database.session.add(child)
    return redirect(url_for('project', name=childname))

@app.route('/project/<name>/add-member', methods=['POST'])
@requires_auth
def project_add_member(name):
    proj = database.Project.by(name=name)
    try:
        user = database.User.by(name=request.form['user'])
    except:
        flask.abort(400)
    member = database.Member.filter_by(project_id=proj.id, user_id=user.id)
    if member.count() > 0:
        flask.abort(400)
    membername = request.form['name']
    if not membername:
        membername = None
    member = database.Member(proj.id, user.id, membername)
    database.session.add(member)
    return redirect(url_for('project', name=name))

@app.route('/project/<name>/add-job', methods=['POST'])
@requires_auth
def project_add_job(name):
    proj = database.Project.by(name=name)
    jobname = request.form['name']
    if not jobname:
        flask.abort(400)
    job = database.Job.filter_by(project_id=proj.id, name=jobname)
    if job.count() > 0:
        flask.abort(400)
    job = database.Job(proj.id, jobname)
    database.session.add(job)
    return redirect(url_for('project', name=name))

@app.route('/user/<name>')
@requires_auth
def user(name):
    return render_template("base.html")

def user_select_form(name):
    form = '<select name="%s">' % name
    for user in database.User.all():
        form += '<option value="%s">%s</option>' % (user.name, user.name)
    form += '</select>'
    return flask.Markup(form)
app.jinja_env.globals.update(user_select_form=user_select_form)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7111, debug=True)
