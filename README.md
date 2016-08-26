Brown University APIs
=====================

_This README is for development of the APIs. Public documentation is located [here](http://api.students.brown.edu)._

**DO NOT PUSH DIRECTLY TO MASTER UNLESS YOU INTEND TO DEPLOY A NEW VERSION OF THE SITE. THE SITE AND ALL APIS IS CONTINUOUSLY REDEPLOYED WHEN THE MASTER BRANCH IS UPDATED.**


Before Getting Started
------------

You'll need the latest version of Python 3, along with `virtualenv` and `pip`. Go ahead and look up these programs if you aren't familiar with them. They're crucial to our development process.

Getting Started on Development
------------------------------

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
	- `git rebase -i <your-branch-name>`
	- `git push`
	- Note: This won't work if multiple developers are doing this at the same time.
9. You're code will be merged into `master` once your pull request is accepted.

How to Manually Run Scripts
---------------------------

1. Navigate to the top-level directory (_brown-apis/_).
2. Run the script from a package environment, allowing it to import the database from the _api_ package:
	- `python3 -m api.scripts.<scriptname>` where 'scriptname' does NOT include the '.py' extension.
3. You can include any script arguments after the command (just like you normally would).

Data Structures
---------------

We use MongoDB to store various menus and schedules, as well as client information. In MongoDB, all objects are stored as JSON, and there is no schema that forces all objects in a collection to share the same fields. Thus, we keep documentation of the different collections here to encourage an implicit schema. All objects added to the database should follow these templates. If you add a new collection to the database, remember to add a template here, too.

### db.clients ###

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

### db.api_documentations ###
- *urlname*: &lt;STRING&gt;
- *name*: &lt;STRING&gt;
- *contents*: &lt;STRING&gt;
- *imageurl*: &lt;IMAGE&gt;

### db.members ###
- *name*: &lt;STRING&gt;
- *image_url*: &lt;STRING&gt;
- *about*: &lt;STRING&gt;

### db.dining\_menus ###

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

### db.dining\_hours ###

- *eatery*: &lt;STRING&gt;,
- *year*: &lt;INTEGER&gt;,
- *month*: &lt;INTEGER&gt;,
- *day*: &lt;INTEGER&gt;,
- *open_hour*: &lt;INTEGER&gt;,
- *open_minute*: &lt;INTEGER&gt;, 
- *close_hour*: &lt;INTEGER&gt;, 
- *close_minute*: &lt;INTEGER&gt;

### db.dining\_all\_foods ###

- *eatery*: &lt;STRING&gt;,
- *food*: [ &lt;STRING&gt;, &lt;STRING&gt;, ... ]


### db.laundry ###
- *room*
    - *name*: &lt;STRING&gt;
    - *id*: &lt;INT&gt;
    - *machines*: list of objects with:
        - *id*: &lt;INT&gt;
        - *type*: &lt;STRING&gt; (one of `washFL`, `washNdry`, `dry`)
