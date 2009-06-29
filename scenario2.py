from math import acos, atan2, cos, hypot, pi, sin, sqrt
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
        set_dv((0., 0.))
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
        print ('%5d   %10.2f %10.f\n        %10.2f %10.2f\n        %10.2f %10.2f'
               % (m.nsteps, r[0], r[1], t[0]-r[0], t[1]-r[1], t[0], t[1]))
#        print ('%d\tr %g\ta %g\tt %g\ta %g'
#               % (m.nsteps, magnitude(r), angle(r), magnitude(t), angle(t)))

    def run():
        set_dv((0., 0.))
        m.step()
        r0 = my_position()
        t0 = get_target()
        m.step()
        r1 = my_position()
        t1 = get_target()
        clockwise = (cross(r0, r1) < 0)
        omega = relative_angle(t0, t1) # angular velocity of target
        print 'omega', omega

        dv, dv_prime, T = calculate_burn()
        while not propitious(omega, T):
            m.step()
            show()
            if 50000 < m.nsteps:
                print 'Giving up'
                return
        prev_r = my_position()
        burn(tangent(dv, clockwise))
        print 'Burned'
        show()

        set_dv((0., 0.))
        tmp = my_next_position(my_velocity(prev_r, (0.,0.)))
        fudge = 16  # or 0 for 2002
        for i in range(int(T) - fudge): # XXX
            prev_r = my_position()
            next_target = rotate(get_target(), omega)
            m.step()
            show()
            #print 'My discrepancy', vsub(tmp, my_position())
            #print 'Target relative discrepancy', (magnitude(vsub(next_target, get_target())) / magnitude(get_target()))
            tmp = my_next_position(my_velocity(prev_r, (0.,0.)))
            #print 'Estimated next r', magnitude(tmp), angle(tmp)

        B0, B1 = compute_insertion(clockwise, omega, prev_r)
        print 'Insertion burns'
        burn(B0)
        show()
        prev_t = get_target()
        burn(B1)
        show()

        print 'Inserted'
        print 'rt actual', get_target()
        print 'rv actual', infer_v(prev_t, (0.,0.), get_target())
        show()
        print 'Initial separation', magnitude(vsub(my_position(), get_target()))

        set_dv((0., 0.))
        for i in range(1000): m.step()
        print 'Score', get_score()
        show()
        print 'Final separation', magnitude(vsub(my_position(), get_target()))

    def compute_insertion(clockwise, omega, prev_r):
        r0 = my_position()
        v0 = my_velocity(prev_r, (0.,0.))
        rt = rotate(get_target(), 2 * omega)
        speed = sqrt(GM / magnitude(get_target()))
        vt = tangent_from(rt, speed, clockwise)
        print 'rt', rt
        print 'vt', vt
        return compute_rendezvous(r0, v0, rt, vt)

    def compute_rendezvous(r0, v0, rt, vt):
        """Compute two successive burns that take us from the state
        (r0, v0) to the state (rt, vt) (approximately)."""
        U = vsub(rt, vadd(r0, vscale(2., vadd(v0, gravity(r0)))))
        V = vsub(vt, vadd(v0, vscale(2., gravity(r0))))
        B0 = vsub(U, vscale(0.5, V))
        B1 = vsub(vscale(1.5, V), U)
        return B0, B1

    def my_next_position(v):
        rn, vn = tick(my_position(), v, (0.,0.))
        return rn

    def gravity(r):
        return vscale(-GM / magnitude(r)**3, r)

    def my_velocity(prev_r, prev_burn):
        return infer_v(prev_r, prev_burn, my_position())

    def tick(r, v, B):
        """Compute next position and velocity, given current position,
        velocity, and boost."""
        rn = vadd(r, vadd(v, vscale(0.5, vadd(B, gravity(r)))))
        vn = vadd(v, vadd(B, vaverage(gravity(r), gravity(rn))))
        return rn, vn

    def infer_v(rp, Bp, r):
        """Compute current velocity given previous position, previous
        boost, and current position."""
        return vadd(vsub(r, rp), vscale(0.5, vadd(gravity(r), Bp)))

    def propitious(omega, T):
        # omega: angular velocity of target
        # T: transit time to target orbit
        # Return true iff, T seconds from now, the target will
        # be approximately 180 degrees from our current angle.
        # (That's our launch window.)
        a = extrapolate_target_angle(omega, T)
        dest = angle(my_position()) + pi
        return angle_approx_zero(a - dest)

    def extrapolate_target_angle(omega, T): # angle of target after interval T
        return angle(get_target()) + int(T) * omega

    def angle_approx_zero(a):
        a = rr(a)
        mag_a = min(a, 2*pi - a)
        return mag_a < one_degree * 4e-3

    def rr(a):                  # range-reduce an angle
        while a < 0:     a += 2*pi
        while 2*pi <= a: a -= 2*pi
        assert 0 <= a < 2*pi
        return a

    def calculate_burn():       # Hohmann transfer values
        r1 = my_radius()
        r2 = magnitude(get_target())
        dv       = sqrt(GM / r1) * (sqrt(2 * r2 / (r1 + r2)) - 1)
        dv_prime = sqrt(GM / r2) * (1 - sqrt(2 * r1 / (r1 + r2)))
        T        = pi * (r1 + r2) * sqrt((r1 + r2) / (8*GM))
        return dv, dv_prime, T

    def burn(dv):
        set_dv(dv)
        m.step()

    def tangent(dv, clockwise):
        theta = angle(get_s()) + (pi/2 if clockwise else -pi/2)
        return ((cos(theta) * dv, sin(theta) * dv))

    def tangent_from(r, dv, clockwise):
        theta = angle(vnegate(r)) + (pi/2 if clockwise else -pi/2)
        return ((cos(theta) * dv, sin(theta) * dv))

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

def vaverage(v0, v1):        return vscale(0.5, vadd(v0, v1))

def dot((x0,y0), (x1,y1)):   return x0 * x1 + y0 * y1
def cross((x0,y0), (x1,y1)): return x0 * y1 - x1 * y0

def relative_angle(v0, v1):
    #return atan2(cross(v0, v1), dot(v0, v1))
    angle = acos(dot(v0, v1) / (magnitude(v0) * magnitude(v1)))
    return angle if 0 <= cross(v0, v1) else -angle

def rotate((x,y), a):
    ca, sa = cos(a), sin(a)
    return (ca * x - sa * y, sa * x + ca * y)


if __name__ == '__main__':
    main()
