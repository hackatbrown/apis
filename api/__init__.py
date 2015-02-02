from flask import Flask, jsonify, request
from flask_limiter import Limiter
from werkzeug.exceptions import default_exceptions
from werkzeug.exceptions import HTTPException
import pymongo
import os

'''
    make_json_error - a wrapper for all exceptions

    All error responses that you don't specifically
    manage yourself will have application/json content
    type, and will contain JSON like this (just an example):

    { "error": "405: Method Not Allowed" }
'''
def make_json_error(ex):
    response = jsonify(error=[str(ex)])
    response.status_code = (ex.code
                            if isinstance(ex, HTTPException)
                            else 500)
    return response

app = Flask(__name__)

# override all error handlers to be 'make_json_error'
for code in default_exceptions.iterkeys():
    app.error_handler_spec[None][code] = make_json_error

if 'MONGO_URI' in os.environ:
    db = pymongo.MongoClient(os.environ['MONGO_URI']).brown
else:
    print "The database URI's environment variable was not found."

limiter = Limiter(app, global_limits=["4/second", "60/minute", "3000/hour"], key_func=lambda : request.args.get('client_id', 'missing_client'))

import meta
import dining