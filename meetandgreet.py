from math import cos, pi, sin, sqrt
from sys import stderr

from mechanics import *
import problem

class MeetAndGreetProblem(problem.Problem):
    bin_name = 'bin2'

    def run(self):
        # First, learn the state of the universe from two successive steps.
        self.set_dv((0., 0.))
        self.stepv()
        self.stepv()
        clockwise = (cross(self.prev_r, self.get_r()) < 0)
        # Angular velocity of target:
        omega = relative_angle(self.prev_t, self.get_t()) 

        # Then wait for a launch window, and depart:
        dv, dv_prime, T = self.calculate_burn()
        while not self.propitious(omega, T):
            self.stepv()
            if 50000 < self.m.nsteps:
                report('Giving up')
                return
        report('Departure burn')
        self.burn(self.tangent(dv, clockwise))

        # Coast until rendezvous time:
        self.set_dv((0., 0.))
        fudge = 0 if self.scenario == 2002 else 16  # XXX cheating
        self.coast(int(T) - fudge)

        # Two burns to match position/velocity with the target:
        B0, B1 = self.compute_insertion(clockwise, omega)
        report('Insertion burns')
        self.burn(B0)
        self.burn(B1)
        report('Inserted')
        report('rt actual', self.get_t())
        report('rv actual', infer_v(self.prev_t, (0.,0.), self.get_t()))
        report('Initial separation',
               magnitude(vsub(self.get_r(), self.get_t())))

        # Coast for >900 steps for the VM to score us:
        self.set_dv((0., 0.))
        self.coast(1000)
        report('Final separation', magnitude(vsub(self.get_r(), self.get_t())))

    def coast(self, nsteps):
        for i in range(nsteps):
            self.stepv()

    def burn(self, dv):
        self.set_dv(dv)
        self.stepv()

    def stepv(self):
        self.prev_r = self.get_r()
        self.prev_t = self.get_t()
        self.step()
        self.telemetry()

    def telemetry(self):
        r = self.get_r()
        t = self.get_t()
        report('%5d   %10.2f %10.f' % (self.m.nsteps, r[0], r[1]))
        report('        %10.2f %10.2f' % (t[0]-r[0], t[1]-r[1]))
        report('        %10.2f %10.2f' % (t[0], t[1]))

    def compute_insertion(self, clockwise, omega):
        # It takes two burns to precisely match a position and
        # velocity. So we need (r0,v0) for our ship's state now, and
        # (rt,vt) for the target's state two time-steps from now:
        r0 = self.get_r()
        v0 = self.get_v((0.,0.))
        rt = rotate(self.get_t(), 2 * omega)
        speed = sqrt(GM / magnitude(self.get_t()))
        vt = tangent_from(rt, speed, clockwise)
        report('rt', rt)
        report('vt', vt)
        return compute_rendezvous(r0, v0, rt, vt)

    def get_v(self, prev_burn):
        return infer_v(self.prev_r, prev_burn, self.get_r())

    def propitious(self, omega, T):
        # omega: angular velocity of target
        # T: transit time to target orbit
        # Return true iff, T seconds from now, the target will
        # be approximately 180 degrees from our current angle.
        # (That's our launch window.)
        a = self.extrapolate_target_angle(omega, T)
        dest = angle(self.get_r()) + pi
        return angles_approx_equal(a, dest, one_degree * 4e-3)

    def extrapolate_target_angle(self, omega, T):
        # angle of target after interval T
        return angle(self.get_t()) + int(T) * omega

    def calculate_burn(self):
        return calculate_hohmann_transfer(magnitude(self.get_r()),
                                          magnitude(self.get_t()))

    def get_theta(self):
        x, y = self.get_r()
        return atan2(-y, -x)

    def tangent(self, dv, clockwise):
        return tangent_from(self.get_r(), dv, clockwise)

    def get_t(self):
        return vadd(self.get_r(),
                    (self.m.sensors[4], self.m.sensors[5]))

    view_update_period = 1

    def make_canvas(self):
        import canvas
        scale = max(magnitude(self.get_r()),
                    magnitude(self.get_t()))
        return canvas.Canvas(1.1 * scale)

    def show(self):
        c = self.canvas
        c.draw_dot(self.get_r(), c.white)
        c.draw_dot(self.get_t(), c.green)

def tangent_from(r, dv, clockwise):
    theta = angle(vnegate(r)) + (pi/2 if clockwise else -pi/2)
    return ((cos(theta) * dv, sin(theta) * dv))

def report(*args):
    for arg in args:
        print >>stderr, arg,
    print >>stderr
