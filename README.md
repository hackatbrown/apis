Brown University APIs
=====================

_This README is for development of the APIs. Public documentation is located [here](http://api.students.brown.edu)._

**DO NOT PUSH DIRECTLY TO MASTER UNLESS YOU INTEND TO DEPLOY A NEW VERSION OF THE SITE. YOU COULD BREAK EVERYTHING!**


Getting Started on Development
------------------------------

1. Clone this repository to your own machine:
	- `git clone https://github.com/hackatbrown/brown-apis.git`
2. If you don't have 'pip' installed, install 'pip' (find instructions online).
3. Also, make sure you have 'virtualenv' installed (find instructions online).
4. Open a terminal and navigate to the top level of the reposity (_brown-apis/_).
5. Create and activate a virtual environment:
	- `virtualenv venv`
	- `source venv/bin/activate`
6. Install all the required libraries in your virtual environment:
	- `pip install -r requirements.txt`
7. Change to your feature's branch with Git. For example:
	- `git checkout feature/courses`
	- Or, if your feature's branch does not exist yet: `git checkout -b feature/<name>`
8. Edit any necessary files with whichever editor you prefer.
9. Commit your changes:
	- `git add --all`
	- `git commit -m "Some informative message your changes"`
	- `git push origin feature/<name>` or just `git push`
10. To test your code, you may merge them into the `stage` branch. These changes will be automatically reflected on our [staging server](http://brown-apis-staging.herokuapp.com/). You can merge changes from the develop branch into the staging branch with:
	- `git checkout stage`
	- `git merge --no-ff feature/<name>`
	- Type a very brief explanation of the merge (if you can't figure out how, lookup 'Vim' online)
	- `git push`
11. Deactivate the virtual environment when you're finished developing:
	- `deactivate`

How to Manually Run Scripts
---------------------------

1. Navigate to the top-level directory (_brown-apis/_).
2. Run the script from a package environment, allowing it to import the database from the _api_ package:
	- `python -m api.scripts.<scriptname>` where 'scriptname' does NOT include the '.py' extension.
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
- *name*: &lt;STRING&lt;
- *contents*: &lt;STRING&gt;
- *image*: &lt;IMAGE&gt; Not yet implemented

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
