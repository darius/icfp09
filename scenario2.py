from math import atan2, cos, hypot, pi, sin, sqrt
import sys

import vm

team_id = 468

def main():
    assert 2 == len(sys.argv)
    run_it(int(sys.argv[1]))


GM = 6.67428e-11 * 6.0e24

one_degree = pi / 180.0

def run_it(scenario):
    trace_file = open('%d.osf' % scenario, 'wb')
    m = vm.VM(trace_file=trace_file, loud=False)

    # Before trying to solve the scenario, let's just check that the
    # initial orbits are circular, as promised:
    def watch():
        set_dv((0.0, 0.0))
        t = None
        for i in range(100):
            m.step()
            r = my_position()
            if t: print angle(get_target()) - angle(t)
            t = get_target()
            print ('r %g\ta %g\tt %g\ta %g'
                   % (magnitude(r), angle(r), magnitude(t), angle(t)))

    def show():
        r = my_position()
        t = get_target()
        print ('%d\tr %g\ta %g\tt %g\ta %g'
               % (m.nsteps, magnitude(r), angle(r), magnitude(t), angle(t)))

    def run():
        set_dv((0.0, 0.0))
        m.step()
        r0 = my_position()
        t0 = get_target()
        m.step()
        r1 = my_position()
        t1 = get_target()
        clockwise = (cross(r0, r1) < 0)
        omega = relative_angle(t0, t1)
        print 'omega', omega
        dv, dv_prime, T = calculate_burn()
        while not propitious(omega, T):
            m.step()
            show()
            if 50000 < m.nsteps:
                print 'Giving up'
                return
        burn(dv, clockwise)
        print 'Burned'
        show()
        set_dv((0.0, 0.0))
        for i in range(int(T)): m.step()
        burn(dv_prime, clockwise)
        print 'Inserted'
        show()
        set_dv((0.0, 0.0))
        m.step()
        for i in range(1000): m.step()
        print 'Score', get_score()
        show()

    def propitious(omega, T):
        # omega: angular velocity of target
        # T: transit time to target orbit
        # Return true iff, T seconds from now, the target will
        # be approximately 180 degrees from our current angle.
        # (That's our launch window.)
        a = extrapolate_target_angle(omega, T)
        dest = angle(my_position()) + pi
        return angle_approx_zero(a - dest)

    def extrapolate_target_angle(omega, T): # angle of target after time T
        return angle(get_target()) + int(T) * omega

    def angle_approx_zero(a):
        a = rr(a)
        mag_a = min(a, 2*pi - a)
        return mag_a < one_degree * 4e-3

    def rr(a):  # range-reduce an angle
        while a < 0:     a += 2*pi
        while 2*pi <= a: a -= 2*pi
        assert 0 <= a < 2*pi
        return a

    def calculate_burn():
        r1 = my_radius()
        r2 = magnitude(get_target())
        dv       = sqrt(GM / r1) * (sqrt(2 * r2 / (r1 + r2)) - 1)
        dv_prime = sqrt(GM / r2) * (1 - sqrt(2 * r1 / (r1 + r2)))
        T        = pi * (r1 + r2) * sqrt((r1 + r2) / (8*GM))
        return dv, dv_prime, T

    def burn(dv, clockwise):
        theta = angle(get_s()) + (pi/2 if clockwise else -pi/2)
        set_dv((cos(theta) * dv, sin(theta) * dv))
        m.step()

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
    run()
    m.write_trace_end()
    trace_file.close()

def magnitude((x, y)):       return hypot(x, y)
def angle((x, y)):           return atan2(y, x)

def vnegate((x, y)):         return (-x, -y)
def vscale(c, (x, y)):       return (c*x, c*y)

def vadd((x0,y0), (x1,y1)):  return (x0+x1, y0+y1)
def vsub((x0,y0), (x1,y1)):  return (x0-x1, y0-y1)

def dot((x0,y0), (x1,y1)):   return x0 * x1 + y0 * y1
def cross((x0,y0), (x1,y1)): return x0 * y1 - x1 * y0

def relative_angle(v0, v1):  return atan2(cross(v0, v1), dot(v0, v1))


if __name__ == '__main__':
    main()
