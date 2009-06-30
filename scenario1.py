from math import atan2, cos, hypot, pi, sin, sqrt
import sys

import compiledvm

team_id = 468

def main():
    assert 2 == len(sys.argv)
    run_it(int(sys.argv[1]))


GM = 6.67428e-11 * 6.0e24

def run_it(scenario):
    m = compiledvm.CompiledVM('bin1', loud=False)
    
    def run():
        set_dv((0.0, 0.0))
        m.step()
        s0 = get_s()
        m.step()
        s1 = get_s()
        clockwise = (cross(s0, s1) < 0)
        dv, dv_prime, t = calculate_burn()
        burn(dv, clockwise)
        set_dv((0.0, 0.0))
        for i in range(int(t)): m.step()
        burn(dv_prime, clockwise)
        set_dv((0.0, 0.0))
        m.step()
        for i in range(1000): m.step()
        print 'Score', get_score()

    def calculate_burn():
        r1 = get_current_radius()
        r2 = get_target_radius()
        dv       = sqrt(GM / r1) * (sqrt(2 * r2 / (r1 + r2)) - 1)
        dv_prime = sqrt(GM / r2) * (1 - sqrt(2 * r1 / (r1 + r2)))
        t        = pi * (r1 + r2) * sqrt((r1 + r2) / (8*GM))
        return dv, dv_prime, t

    def burn(dv, clockwise):
        theta = get_theta() + (pi/2 if clockwise else -pi/2)
        set_dv((cos(theta) * dv, sin(theta) * dv))
        m.step()

    # Sensor ports
    s_score, s_fuel, s_sx, s_sy, s_rt = range(5)

    def get_score():          return m.sensors[s_score]
    def get_fuel():           return m.sensors[s_fuel]
    def get_s():              return (m.sensors[s_sx], m.sensors[s_sy])
    def get_target_radius():  return m.sensors[s_rt]

    def get_theta():          return atan2(m.sensors[s_sy], m.sensors[s_sx])
    def get_current_radius(): return hypot(*get_s())

    # Actuator ports
    a_dvx, a_dvy, a_config = 2, 3, 0x3E80

    def set_dv((dvx, dvy)):
        m.actuate(a_dvx, dvx)
        m.actuate(a_dvy, dvy)

    m.actuate(a_config, scenario)
    run()
    m.write_trace(open('%d.osf' % scenario, 'wb'), team_id, scenario)

def cross((x0,y0), (x1,y1)):
    return x0 * y1 - x1 * y0


if __name__ == '__main__':
    main()
