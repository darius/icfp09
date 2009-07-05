import clop
import scenarios
import struct

def main():
    options = clop.parse('osf_file')
    review(options.osf_file)

def review(osf_filename):
    team_id, scenario, frames = load_osf(open(osf_filename, 'rb'))
    p = scenarios.make_problem(scenario, watching=True)
    p.review(frames)

def load_osf(osf_file):
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


if __name__ == '__main__':
    main()
