import unittest
import os
import json
from app import app, mongo, hepmcio, hepmcio_json

testParticle = None
testVertex = None
testEvent = None



class HepMCTests(unittest.TestCase):
    """
    Test suite for the Visualiser app.

    Methods:
    setUp -- sets up an app test session.
    tearDown -- performs clean-up after test suite finishes.
    openEvent -- tests opening file from filename with HepMCIO.
    testHepMCInput -- tests whether opening file with HepMCIO from filename and from file object produces same output.
    testParticleEncoder -- tests encoding particles into JSON and deocding them back.
    testVertexEncoder -- tests encoding vertices into JSON and decoding them back.
    testEventEncoder -- tests encoding events into JSON and decoding them back.
    testHepMCEncodeParticle -- 
    """

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config["MONGO_URI"] = "mongodb://localhost:27017/testDatabase"
        self.app = app.test_client()
        
    def tearDown(self):
        pass

    def openEvent(self, filename="/event_files/default.hepmc"):
        filename = os.getcwd() + filename
        return hepmcio.HepMCReader.fromfilename(filename).next()

    def testHepMCInput(self):
        filename = os.getcwd() + "/event_files/default.hepmc"
        f = open(filename)
        evt1 = hepmcio.HepMCReader(f).next()
        evt2 = hepmcio.HepMCReader.fromfilename(filename).next()
        self.assertEqual(evt1,evt2)

    
    def testParticleCoding(self):
        jsonEncoder = hepmcio_json.ParticleEncoder()
        jsonDecoder = hepmcio_json.HepMCJSONDecoder()
        particle = hepmcio.Particle(pid=-6, mom=[168.72025653940125, 3.9969008138100155, -112.36238454330316, 264.15110849058215 ], \
            barcode=21, event=hepmcio.Event())
        particle.evt.num=168
        particle.charge = 0
        particle.mass = 169.31627941137094
        particle.nvtx_start = -16
        particle.nvtx_end = -52
        particle.status = 44

        particleComparison = jsonDecoder.decode(jsonEncoder.encode(particle))

        self.assertEqual(particle, particleComparison)
    
    def testVertexCoding(self):
        jsonEncoder = hepmcio_json.VertexEncoder()
        jsonDecoder = hepmcio_json.HepMCJSONDecoder()
        vertex = hepmcio.Vertex(barcode=-20, event=hepmcio.Event())
        vertex.evt.num = 168
        print(vertex.__dict__)
        vertexComparison = jsonDecoder.decode(jsonEncoder.encode(vertex))

        self.assertEqual(vertex, vertexComparison)

    def testEventCoding(self):
        evt = self.openEvent()
        hepMCEncoder = hepmcio_json.HepMCJSONEncoder()
        hepMCDecoder = hepmcio_json.HepMCJSONDecoder()
        jsonified = hepMCEncoder.encode(evt)
        deJsonified = hepMCDecoder.decode(jsonified)
        self.assertEqual(evt, deJsonified)
        

if __name__ == "__main__":
    unittest.main()