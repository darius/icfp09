import struct

def dump(osf_file, team_id, scenario, frames, nsteps):
    def write(*args):
        osf_file.write(struct.pack(*args))
    write('<III', 0xCAFEBABE, team_id, scenario)
    for step, acts in frames:
        write('<II', step, len(acts))
        for a_id, value in acts:
            write('<Id', a_id, value)
    write('<II', nsteps, 0)
    if 3e6 < nsteps:
        print 'WARNING: too many steps for a contest solution'

def load(osf_file):
    def read_i(): return struct.unpack('<I', osf_file.read(4))[0]
    def read_d(): return struct.unpack('<d', osf_file.read(8))[0]
    assert 0xCAFEBABE == read_i()
    team_id, scenario = read_i(), read_i()
    frames = []
    while True:
        step, n_acts = read_i(), read_i()
        acts = [(read_i(), read_d()) for i in range(n_acts)]
        frames.append((step, acts))
        if n_acts == 0: break
    return team_id, scenario, frames
