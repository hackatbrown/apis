from functools import wraps
from flask import jsonify, render_template, url_for, request, redirect
from flask import send_from_directory
from api import app, db, requires_auth
from api.scripts.stats import get_total_requests
from api.forms import SignupForm, DocumentationForm
from flask import Markup
import markdown

'''
DATABASE OBJECTS: View templates on the private, repository README.
'''

# simplify collection names
clients = db.clients
api_documentations = db['api_documentations']
members = db['members']

# Messages for success/failure during Client ID signup
SUCCESS_MSG = "Your Client ID has been emailed to you!"
FAILURE_MSG = ("Your request could not be processed. "
               "Please email 'joseph_engelman@brown.edu' for "
               "manual registration.")

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico')


@app.route('/')
def root():
    # num_requests = get_total_requests()
    return render_template('home.html', 
            api_documentations=list(api_documentations.find()))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        return redirect(url_for('root', signedup='true'))
    return render_template('signup.html', form=form, active="signup",
            api_documentations=api_documentations.find())

@app.route('/docs', methods=['GET'])
def docs():
    return redirect('/docs/getting-started') #TODO: Fix this part to use url_for

@app.route('/docs/<docName>', methods=['GET'])
def docs_for(docName="getting-started"):
    api_documentation=api_documentations.find_one({'urlname': docName})
    name=api_documentation['name']
    contents=api_documentation['contents']
    contents=Markup(markdown.markdown(contents))
    return render_template('documentation_template.html',
            api_documentations=list(api_documentations.find()),
            name=name, contents=contents, active="docs")

@app.route('/about-us', methods=['GET', 'POST'])
def about_us():
    return render_template('about-us.html',
            api_documentations=list(api_documentations.find()),
            active="about", members=members.find())

@app.route('/admin/add-documentation', methods=['GET', 'POST'])
@requires_auth
def add_documentation():
    form = DocumentationForm()
    if form.validate_on_submit():
        return redirect(url_for('root'))
    return render_template('add_documentation.html', form=form)


# Static responses

INVALID_CLIENT_MSG = "invalid client id"


# Helper methods

def is_valid_client(client_id):
    ''' Return True if client ID is valid, False otherwise '''
    if client_id == 'missing_client':
        # requests without a client_id should default to 'missing_client'
        return False

    client = clients.find_one({'client_id': client_id})
    if client and 'valid' in client and client['valid']:
        # client exists in database and is marked as valid
        return True
    print("Client ID", client_id, "not found in client collection")
    return False


def log_client(client_id, endpoint, timestamp):
    ''' Log a client's activity with the time of occurence
        Return True if successfully logged, otherwise False
    '''
    result = clients.update(
        {'client_id': client_id},
        {
            '$inc': {'requests': 1},
            '$push': {
                'activity': {
                    'endpoint': endpoint,
                    'timestamp': timestamp
                }
            }
        })
    if u'nModified' in result and result[u'nModified'] == 1:
        return True
    print("Bad result from log_client: ", result)
    return False


def invalidate_client(client_id):
    ''' Invalidate a client, revoking future access
        Return True if client's access mode was modified to False, or
            return False if client's access mode was already False or
            the operation was unsuccessful
    '''
    result = clients.update({'client_id': client_id},
                            {'$set': {'valid': False}})
    if u'nModified' in result and result[u'nModified'] == 1:
        return True
    return False


def validate_client(client_id):
    ''' Validate a client, enabling future access
        Return True if client's access mode was modified to True, or
            return False if client's access mode was already True or
            the operation was unsuccessful
    '''
    result = clients.update({'client_id': client_id},
                            {'$set': {'valid': True}})
    if u'nModified' in result and result[u'nModified'] == 1:
        return True
    return False


class require_client_id(object):
    ''' Wraps view functions to require valid client IDs.
        Must be included *after* the app.route decorator.
        Optionally takes a custom endpoint string to log on success.'''
    def __init__(self, endpoint=None):
        self.endpoint = endpoint

    def __call__(self, f):
        @wraps(f)
        def wrapper_fn(*args, **kwargs):
            ep = self.endpoint
            if ep is None:
                ep = str(request.url_rule)

            client_id = request.args.get('client_id', 'missing_client')
            if is_valid_client(client_id):
                log_client(client_id, ep, str(datetime.now()))
                return f(*args, **kwargs)
            else:
                return make_json_error(INVALID_CLIENT_MSG)

        return wrapper_fn
