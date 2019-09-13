import unittest
import os
import json
from app import app, mongo, hepmcio, hepmcio_json

class BasicTests(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config["MONGO_URI"] = "mongodb://localhost:27017/testDatabase"
        self.app = app.test_client()
        
    def tearDown(self):
        pass

    def openEvent(self, filename="/app/static/badtops_8events.hepmc"):
        filename = os.getcwd() + filename
        return hepmcio.HepMCReader.fromfilename(filename).next()

    def testHepMCInput(self):
        filename = os.getcwd() + "/app/static/badtops_8events.hepmc"
        f = open(filename)
        evt1 = hepmcio.HepMCReader(f).next()
        evt2 = hepmcio.HepMCReader.fromfilename(filename).next()
        self.assertEqual(evt1,evt2)

    
    def testParticleJson(self):
        evt = self.openEvent()
        jsonEncoder = hepmcio_json.ParticleEncoder()
        jsonDecoder = json.JSONDecoder()
        for _, p in evt.particles.items():
            jsonParticle = jsonEncoder.encode(p)
            jsonParticleDecoded = jsonDecoder.decode(jsonParticle)
            self.assertIsInstance(jsonParticle, str)
            self.assertIsInstance(jsonParticleDecoded, dict)
    
    def testVertexJson(self):
        evt = self.openEvent()
        jsonEncoder = hepmcio_json.VertexEncoder()
        jsonDecoder = json.JSONDecoder()
        for _, v in evt.vertices.items():
            jsonVertex = jsonEncoder.encode(v)
            jsonVertexDecoded = jsonDecoder.decode(jsonVertex)
            self.assertIsInstance(jsonVertex, str)
            self.assertIsInstance(jsonVertexDecoded, dict)


    def testEventJson(self):
        evt = self.openEvent()
        jsonEvent = hepmcio_json.EventEncoder().encode(evt)
        jsonEventDecoded = json.JSONDecoder().decode(jsonEvent)
        print(type(jsonEvent))
        self.assertIsInstance(jsonEvent, str)
        self.assertIsInstance(jsonEventDecoded, dict)
        

if __name__ == "__main__":
    unittest.main()