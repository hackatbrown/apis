Brown University APIs
=====================

_This README is for development of the APIs. Public documentation is located at [here](http://api.students.brown.edu)._

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
7. Change to the `develop` branch with Git:
	- `git checkout develop`
8. Edit any necessary files with whichever editor you prefer.
9. Commit your changes:
	- `git add --all`
	- `git commit -m "Some informative message your changes"`
	- `git push origin development` or just `git push`
10. If you've _thoroughly tested_ your code, you may merge them into the `master` branch. These changes will be automatically reflected on the server. For now, Joe is the only person with access to the Heroku account (where our server is kept), so you probably shouldn't perform this step:
	- `git checkout master`
	- `git merge --no-ff develop`
11. Deactivate the virtual environment when you're finished developing:
	- `deactivate`

How to Manually Run Scripts
---------------------------

1. Navigate to the top-level directory (_brown-apis/_).
2. Run the script from a package environment, allowing it to import the database from the _api_ package:
	- `python -m api.scripts.<scriptname>` where 'scriptname' does NOT include the '.py' extension.
3. You can include any script arguments after the command (just like you normally would).