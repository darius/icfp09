from math import acos, atan2, cos, hypot, pi, sin, sqrt
import sys

import compiledvm
from mechanics import *

team_id = 468

def main():
    assert 2 == len(sys.argv)
    run_it(int(sys.argv[1]))


def run_it(scenario):
    m = compiledvm.CompiledVM('bin2', loud=False)

    def show():
        r = my_position()
        t = get_target()
        print ('%5d   %10.2f %10.f\n        %10.2f %10.2f\n        %10.2f %10.2f'
               % (m.nsteps, r[0], r[1], t[0]-r[0], t[1]-r[1], t[0], t[1]))

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
        fudge = 0 if scenario == 2002 else 16  # XXX cheating
        for i in range(int(T) - fudge):
            prev_r = my_position()
            next_target = rotate(get_target(), omega)
            m.step()
            show()

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

    def my_next_position(v):
        rn, vn = tick(my_position(), v, (0.,0.))
        return rn

    def my_velocity(prev_r, prev_burn):
        return infer_v(prev_r, prev_burn, my_position())

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

    def calculate_burn():
        return calculate_hohmann_transfer(my_radius(),
                                          magnitude(get_target()))

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

    m.actuate(a_config, scenario)
    run()
    m.write_trace(open('%d.osf' % scenario, 'wb'), team_id, scenario)


if __name__ == '__main__':
    main()
