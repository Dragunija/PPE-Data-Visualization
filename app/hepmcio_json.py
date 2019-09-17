import json
from app import hepmcio

class ParticleEncoder(json.JSONEncoder):
    def default(self,obj):
        if isinstance(obj,hepmcio.Particle):
            return {"type":"particle", "event":obj.evt.num, "barcode":obj.barcode, "pid":obj.pid, "mass":obj.mass, "momentum":obj.mom, "start_vertex":obj.nvtx_start, "end_vertex":obj.nvtx_end, "status":obj.status}
        return json.JSONEncoder.default(self,obj)

class VertexEncoder(json.JSONEncoder):
    def default(self,obj):
        if isinstance(obj, hepmcio.Vertex):
            return {"type":"vertex", "event":obj.evt.num, "barcode":obj.barcode, "position":obj.pos}
        return json.JSONEncoder.default(self,obj)

class EventEncoder(json.JSONEncoder):
    def default(self,obj):
        if isinstance(obj, hepmcio.Event):
            return {"type":"event", "no":obj.no, "barcode":obj.num,  "weight":obj.weights, "units":obj.units, "xsec":obj.xsec}
        return json.JSONEncoder.default(self,obj)

def as_event(dct):
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
    if dct["type"]=="vertex":
        return hepmcio.Vertex(dct["position"], dct["barcode"])
    return dct

def as_particle(dct):
    if dct["type"]=="particle":
        particle = hepmcio.Particle(dct["pid"], dct["momentum"], dct["barcode"])
        particle.status = dct["status"]
        particle.nvtx_start = dct["start_vertex"]
        particle.nvtx_end = dct["end_vertex"]
        particle.mass = dct["mass"]
        return particle
    return dct

def decodeEvent(evt, particles, vertices):
    jsonEventDecoder = json.JSONDecoder(object_hook=as_event)
    jsonParticleDecoder = json.JSONDecoder(object_hook=as_particle)
    jsonVertexDecoder = json.JSONDecoder(object_hook=as_vertex)
    evt = jsonEventDecoder.decode(evt)
    particles = [jsonParticleDecoder.decode(p) for p in particles]
    for p in particles:
        p.evt = evt
    vertices = [jsonVertexDecoder.decode(v) for v in vertices]
    for v in vertices:
        v.evt = evt
    evt.particles = {p.barcode:p for p in particles}
    evt.vertices = {v.barcode:v for v in vertices}
    return evt


def encodeEvent(evt):
    particles = [ParticleEncoder().encode(p) for _, p in evt.particles.items()]
    vertices = [VertexEncoder().encode(v) for _, v in evt.vertices.items()]
    event = EventEncoder().encode(evt)
    return (event, particles, vertices)


