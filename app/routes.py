from app import app, mongo
from flask import render_template, request
from app import hepmcio_json
from app import hepmcio
import os
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
		jsonified = hepmcio_json.encodeFile(hepmcio.HepMCReader(io.StringIO(request.files['file'].read().decode('utf-8'))).next())
		mongo.db.events.insert_one(jsonified[0])
		mongo.db.particles.insert_many(jsonified[1])
		mongo.db.vertices.insert_many(jsonified[2])
		return "upload succesful"


@app.route("/visualiser/<string:filename>")
def visualiser(filename):
	
	
	return render_template("visualiser.html", title="Visualiser")
	
