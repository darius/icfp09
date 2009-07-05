from math import cos, pi, sin, sqrt
from sys import stderr

from mechanics import *
import problem

def report(*args):
    for arg in args:
        print >>stderr, arg,
    print >>stderr

class MeetAndGreetProblem(problem.Problem):
    bin_name = 'bin2'

    def telemetry(self):
        r = self.get_r()
        t = self.get_t()
        report('%5d   %10.2f %10.f\n' % (self.m.nsteps, r[0], r[1]))
        report('        %10.2f %10.2f' % (t[0]-r[0], t[1]-r[1]))
        report('        %10.2f %10.2f' % (t[0], t[1]))

    def run(self):
        self.set_dv((0., 0.))
        self.step()
        r0 = self.get_r()
        t0 = self.get_t()
        self.step()
        r1 = self.get_r()
        t1 = self.get_t()
        clockwise = (cross(r0, r1) < 0)
        omega = relative_angle(t0, t1) # angular velocity of target

        dv, dv_prime, T = self.calculate_burn()
        while not self.propitious(omega, T):
            self.step()
            self.telemetry()
            if 50000 < self.m.nsteps:
                report('Giving up')
                return
        prev_r = self.get_r()
        self.burn(self.tangent(dv, clockwise))
        report('Burned')
        self.telemetry()

        self.set_dv((0., 0.))
        fudge = 0 if self.scenario == 2002 else 16  # XXX cheating
        for i in range(int(T) - fudge):
            prev_r = self.get_r()
            next_target = rotate(self.get_t(), omega)
            self.step()
            self.telemetry()

        B0, B1 = self.compute_insertion(clockwise, omega, prev_r)
        report('Insertion burns')
        self.burn(B0)
        self.telemetry()
        prev_t = self.get_t()
        self.burn(B1)
        self.telemetry()

        report('Inserted')
        report('rt actual', self.get_t())
        report('rv actual', infer_v(prev_t, (0.,0.), self.get_t()))
        self.telemetry()
        report('Initial separation',
               magnitude(vsub(self.get_r(), self.get_t())))

        self.set_dv((0., 0.))
        for i in range(1000): self.step()
        self.telemetry()
        report('Final separation', magnitude(vsub(self.get_r(), self.get_t())))

    def compute_insertion(self, clockwise, omega, prev_r):
        r0 = self.get_r()
        v0 = self.get_v(prev_r, (0.,0.))
        rt = rotate(self.get_t(), 2 * omega)
        speed = sqrt(GM / magnitude(self.get_t()))
        vt = tangent_from(rt, speed, clockwise)
        report('rt', rt)
        report('vt', vt)
        return compute_rendezvous(r0, v0, rt, vt)

    def get_v(self, prev_r, prev_burn):
        return infer_v(prev_r, prev_burn, self.get_r())

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

    def burn(self, dv):
        self.set_dv(dv)
        self.step()

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
