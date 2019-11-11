from app import app, mongo
from flask import render_template, request, jsonify
import operator
from werkzeug import secure_filename
from app import hepmcio_json
from app import hepmcio
import os
import json
import io
from functools import reduce

@app.route('/')
@app.route('/index')
def index():
	"""
	View for the home page.
	"""
	return render_template("index.html", title="Home")

@app.route('/upload')
def upload():
	"""
	View for the upload page.
	"""
	return render_template("upload.html", title="Upload a file")

@app.route('/uploader', methods=['GET', 'POST'])
def uploader():
	"""
	A view for the file upload action. Retrieves file from a form, parses it using HepMCIO and uploads
	the parsed data to the database.

	Multiple checks are performed to see whether the file upload is well-formed.

	Returns:
	response string -- a string indicating the outcome of the upload.
	"""
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


@app.route("/visualiser/<string:filename>/")
def visualiser(filename):
	"""
	View for the Visualiser. Gets first event in requested file and returns particle/vertex data
	to the Visualiser template/JS.

	Arguments:
	filename -- the name of the required file provided in the URL.

	Returns:
	file - filename provided in the URL.
	particles - an array of interesting particles from the first event in the file.
	vertices - an array of vertices from the first event in the file.
	
	Returned to the render_template call.
	"""
	collection = mongo.db[filename]
	jsonEncoder = hepmcio_json.HepMCJSONEncoder()
	hepMCDecoder = hepmcio_json.HepMCJSONDecoder()
	jsonDecoder = json.JSONDecoder()
	#Get first event data in file and decode to HepMCIO objects.
	event = collection.find_one({"type":"event", "no":1}, {"_id":False})
	particleJson = collection.find({"type":"particle", "event":event["barcode"]}, {"_id":False})
	particles = []
	for particle in particleJson:
		particles.append(jsonEncoder.encode(particle))
	
	vertices = []
	vertexJson = collection.find({"type":"vertex", "event":event["barcode"]}, {"_id":False})
	for vertex in vertexJson:
		vertices.append(jsonEncoder.encode(vertex))
	event = jsonEncoder.encode(event)
	
	
	#Decode event to find interesting particles, i.e. particles above PT_CUTOFF and their ancestors..
	eventObject = hepmcio_json.EventJSONObject(event, particles, vertices)
	decodedEvent = hepMCDecoder.decode(eventObject)

	PT_CUTOFF = 0.0
	intParticles = [particle for particle in decodedEvent.particles.values() if particle.status!=1 and \
		particle.mom[0]**2 + particle.mom[1]**2 > PT_CUTOFF**2]
	#Build a single list from the individual particle ancestor lists.
	intParticleAncestors = reduce(operator.concat, [hepmcio.get_ancestors(particle)[:-1] for particle in intParticles])

	particles = []
	for particle in (intParticles + intParticleAncestors):
		#Encode particle to JSON, decode to Python dicts.
		particles.append(jsonDecoder.decode(jsonEncoder.encode(particle)))
	#Decode to Python dicts.
	vertices = list(map(jsonDecoder.decode, vertices))
	
	return render_template("visualiser.html", title="Visualiser", file=filename, particles=particles, vertices=vertices)
	
@app.route('/visualiser/get_event', methods=['GET'])
def get_event():
	"""
	A view for the AJAX call from the Visualiser. Receives an HTTP GET and retrieves an event.

	HTTP request:
	no -- number of the event to be retrieved.
	filename - filename for the file.

	Returns:
	A dict containing:
	particles -- an array of interesting particles from the event.
	vertices -- an array of interesting vertices from the event.
	"""
	#Get HTTP query args.
	no = request.args.get('no')
	filename = request.args.get('filename')
	collection = mongo.db[filename]

	jsonEncoder = hepmcio_json.HepMCJSONEncoder()
	hepMCDecoder = hepmcio_json.HepMCJSONDecoder()
	jsonDecoder = json.JSONDecoder()
	#Everything below same as in the Visualiser view.
	event = collection.find_one({"type":"event", "no":int(no)}, {"_id":False})
	particleJson = collection.find({"type":"particle", "event":event["barcode"]}, {"_id":False})
	particles = []
	for particle in particleJson:
		particles.append(jsonEncoder.encode(particle))
	vertices = []
	vertexJson = collection.find({"type":"vertex", "event":event["barcode"]}, {"_id":False})
	for vertex in vertexJson:
		vertices.append(jsonEncoder.encode(vertex))
	event = jsonEncoder.encode(event)

	eventObject = hepmcio_json.EventJSONObject(event, particles, vertices)
	
	decodedEvent = hepMCDecoder.decode(eventObject)

	PT_CUTOFF = 0.0
	intParticles = [particle for particle in decodedEvent.particles.values() if particle.status!=1 and \
		particle.mom[0]**2 + particle.mom[1]**2 > PT_CUTOFF**2]
	
	intParticleAncestors = reduce(operator.concat, [hepmcio.get_ancestors(particle)[:-1] for particle in intParticles])

	particles = []
	for particle in (intParticles + intParticleAncestors):
		particles.append(jsonDecoder.decode(jsonEncoder.encode(particle)))
	
	vertices = list(map(jsonDecoder.decode, vertices))
	
	return {"particles":jsonEncoder.encode(particles), "vertices":jsonEncoder.encode(vertices)}