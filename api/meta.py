from flask import jsonify
from api import app

@app.route('/')
def root():
	return jsonify(hello='world')