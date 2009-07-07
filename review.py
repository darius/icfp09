import clop
import osf
import scenarios

def main():
    options = clop.parse('osf_file')
    review(options.osf_file)

def review(osf_filename):
    team_id, scenario, frames = osf.load(open(osf_filename, 'rb'))
    p = scenarios.make_problem(scenario, watching=True)
    p.review(frames)

if __name__ == '__main__':
    main()
