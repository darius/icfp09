from math import atan2, cos, hypot, pi, sin, sqrt
import sys

import vm

team_id = 468

def main():
    assert 2 == len(sys.argv)
    run_it(int(sys.argv[1]))


GM = 6.67428e-11 * 6.0e24

def run_it(scenario):
    trace_file = open('%d.osf' % scenario, 'wb')
    m = vm.VM(trace_file=trace_file, loud=False)

    # Before trying to solve the scenario, let's just check that the
    # initial orbits are circular, as promised:
    def watch():
        set_dv((0.0, 0.0))
        for i in range(100):
            m.step()
            r = my_position()
            t = get_target()
            print ('r %g\ta %g\tt %g\ta %g'
                   % (magnitude(r), angle(r), magnitude(t), angle(t)))

    # Sensor ports
    s_score, s_fuel, s_ex, s_ey, s_tx, s_ty = range(6)

    def get_score(): return m.sensors[s_score]
    def get_fuel():  return m.sensors[s_fuel]
    def get_s():     return (m.sensors[s_ex], m.sensors[s_ey])
    def get_t():     return (m.sensors[s_tx], m.sensors[s_ty])

    def my_position(): return vnegate(get_s())
    def my_radius():   return magnitude(get_s())
    def my_angle():    return angle(my_position())

    def get_target():  return vadd(my_position(), get_t())
        
    # Actuator ports
    a_dvx, a_dvy, a_config = 2, 3, 0x3E80

    def set_dv((dvx, dvy)):
        m.actuate(a_dvx, dvx)
        m.actuate(a_dvy, dvy)

    m.load('bin2.obf')
    m.actuate(a_config, scenario)
    m.write_trace_header(team_id, scenario)
    watch()
    m.write_trace_end()
    trace_file.close()

def magnitude((x, y)):       return hypot(x, y)
def angle((x, y)):           return atan2(y, x)

def vnegate((x, y)):         return (-x, -y)
def vscale(c, (x, y)):       return (c*x, c*y)

def vadd((x0,y0), (x1,y1)):  return (x0+x1, y0+y1)

def cross((x0,y0), (x1,y1)): return x0 * y1 - x1 * y0


if __name__ == '__main__':
    main()
