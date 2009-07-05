from math import atan2, cos, pi, sin

from mechanics import *
import problem

class HohmannProblem(problem.Problem):
    bin_name = 'bin1'

    def run(self):
        self.set_dv((0.0, 0.0))
        self.step()
        r0 = self.get_r()
        self.step()
        r1 = self.get_r()
        clockwise = (cross(vnegate(r0), vnegate(r1)) < 0)
        dv, dv_prime, t = self.calculate_burn()

        self.burn(dv, clockwise)
        self.set_dv((0.0, 0.0))

        for i in range(int(t)): self.step()

        self.burn(dv_prime, clockwise)
        self.set_dv((0.0, 0.0))

        for i in range(1000): self.step()

    def calculate_burn(self):
        return calculate_hohmann_transfer(magnitude(self.get_r()),
                                          self.get_r_target())

    def burn(self, dv, clockwise):
        theta = self.get_theta() + (pi/2 if clockwise else -pi/2)
        self.set_dv((cos(theta) * dv, sin(theta) * dv))
        self.step()

    def get_theta(self):
        x, y = self.get_r()
        return atan2(-y, -x)

    def get_r_target(self): return self.m.sensors[4]

    view_update_period = 10

    def make_canvas(self):
        import canvas
        scale = max(magnitude(self.get_r()), self.get_r_target())
        c = canvas.Canvas(1.1 * scale)
        c.draw_circle((0, 0), self.get_r_target(), c.green)
        return c

    def show(self):
        c = self.canvas
        c.draw_dot(self.get_r(), c.white)
