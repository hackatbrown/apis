from functools import wraps
from flask import jsonify, render_template, url_for, request, redirect
from flask import send_from_directory
from api import app, db, requires_auth, make_json_error
from api.scripts.stats import get_total_requests
from api.forms import SignupForm, DocumentationForm, MemberForm
from flask import Markup
import markdown
from datetime import datetime
import os

'''
DATABASE OBJECTS: View templates on the private, repository README.
'''

# simplify collection names
clients = db.clients
api_documentations = db['api_documentations']
members = db['members']

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico')


@app.route('/')
def root():
    # num_requests = get_total_requests()
    return render_template('home.html', 
            api_documentations=list(api_documentations.find().sort("_id",1)))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        return redirect(url_for('root', signedup='true'))
    return render_template('signup.html', form=form, active="signup",
            api_documentations=list(api_documentations.find().sort("_id",1)))

@app.route('/docs', methods=['GET'])
def docs():
    return redirect('https://api.students.brown.edu/docs/getting-started') #TODO: Fix this part to use url_for

@app.route('/docs/<docName>', methods=['GET'])
def docs_for(docName="getting-started"):
    api_documentation=api_documentations.find_one({'urlname': docName})
    name=api_documentation['name']
    contents=api_documentation['contents']
    contents=Markup(markdown.markdown(contents))
    return render_template('documentation_template.html',
            api_documentations=list(api_documentations.find().sort("_id",1)),
            name=name, contents=contents, active="docs")

@app.route('/about-us', methods=['GET'])
def about_us():
    return render_template('about-us.html',
            api_documentations=list(api_documentations.find().sort("_id",1)),
            active="about", members=members.find().sort("name",1))

@app.route('/github', methods=['GET'])
def github():
    return redirect('https://github.com/hackatbrown/apis')

@app.route('/contribute', methods=['GET'])
def contribute():
    # TODO: Get rid of inline documentation, this is very bad...
    contents='The future of Brown APIs depends on you! All of our code is open source, and we rely heavily on contributions from the Brown community. You can view our code (along with open issues and future plans) [on Github](https://github.com/hackatbrown/apis).\r\n\r\n## How to Help\r\n\r\nThere are many ways to help further the development of Brown APIs. You can add new APIs, maintain and enhance current APIs, fix bugs, improve this website, or build better tools to help others contribute. Check the [issues](https://github.com/hackatbrown/apis/issues) on our Github for suggestions of what to do first. You don\'t need to be able to code to help either. Reach out to CIS and other university organizations to get easier and wider access to campus data.\r\n\r\n## General Development Information\r\n\r\nThe APIs are written in Python and run on a [Flask](http://flask.pocoo.org) server. This website is also served by the same server and uses [Jinja](http://jinja.pocoo.org) templates with the [Bootstrap](http://getbootstrap.com) framework.\r\n\r\nData is stored in a single [MongoDB](https://docs.mongodb.com/getting-started/python/introduction/) database hosted on [mLab.com](https://mlab.com/) (_Note: This was probably a bad decision that could really use some contributions to fix!_). Because there is only one copy of the database, developers must take care to avoid corrupting the data while testing fixes or new features.\r\n\r\n## Getting Started\r\n\r\nYou\'ll need the latest version of Python 3, along with `virtualenv` and `pip`. Go ahead and look up these programs if you aren\'t familiar with them. They\'re crucial to our development process.\r\n\r\n1. Clone this repository to your own machine:\r\n    - `git clone https://github.com/hackatbrown/brown-apis.git`\r\n2. Open a terminal and navigate to the top level of the repository (_brown-apis/_).\r\n3. Create and activate a virtual environment (again, look up `virtualenv` online to understand what this does):\r\n    - ``virtualenv -p `which python3` venv``\r\n    - `source venv/bin/activate`\r\n4. Install all the required libraries in your virtual environment:\r\n    - `pip install -r requirements.txt`\r\n5. Create a new branch for your changes. For example (while on the master branch):\r\n    - `git checkout -b <descriptive-branch-name>`\r\n6. Make any changes you want to make.\r\n7. Commit your changes, push them to `origin/<branch-name>`, and open a new pull request.\r\n8. To test your code, you may merge them into the `stage` branch. These changes will be automatically reflected on our [staging server](http://brown-apis-staging.herokuapp.com/). You can merge changes from the develop branch into the staging branch with:\r\n    - `git checkout stage`\r\n    - `git fetch origin`\r\n    - `git reset --hard origin/master`\r\n    - `git rebase <your-branch-name>`\r\n    - `git push --force`\r\n    - Note: This won\'t work if multiple developers are doing this at the same time.\r\n9. You\'re code will be merged into `master` once your pull request is accepted.\r\n\r\n#### How to Run Scripts\r\n\r\n1. Navigate to the top-level directory (_brown-apis/_).\r\n2. Run the script from a package environment, allowing it to import the database from the _api_ package:\r\n    - `python3 -m api.scripts.<scriptname>` where \'scriptname\' does NOT include the \'.py\' extension.\r\n3. You can include any script arguments after the command (just like you normally would).\r\n\r\n## Data Structures\r\n\r\nWe use MongoDB to store various menus and schedules, as well as client information. In MongoDB, all objects are stored as JSON, and there is no schema that forces all objects in a collection to share the same fields. Thus, we keep documentation of the different collections here (and in the API overviews below) to encourage an implicit schema. Objects added to the database should follow these templates. If you add a new collection to the database, remember to add a template here, too.\r\n\r\n#### db.clients ####\r\n\r\n- *username*: &lt;STRING&gt;,\r\n- *client_email*: &lt;STRING&gt;,\r\n- *client_id*: &lt;STRING&gt;,\r\n- *valid*: &lt;BOOLEAN&gt;, **<-- can this client make requests?**\r\n- *joined*: &lt;DATETIME&gt;, **<-- when did this client register?**\r\n- *requests*: &lt;INTEGER&gt; **<-- total number of requests made by this client (not included until this client makes their first request)**\r\n- *activity*: **list of activity objects which take the form:**\r\n   * _timestamp_: &lt;DATETIME&gt;, **<-- time of request**\r\n    * _endpoint_: &lt;STRING&gt; **<-- endpoint of request**\r\n- **DEPRECATED:** *client_name*: &lt;STRING&gt; **<-- replaced with _username_**\r\n\r\n#### db.api_documentations ####\r\n- *urlname*: &lt;STRING&gt;\r\n- *name*: &lt;STRING&gt;\r\n- *contents*: &lt;STRING&gt;\r\n- *imageurl*: &lt;IMAGE&gt;\r\n\r\n\r\n## High Level API Overviews\r\n\r\n### Dining\r\n\r\nThe Dining API is updated every day by a scraper that parses the menus from Brown Dining Services\' website. The hours for each eatery are entered manually inside of the scraper script before each semester. When the scraper is run, all this data is stored in the database. Calls to the API trigger various queries to the database and fetch the scraped data.\r\n\r\n#### db.dining\_menus\r\n\r\n- *eatery*: &lt;STRING&gt;,\r\n- *year*: &lt;INTEGER&gt;,\r\n- *month*: &lt;INTEGER&gt;,\r\n- *day*: &lt;INTEGER&gt;,\r\n- *start_hour*: &lt;INTEGER&gt;,    **<-- these four lines describe a menu\'s start/end times**\r\n- *start_minute*: &lt;INTEGER&gt;, \r\n- *end_hour*: &lt;INTEGER&gt;, \r\n- *end_minute*: &lt;INTEGER&gt;,\r\n- *meal*: &lt;STRING&gt;,\r\n- *food*: [ &lt;STRING&gt;, &lt;STRING&gt;, ... ]  **<-- list of all food items on menu**\r\n- *&lt;section&gt;*: [ &lt;STRING&gt;, &lt;STRING&gt;, ... ],  **<-- category (e.g. "Bistro") mapped to list of food items**\r\n- ... (there can be multiple sections per menu)\r\n\r\n#### db.dining\_hours\r\n\r\n- *eatery*: &lt;STRING&gt;,\r\n- *year*: &lt;INTEGER&gt;,\r\n- *month*: &lt;INTEGER&gt;,\r\n- *day*: &lt;INTEGER&gt;,\r\n- *open_hour*: &lt;INTEGER&gt;,\r\n- *open_minute*: &lt;INTEGER&gt;, \r\n- *close_hour*: &lt;INTEGER&gt;, \r\n- *close_minute*: &lt;INTEGER&gt;\r\n\r\n#### db.dining\_all\_foods\r\n\r\n- *eatery*: &lt;STRING&gt;,\r\n- *food*: [ &lt;STRING&gt;, &lt;STRING&gt;, ... ]\r\n\r\n### WiFi\r\n\r\nThe WiFi API just forwards requests to another API run by Brown CIS. Their API is protected by a password (HTTP Basic Auth) and is nearly identical to the WiFi API that we expose. The response from the CIS API is returned back to the client.\r\n\r\n### Laundry\r\n\r\nThe Laundry API is updated manually with a scraper that pulls all the laundry rooms and stores them in the database. When a request is received, the API checks the request against the list of rooms in the database and optionally retrieves status information by scraping the laundry website in realtime.\r\n\r\n#### db.laundry\r\n- *room*\r\n    - *name*: &lt;STRING&gt;\r\n    - *id*: &lt;INT&gt;\r\n    - *machines*: list of objects with:\r\n        - *id*: &lt;INT&gt;\r\n        - *type*: &lt;STRING&gt; (one of `washFL`, `washNdry`, `dry`)\r\n\r\n### Academic\r\n\r\nThe Academic API used to scrape course information from Banner and store it in the database. Since Banner has been deprecated for course selection, the Academic API scraper has stopped working, and we are no longer able to collect course data. Thus, the Academic API is unavailable for the foreseeable future. Contributions are especially welcome here.'
    contents=Markup(markdown.markdown(contents))
    return render_template('documentation_template.html',
            api_documentations=list(api_documentations.find().sort("_id",1)),
            name='How to Contribute', contents=contents)

@app.route('/admin/add-documentation', methods=['GET', 'POST'])
@requires_auth
def add_documentation():
    form = DocumentationForm()
    if form.validate_on_submit():
        return redirect(url_for('root'))
    return render_template('add_documentation.html', form=form,
            api_documentations=list(api_documentations.find().sort("_id",1)))

@app.route('/admin/add-member', methods=['GET', 'POST'])
@requires_auth
def add_member():
    form = MemberForm()
    if form.validate_on_submit():
        return redirect(url_for('root'))
    return render_template('add_member.html', form=form,
            api_documentations=list(api_documentations.find().sort("_id",1)))

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
