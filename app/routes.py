from app import app, mongo
from flask import render_template, request, redirect, jsonify
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

			#Get all events from file and jsonify them.
			events = hepmcio.HepMCReader(string_stream).all_events()
			hepMCEncoder = hepmcio_json.HepMCJSONEncoder()
			jsonified = [hepMCEncoder.encode(event) for event in events]

			#Each collection contains all the data in a file.
			if filename not in mongo.db.collection_names():
				collection = mongo.db[filename]
				jsonDecoder = json.JSONDecoder()

				#MongoDB takes in Python objects and not JSON strings, so have to decode before adding documents.
				for jsonObject in jsonified:
					jsonEvent = jsonDecoder.decode(jsonObject.evt)
					jsonParticles = [jsonDecoder.decode(p) for p in jsonObject.particles]
					jsonVertices = [jsonDecoder.decode(v) for v in jsonObject.vertices]

					collection.insert_one(jsonEvent)
					collection.insert_many(jsonParticles)
					collection.insert_many(jsonVertices)
		
				return "Succesfully uploaded file."
			
			return "File already in database."

		return "Incorrect file type."


@app.route("/visualiser/<string:filename>/<int:view>")
def visualiser(filename, view):
	collection = mongo.db[filename]
	event = collection.find_one({"type":"event", "no":1}, {"_id":False})
	particleJson = collection.find({"type":"particle", "event":event["barcode"]}, {"_id":False})
	particles = []
	for particle in particleJson:
		particles.append(particle)
	vertices = []
	vertexJson = collection.find({"type":"vertex", "event":event["barcode"]}, {"_id":False})
	for vertex in vertexJson:
		vertices.append(vertex)
	return render_template("visualiser.html", title="Visualiser", filename=filename, event=event, particles=particles, vertices=vertices, view=view)
	
@app.route('/visualiser/get_event', methods=['GET'])
def get_event():
	no = request.args.get('no')
	filename = request.args.get('filename')
	collection = mongo.db[filename]
	event = collection.find_one({"type":"event", "no":int(no)}, {"_id":False})
	particleJson = collection.find({"type":"particle", "event":event["barcode"]}, {"_id":False})
	particles = []
	for particle in particleJson:
		particles.append(particle)
	vertices = []
	vertexJson = collection.find({"type":"vertex", "event":event["barcode"]}, {"_id":False})
	for vertex in vertexJson:
		vertices.append(vertex)
	return jsonify(particles=particles)