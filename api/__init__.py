from flask import Flask
import pymongo
import os

app = Flask(__name__)

if 'MONGO_URI' in os.environ:
	db = pymongo.MongoClient(os.environ['MONGO_URI']).brown
else:
	print "The database URI's environment variable was not found."

import dining
