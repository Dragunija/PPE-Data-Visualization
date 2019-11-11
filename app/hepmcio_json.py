"""Utility module to implement JSON functionality for objects produced by hepmcio.

   Classes:
   EventJSONObject -- an object wrapper for a JSONified event
   HepMCJSONEncoder -- general JSON encoder for all hepmcio objects
   HepMCJSONDecoder -- general JSON decoder for all hepmcio objects
   ParticleEncoder -- JSON encoder implementation for particle objects
   VertexEncoder -- JSON encoder implementation for vertex objects
   EventEncoder -- JSON encoder implementation for event objects
   
   Functions:
   as_event -- object hook for JSONified events, for use with standard JSON decoder
   as_particle -- object hook for JSONified particles, for use with standard JSON decoder
   as_vertex -- object hook for JSONified vertices, for use with standard JSON decoder
   """

import json
from app import hepmcio

class EventJSONObject(object):
    """An object wrapper for JSONified events. Contains event, associated particles and vertices
    in JSON.
       """
    def __init__(self, evt, particles, vertices):
        """Constructor.
           
           Arguments:
           evt -- JSONified event object
           particles -- list of JSONified particle objects
           vertices --- list of JSONified vertex objects
        """
        self.evt = evt
        self.particles = particles
        self.vertices = vertices

    def __repr__(self):
        return f"{self.__class__} \n Event: {self.evt}"

class HepMCJSONEncoder(object):
    """General JSON encoder for hepmcio objects. Encoding returns a standard JSON string for particles and vertices,
       and an EventJSONObject for events. It is composed from custom Encoder classes overriding the standard JSON encoder.

       Methods:
       encode(self, obj) -- encodes hepmcio object.
    """
    def __init__(self):
        """Constructor without arguments. It initalizes the custom hepmcio encoders.
        """
        self.ParticleEncoder = ParticleEncoder()
        self.VertexEncoder = VertexEncoder()
        self.EventEncoder = EventEncoder()

    def encode(self, obj):
        """Encodes a given hepmcio object to JSON, or raises a TypeError 
           through the JSONEncoder base class. 
           
           Arguments:
           obj -- the object to be encoded.

           Returns:
           A JSON string if obj is an event or particle, an EventJSONObject if obj is an event.
        """
        if isinstance(obj, hepmcio.Event):
            particles = [self.ParticleEncoder.encode(p) for _, p in obj.particles.items()]
            vertices = [self.VertexEncoder.encode(v) for _, v in obj.vertices.items()]
            event = self.EventEncoder.encode(obj)
            return EventJSONObject(event, particles, vertices)
        elif isinstance(obj, hepmcio.Vertex):
            return self.VertexEncoder.encode(obj)
        else:
            return self.ParticleEncoder.encode(obj)
    
    
    
class HepMCJSONDecoder(object):
    """Decodes a given JSONified hepmcio object into a Python object. 

       Methods:
       decode(self, obj) -- decodes JSONified hepmcio object
    """
    def __init__(self):
        """Constructor without arguments. Initializes JSONDecoders with object hooks for hepmcio objects.
        """
        self.ParticleDecoder = json.JSONDecoder(object_hook=as_particle)
        self.VertexDecoder = json.JSONDecoder(object_hook=as_vertex)
        self.EventDecoder = json.JSONDecoder(object_hook=as_event)

    def decode(self, obj):
        """Decodes the given hepmcio object into a Python object. Expects either a EventJSONObject or a JSON string
           with a field 'type' and value 'particle' or 'vertex'. Otherwise raises a ValueError.
           
           Arguments:
           obj -- JSON object to be decoded, either EventJSONObject or particle/vertex JSON string

           Returns:
           A hepmcio Python object.
        """
        if isinstance(obj, EventJSONObject):
            evt = self.EventDecoder.decode(obj.evt)
            particles = [self.ParticleDecoder.decode(p) for p in obj.particles]
            for p in particles:
                p.evt = evt
            vertices = [self.VertexDecoder.decode(v) for v in obj.vertices]
            for v in vertices:
                v.evt = evt
            evt.particles = {p.barcode:p for p in particles}
            evt.vertices = {v.barcode:v for v in vertices}
            return evt
        
        objType = json.JSONDecoder().decode(obj).get("type", None)
        if objType=="particle":
            return self.ParticleDecoder.decode(obj)
        elif objType=="vertex":
            return self.VertexDecoder.decode(obj)
        else:
            raise ValueError
        

class ParticleEncoder(json.JSONEncoder):
    """JSON encoder for hepmcio Particle objects. Overrides standard JSONEncoder and its default method. 
        The returned JSON string contains all the attributes of the object plus type info.
    """
    def default(self,obj):
        if isinstance(obj,hepmcio.Particle):
            return {"type":"particle", "event":obj.evt.num, "barcode":obj.barcode, "pid":obj.pid,"charge":obj.charge, "mass":obj.mass, "momentum":obj.mom, "start_vertex":obj.nvtx_start, "end_vertex":obj.nvtx_end, "status":obj.status}
        return json.JSONEncoder.default(self,obj)

class VertexEncoder(json.JSONEncoder):
    """JSON encoder for hepmcio Vertex objects. Overrides standard JSONEncoder and its default method. 
        The returned JSON string contains all the attributes of the object plus type info.
    """
    def default(self,obj):
        if isinstance(obj, hepmcio.Vertex):
            return {"type":"vertex", "event":obj.evt.num, "barcode":obj.barcode, "position":obj.pos}
        return json.JSONEncoder.default(self,obj)

class EventEncoder(json.JSONEncoder):
    """JSON encoder for hepmcio Event objects. Overrides standard JSONEncoder and its default method. 
        The returned JSON string contains all the attributes of the object plus type info except for references to 
        associated particles/vertices to maintain a semi-normal form.
    """
    def default(self,obj):
        if isinstance(obj, hepmcio.Event):
            return {"type":"event", "no":obj.no, "barcode":obj.num,  "weight":obj.weights, "units":obj.units, "xsec":obj.xsec}
        return json.JSONEncoder.default(self,obj)

def as_event(dct):
    """Object hook for decoding JSONified events. Passed into JSONDecoder.
    """
    if dct["type"]=="event":
        event = hepmcio.Event()
        event.no = dct["no"]
        event.num = dct["barcode"]
        event.weights = dct["weight"]
        event.units = dct["units"]
        event.xsec = dct["xsec"]
        return event
    return dct


def as_vertex(dct):
    """Object hook for decoding JSONified vertices. Passed into JSONDecoder.
    """
    if dct["type"]=="vertex":
        return hepmcio.Vertex(dct["position"], dct["barcode"])
    return dct

def as_particle(dct):
    """Object hook for decoding JSONified particles. Passed into JSONDecoder.
    """
    if dct["type"]=="particle":
        particle = hepmcio.Particle(dct["pid"], dct["momentum"], dct["barcode"])
        particle.status = dct["status"]
        particle.nvtx_start = dct["start_vertex"]
        particle.nvtx_end = dct["end_vertex"]
        particle.mass = dct["mass"]
        particle.charge = dct["charge"]
        return particle
    return dct







