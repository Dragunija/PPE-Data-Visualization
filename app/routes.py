from app import app, mongo
from flask import render_template, request
from werkzeug import secure_filename
from app import hepmcio_json
from app import hepmcio
import os
import json
import io

@app.route('/')
@app.route('/index')
def index():
	return render_template("index.html", title="Home")

@app.route('/upload')
def upload():
	return render_template("upload.html", title="Upload a file")

@app.route('/uploader', methods=['GET', 'POST'])
def uploader():
	if request.method == 'POST':
		File = request.files['file']
		filename = secure_filename(File.filename)
		string_stream = io.StringIO(File.read().decode('utf-8'))
		event = hepmcio.HepMCReader(string_stream).next()
		jsonified = hepmcio_json.encodeEvent(event)
		jsonDecoder = json.JSONDecoder()
		jsonEvent = jsonDecoder.decode(jsonified[0])
		jsonParticles = [jsonDecoder.decode(p) for p in jsonified[1]]
		jsonVertices = [jsonDecoder.decode(v) for v in jsonified[2]]
		mongo.db.filename.insert_one(jsonEvent)
		mongo.db.filename.insert_many(jsonParticles)
		mongo.db.filename.insert_many(jsonVertices)
		
		return str(jsonEvent)


@app.route("/visualiser/<string:filename>")
def visualiser(filename):
	
	
	return render_template("visualiser.html", title="Visualiser")
	
