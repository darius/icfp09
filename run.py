import clop
import scenarios

def main():
    options = clop.parse('scenario:int')
    run(options.scenario)

def run(scenario):
    p = scenarios.make_problem(scenario) #, watching=True)
    p.make_osf()
    print 'Scenario %d score: %6.2f' % (scenario, p.get_score())

if __name__ == '__main__':
    main()
