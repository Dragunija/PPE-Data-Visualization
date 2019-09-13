import json
from app import hepmcio

class ParticleEncoder(json.JSONEncoder):
    def default(self,obj, filename=None):
        if isinstance(obj,hepmcio.Particle):
            return {"event":obj.evt.num, "file":filename, "barcode":obj.barcode, "pid":obj.pid, "mass":obj.mass, "momentum":obj.mom, "start_vertex":obj.nvtx_start, "end_vertex":obj.nvtx_end, "status":obj.status}
        return json.JSONEncoder.default(self,obj)

class VertexEncoder(json.JSONEncoder):
    def default(self,obj, filename=None):
        if isinstance(obj, hepmcio.Vertex):
            return {"event":obj.evt.num, "file":filename, "barcode":obj.barcode, "position":obj.pos}
        return json.JSONEncoder.default(self,obj)

class EventEncoder(json.JSONEncoder):
    def default(self,obj, filename=None):
        if isinstance(obj, hepmcio.Event):
            return {"barcode":obj.num, "file":filename, "weight":obj.weights, "units":obj.units, "xsec":obj.xsec}
        return json.JSONEncoder.default(self,obj)

def encodeFile(evt):
    particles = [ParticleEncoder().encode(p) for _, p in evt.particles.items()]
    vertices = [VertexEncoder().encode(v) for _, v in evt.vertices.items()]
    event = EventEncoder().encode(evt)
    return (event, particles, vertices)


