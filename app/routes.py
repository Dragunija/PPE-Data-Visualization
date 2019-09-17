from app import app, mongo
from flask import render_template, request, redirect
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
		
		if "file" not in request.files:
			return "No data in file."

		File = request.files['file']
		
		if File.filename == "":
			return "No file selected."
		
		filename, ext = secure_filename(File.filename).split('.')
		#Check if file stream exists and file tpye correct.
		if File and ext == "hepmc":
			#The file is a byte stream by default which is not compatible with the current version of hepmcio.
			string_stream = io.StringIO(File.read().decode('utf-8'))

			events = hepmcio.HepMCReader(string_stream).all_events()
			jsonified = [hepmcio_json.encodeEvent(event) for event in events]

			#Each collection contains all the data in a file.
			if filename not in mongo.db.collection_names():
				collection = mongo.db[filename]
				jsonDecoder = json.JSONDecoder()

				for dataTuple in jsonified:
					jsonEvent = jsonDecoder.decode(dataTuple[0])
					jsonParticles = [jsonDecoder.decode(p) for p in dataTuple[1]]
					jsonVertices = [jsonDecoder.decode(v) for v in dataTuple[2]]

					collection.insert_one(jsonEvent)
					collection.insert_many(jsonParticles)
					collection.insert_many(jsonVertices)
		
				return "Succesfully uploaded file."
			
			return "File already in database."

		return "Incorrect file type."


@app.route("/visualiser/<string:filename>/<int:view>")
def visualiser(filename, view):
	collection = mongo.db[filename]
	event = collection.find_one({"type":"event"})
	particleJson = collection.find({"type":"particle", "event":event["barcode"]}, {"_id":False})
	particles = []
	for particle in particleJson:
		particles.append(particle)
	vertices = collection.find({"type":"vertex", "event":event["barcode"]})
	return render_template("visualiser.html", title="Visualiser", event=event, particles=particles, vertices=vertices, view=view)
	
