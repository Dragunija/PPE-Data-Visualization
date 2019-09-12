
"""

TODO:
 * Non-BS spacetime units!!
 * Make B-field stepping pT-dependent: more steps for high pT
 * Particle labeling/interactive mouse-over
 * Line thickness/saturation/opacity proportional to pT or E
 * Better detector
 * Animation
"""

import hepmcio

import numpy as np

import pypdt
PDT = pypdt.PDT()

# Find interesting ancestors of stable particles
def get_ancestors(p, dmin=1e-5):
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
def parse_event(evt_file, MOMENTUM_VIEW = True, PT_CUTOFF=0.5):
## Find stable particles
    reader = hepmcio.HepMCReader(evt_file)
    evt = reader.next()
    evt = reader.next()
    particles1 = []
    for ip, p in evt.particles.items():
        if p.status != 1:
            continue
        if p.mom[0]**2 + p.mom[1]**2 < PT_CUTOFF**2:
            continue
        particles1.append(p)

    #
    #
    particles2 = []
    for p1 in particles1:
        particles2 += get_ancestors(p1)[:-1]


    ## Render particles
    total_verts = []
    particle_ids = []
    for p in particles2 + particles1:
        pidname = "had"
        if p.pid == 22:
            pidname = "pho"
        elif abs(p.pid) in [11,13,15]:
            pidname = "lep"
        elif abs(p.pid) in [12,14,16]:
            pidname = "nu"

        DT = 5e-10 #< seconds
        CLIGHT = 3e10 # mm/s
        QE = 1.6022e-19 # mm/s
        SOLENOID_BVEC = np.array([0,0,4]) #< T
        NSTEP = 16

        verts = []
        if MOMENTUM_VIEW:
            verts += [(0,0,0), p.mom[:3]]
        else:
            E = p.mom[3]
            mass = 0.0
            if p.mom[0]**2 + p.mom[1]**2 + p.mom[2]**2 < E**2:
                mass = np.sqrt(E**2 - p.mom[0]**2 - p.mom[1]**2 - p.mom[2]**2)
            pos3 = np.array(p.vtx_start().pos[:3] if p.vtx_start() else [0.,0.,0.])
            mom3 = np.array(p.mom[:3])
            charge = PDT[p.pid].charge if PDT[p.pid] else 0.
            verts.append(pos3.tolist())
            if charge != 0:
                for i in range(NSTEP):
                    vel3 = mom3/E * CLIGHT # p/E = beta, with c=1
                    pos3 += vel3*DT
                    force = PDT[p.pid].charge * np.cross(vel3, SOLENOID_BVEC) #* QE
                    mom3 += DT*force  / 500
                    verts.append(pos3.tolist())
            else:
                vel3 = mom3/E * CLIGHT
                pos3 += vel3*NSTEP*DT
                verts.append(pos3.tolist())
        total_verts.append(verts)
        particle_ids.append(pidname)

    print(particle_ids, list(map(len, total_verts)))
    return particle_ids, total_verts

parse_event("badtops_8events.hepmc")