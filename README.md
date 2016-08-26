Brown APIs
=====================

_This README is for development of the APIs. Public documentation is located [here](http://api.students.brown.edu)._

**DO NOT PUSH DIRECTLY TO MASTER UNLESS YOU INTEND TO DEPLOY A NEW VERSION OF THE SITE. THE SITE AND ALL APIS IS CONTINUOUSLY REDEPLOYED WHEN THE MASTER BRANCH IS UPDATED.**

_NOTE: At all times, the following should match the [contributions page](http://api.students.brown.edu/contribute) on our website (so update both simultaneously)!_

The future of Brown APIs depends on you! All of our code is open source, and we rely heavily on contributions from the Brown community. You can view our code (along with open issues and future plans) [on Github](https://github.com/hackatbrown/apis).

## How to Help

There are many ways to help further the development of Brown APIs. You can add new APIs, maintain and enhance current APIs, fix bugs, improve this website, or build better tools to help others contribute. Check the [issues](https://github.com/hackatbrown/apis/issues) on our Github for suggestions of what to do first. You don't need to be able to code to help either. Reach out to CIS and other university organizations to get easier and wider access to campus data.

## General Development Information

The APIs are written in Python and run on a [Flask](http://flask.pocoo.org) server. This website is also served by the same server and uses [Jinja](http://jinja.pocoo.org) templates with the [Bootstrap](http://getbootstrap.com) framework.

Data is stored in a single [MongoDB](https://docs.mongodb.com/getting-started/python/introduction/) database hosted on [mLab.com](https://mlab.com/) (_Note: This was probably a bad decision that could really use some contributions to fix!_). Because there is only one copy of the database, developers must take care to avoid corrupting the data while testing fixes or new features.

## Getting Started

You'll need the latest version of Python 3, along with `virtualenv` and `pip`. Go ahead and look up these programs if you aren't familiar with them. They're crucial to our development process.

1. Clone this repository to your own machine:
	- `git clone https://github.com/hackatbrown/brown-apis.git`
2. Open a terminal and navigate to the top level of the repository (_brown-apis/_).
3. Create and activate a virtual environment (again, look up `virtualenv` online to understand what this does):
	- ``virtualenv -p `which python3` venv``
	- `source venv/bin/activate`
4. Install all the required libraries in your virtual environment:
	- `pip install -r requirements.txt`
5. Create a new branch for your changes. For example (while on the master branch):
	- `git checkout -b <descriptive-branch-name>`
6. Make any changes you want to make.
7. Commit your changes, push them to `origin/<branch-name>`, and open a new pull request.
8. To test your code, you may merge them into the `stage` branch. These changes will be automatically reflected on our [staging server](http://brown-apis-staging.herokuapp.com/). You can merge changes from the develop branch into the staging branch with:
	- `git checkout stage`
	- `git fetch origin`
	- `git reset --hard origin/master`
	- `git rebase <your-branch-name>`
	- `git push --force`
	- Note: This won't work if multiple developers are doing this at the same time.
9. You're code will be merged into `master` once your pull request is accepted.

#### How to Run Scripts

1. Navigate to the top-level directory (_brown-apis/_).
2. Run the script from a package environment, allowing it to import the database from the _api_ package:
	- `python3 -m api.scripts.<scriptname>` where 'scriptname' does NOT include the '.py' extension.
3. You can include any script arguments after the command (just like you normally would).

## Data Structures

We use MongoDB to store various menus and schedules, as well as client information. In MongoDB, all objects are stored as JSON, and there is no schema that forces all objects in a collection to share the same fields. Thus, we keep documentation of the different collections here (and in the API overviews below) to encourage an implicit schema. Objects added to the database should follow these templates. If you add a new collection to the database, remember to add a template here, too.

#### db.clients ####

- *username*: &lt;STRING&gt;,
- *client_email*: &lt;STRING&gt;,
- *client_id*: &lt;STRING&gt;,
- *valid*: &lt;BOOLEAN&gt;, **<-- can this client make requests?**
- *joined*: &lt;DATETIME&gt;, **<-- when did this client register?**
- *requests*: &lt;INTEGER&gt; **<-- total number of requests made by this client (not included until this client makes their first request)**
- *activity*: **list of activity objects which take the form:**
	* _timestamp_: &lt;DATETIME&gt;, **<-- time of request**
	* _endpoint_: &lt;STRING&gt; **<-- endpoint of request**
- **DEPRECATED:** *client_name*: &lt;STRING&gt; **<-- replaced with _username_**

#### db.api_documentations ####
- *urlname*: &lt;STRING&gt;
- *name*: &lt;STRING&gt;
- *contents*: &lt;STRING&gt;
- *imageurl*: &lt;IMAGE&gt;


## High Level API Overviews

### Dining

The Dining API is updated every day by a scraper that parses the menus from Brown Dining Services' website. The hours for each eatery are entered manually inside of the scraper script before each semester. When the scraper is run, all this data is stored in the database. Calls to the API trigger various queries to the database and fetch the scraped data.

#### db.dining\_menus

- *eatery*: &lt;STRING&gt;,
- *year*: &lt;INTEGER&gt;,
- *month*: &lt;INTEGER&gt;,
- *day*: &lt;INTEGER&gt;,
- *start_hour*: &lt;INTEGER&gt;, 	**<-- these four lines describe a menu's start/end times**
- *start_minute*: &lt;INTEGER&gt;, 
- *end_hour*: &lt;INTEGER&gt;, 
- *end_minute*: &lt;INTEGER&gt;,
- *meal*: &lt;STRING&gt;,
- *food*: [ &lt;STRING&gt;, &lt;STRING&gt;, ... ]  **<-- list of all food items on menu**
- *&lt;section&gt;*: [ &lt;STRING&gt;, &lt;STRING&gt;, ... ],  **<-- category (e.g. "Bistro") mapped to list of food items**
- ... (there can be multiple sections per menu)

#### db.dining\_hours

- *eatery*: &lt;STRING&gt;,
- *year*: &lt;INTEGER&gt;,
- *month*: &lt;INTEGER&gt;,
- *day*: &lt;INTEGER&gt;,
- *open_hour*: &lt;INTEGER&gt;,
- *open_minute*: &lt;INTEGER&gt;, 
- *close_hour*: &lt;INTEGER&gt;, 
- *close_minute*: &lt;INTEGER&gt;

#### db.dining\_all\_foods

- *eatery*: &lt;STRING&gt;,
- *food*: [ &lt;STRING&gt;, &lt;STRING&gt;, ... ]

### WiFi

The WiFi API just forwards requests to another API run by Brown CIS. Their API is protected by a password (HTTP Basic Auth) and is nearly identical to the WiFi API that we expose. The response from the CIS API is returned back to the client.

### Laundry

The Laundry API is updated manually with a scraper that pulls all the laundry rooms and stores them in the database. When a request is received, the API checks the request against the list of rooms in the database and optionally retrieves status information by scraping the laundry website in realtime.

#### db.laundry
- *room*
    - *name*: &lt;STRING&gt;
    - *id*: &lt;INT&gt;
    - *machines*: list of objects with:
        - *id*: &lt;INT&gt;
        - *type*: &lt;STRING&gt; (one of `washFL`, `washNdry`, `dry`)

### Academic

The Academic API used to scrape course information from Banner and store it in the database. Since Banner has been deprecated for course selection, the Academic API scraper has stopped working, and we are no longer able to collect course data. Thus, the Academic API is unavailable for the foreseeable future. Contributions are especially welcome here.
