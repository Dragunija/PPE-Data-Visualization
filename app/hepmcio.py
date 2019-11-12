import pypdt

"""\
A simple pure-Python parser for HepMC IO_GenEvent ASCII event files, which may
be a lot more convenient than using either the native C++ HepMC API, or wrappers
like pyhepmc!

Classes:

Particle -- particle in an event file; represents a particle in the event graph.
Vertex -- vertex in an event file; represents a vertex in the event graph.
Event -- event in an event file; represents an event graph. Contains hashmaps of all particles and vertices associated
with the graph.
HepMCReader -- the reader class for parsing HepMC files. Can read files using either filename or a file object.
HepMCWriter -- the writer class for creating HepMC files. Currently unfinished.

Functions:

get_ancestors -- gets all the ancestors of a particle above some energy threshold.
mk_nx_graph -- creates a NetworkX graph from event data.
"""

__version__ = "1.1.1"
__author__ = "Andy Buckley, Darius Darulis"
__email__ = "andy@insectnation.org, darius.dragas@gmail.com"

def get_ancestors(p, dmin=1e-5):
    """
    Gets all ancestors of a particle above some energy threshold by traversing vertices.

    Arguments:
    p -- particle whose ancestors to get.
    dmin -- energy cut-off for being considered "interesting".

    Returns:
    rtn -- a list of lists containing interesting ancestor particles.
    """
    rtn = []
    v = p.vtx_start()
    if v:
        d2 = v.pos[0]**2 + v.pos[1]**2 + v.pos[2]**2
        if d2 > dmin**2:
            for pp in p.parents():
                # if pp.status != 2:
                #     continue
                rtn += get_ancestors(pp)
    rtn.append(p)
    return rtn

class Particle(object):
    """
    A particle in a HepMC event graph.

    Methods:
    vtx_start -- returns the particle's parent vertex from the event graph.
    vtx_end -- returns the particle's target vertex from the event graph.
    parents -- returns the particle's parent particles from the event graph.
    children -- returns the particle's children particles from the event graph.
    """
    def __init__(self, pid=0, mom=[0,0,0,0], barcode=0, event=None):
        """
        Constructor.

        Arguments:
        pid -- ID identifying particle type.
        mom -- the particle's momentum.
        barcode -- barcode uniquely identifying an event graph element.
        event -- the event the particle is associated with.
        """
        self.evt = event
        self.barcode = barcode
        self.pid = pid
        self.status = None
        self.mom = list(mom)
        self.charge = None
        #Start vertex for the particle.
        self.nvtx_start = None
        #Target vertex for the particle.
        self.nvtx_end = None
        self.mass = None

    def vtx_start(self):
        """
        Returns the start vertex for the particle from the event graph.
        """
        return self.evt.vertices.get(self.nvtx_start) if self.evt else None

    def vtx_end(self):
        """
        Returns the target vertex for the particle from the event graph.
        """
        return self.evt.vertices.get(self.nvtx_end) if self.evt else None

    def parents(self):
        """
        Returns parent particles of the particle.
        """
        return self.vtx_start().parents() if self.vtx_start() else None

    def children(self):
        """
        Returns the children particles for the particle.
        """
        return self.vtx_end().children() if self.vtx_end() else None

    
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.evt == other.evt and self.barcode == other.barcode and self.pid == other.pid and self.status == other.status and self.mom == other.mom and self.nvtx_start == other.nvtx_start and self.nvtx_end == other.nvtx_end and self.mass == other.mass and self.charge == other.charge
        return False

    def __repr__(self):
        return "P" + str(self.barcode)
        


class Vertex(object):
    """
    A vertex in a HepMC event graph. 

    Methods:
    parents -- returns particles incoming into the vertex.
    children -- returns particles coming out of the vertex.
    """
    def __init__(self, pos=[0,0,0,0], barcode=0, event=None):
        """
        Constructor.

        Arguments:
        pos -- vertex coordinates.
        barcode -- barcode uniquely identifying an event element.
        event -- the event the vertex is associated with.
        """
        self.evt = event
        self.pos = list(pos)
        self.barcode = barcode

    def parents(self):
        """
        Returns particles coming into the vertex by comparing barcodes.
        """
        return [p for p in self.evt.particles.values() if p.nvtx_end == self.barcode]

    def children(self):
        """
        Returns particles coming out of the vertex by comparing barcodes.
        """
        return [p for p in self.evt.particles.values() if p.nvtx_start == self.barcode]

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.evt == other.evt and self.pos == other.pos and self.barcode == other.barcode
        return False

    def __repr__(self):
        return "V" + str(self.barcode)
       


class Event(object):
    """
    An event represnting a HepMC graph.
    """
    def __init__(self):
        """
        Constructor.
        no -- the order of the event in the file.
        num -- barcode uniquely identifying the event.
        units -- the physical units used in the event.
        xsec --
        particles -- a hashmap of particles in the event.
        vertices -- a hashmap of vertices in the event.
        """
        self.no = None
        self.num = None
        self.weights = None
        self.units = [None, None]
        self.xsec = [None, None]
        self.particles = {}
        self.vertices = {}
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.num == other.num and self.weights == other.weights and self.units == other.units and self.xsec == other.xsec 
        return False

    def __repr__(self):
        return "E%d. #p=%d #v=%d, xs=%1.2e+-%1.2e, No%d" % \
               (self.num, len(self.particles), len(self.vertices),
                self.xsec[0], self.xsec[1], self.no)


class HepMCReader(object):

    def __init__(self, file):
        self._file = file
        self._currentline = None
        self._currentvtx = None
        self.version = None
        ## First non-empty line should be the version info
        while True:
            self._read_next_line()
            if self._currentline.startswith("HepMC::Version"):
                self.version = self._currentline.split()[1]
                break
        ## Read on until we see the START_EVENT_LISTING marker
        while True:
            self._read_next_line()
            if self._currentline == "HepMC::IO_GenEvent-START_EVENT_LISTING":
                break
        ## Read one more line to make the first E line current
        self._read_next_line()

    @classmethod
    def fromfilename(cls, filename):
        return cls(open(filename))

    def _read_next_line(self):
        "Return the next line, stripped of the trailing newline"
        self._currentline = self._file.readline()
        if not self._currentline: # no newline means it's the end of the file
            return False
        if self._currentline.endswith("\n"):
            self._currentline = self._currentline[:-1] # strip the newline
        return True

    def next(self):
        """
        Gets next event in file. Returns none if no events are left.

        Returns:
        evt -- next event in file.
        """
        "Return a new event graph"
        PDT = pypdt.PDT()
        evt = Event()
        if not self._currentline or self._currentline == "HepMC::IO_GenEvent-END_EVENT_LISTING":
            return None
        assert self._currentline.startswith("E ")
        vals = self._currentline.split()
        evt.num = int(vals[1])
        evt.weights = [float(vals[-1])] # TODO: do this right, and handle weight maps
        ## Read the other event header lines until a Vertex line is encountered
        while not self._currentline.startswith("V "):
            self._read_next_line()
            vals = self._currentline.split()
            if vals[0] == "U":
                evt.units = vals[1:3]
                #print("U")
            elif vals[0] == "C":
                evt.xsec = [float(x) for x in vals[1:3]]
                #print("C")
        ## Read the event content lines until an Event line is encountered
        while not self._currentline.startswith("E "):
            vals = self._currentline.split()
            if vals[0] == "P":
                bc = int(vals[1])
                #print("P", bc)
                try:
                    p = Particle(barcode=bc, pid=int(vals[2]), mom=[float(x) for x in vals[3:7]], event=evt)
                    p.mass = float(vals[7])
                    p.status = int(vals[8])
                    p.nvtx_start = self._currentvtx
                    p.nvtx_end = int(vals[11])
                    p.charge = PDT[p.barcode].charge if PDT[p.barcode] else 0.0
                    evt.particles[bc] = p
                except:
                    print (vals)
            elif vals[0] == "V":
                bc = int(vals[1])
                #print("V", bc)
                self._currentvtx = bc # current vtx barcode for following Particles
                v = Vertex(barcode=bc, pos=[float(x) for x in vals[3:7]], event=evt)
                evt.vertices[bc] = v
            elif not self._currentline or self._currentline == "HepMC::IO_GenEvent-END_EVENT_LISTING":
                break
            self._read_next_line()
        return evt
    
    def all_events(self):
        """
        Utility function to get all events in the file. Returns empty list if no events in file.

        Returns:
        events -- a list of events in the file.
        """
        #Counter for the number of objects in file.
        no = 1
        events = []
        evt = self.next()
        while evt is not None:
            evt.no = no
            no += 1
            events.append(evt)
            evt = self.next()
        return events


class HepMCWriter(object):

    def __init__(self, filename):
        self._file = open(filename)
        self._file.write("HepMC::Version 2.6.X")
        self._file.write("HepMC::IO_GenEvent-START_EVENT_LISTING\n")

    def finalize(self):
        "Close the HepMC event file"
        self._file.write("HepMC::IO_GenEvent-END_EVENT_LISTING\n")
        self._file.close()
        self._file = None

    # TODO: FINISH!
    def write_next(self, evt):
        "Write the next event"
        self._file.write("E\n")
        self._file.write("U\n") # evt.units
        self._file.write("U\n") # evt.xsec
        for v in evt.vertices:
            self._file.write("V\n")
            for p in v.particles_in + v.particles_out:
                self._file.write("P\n")


def mk_nx_graph(evt):
    "Make a NetworkX graph"
    import networkx as nx
    nxevt = nx.Graph()
    nxevt.add_nodes_from(evt.vertices.values())
    for p in evt.particles.values():
        nxevt.add_edge(evt.vertices[p.nvtx_start],
                       evt.vertices[p.nvtx_end] if p.nvtx_end else p.nvtx_end,
                       object=p)
        # TODO: Why aren't there enough particles?
    return nxevt


if __name__ == "__main__":

    import sys
    mcfile = sys.argv[1] if len(sys.argv) > 1 else "out.hepmc"
    r = HepMCReader(mcfile)
    print ("version =", r.version)
    while True:
        evt = r.next()
        if not evt:
            break # end of file
        print (evt)
        # for p in evt.particles: print p
        # for v in evt.vertices: print v

        # ## Make an NX event graph
        # nxevt = mk_nx_graph(evt)
        # print "#p =", nxevt.number_of_nodes(), "#v =", nxevt.number_of_edges()

        # ## Plot the NX event graph
        # import matplotlib.pyplot as plt
        # # nx.draw_circular(nxevt)
        # # nx.draw_spectral(nxevt)
        # # nx.draw_random(nxevt)
        # pos = nx.graphviz_layout(nxevt, prog='dot', args='')
        # plt.figure(figsize=(8,8))
        # nx.draw(nxevt, pos, node_size=20, alpha=0.5, node_color="blue", with_labels=False)
        # plt.savefig("nx-%d.pdf" % evt.num)

        # break
