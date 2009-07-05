from mechanics import *
import problem

class HohmannProblem(problem.Problem):
    bin_name = 'bin1'

    def run(self):
        self.coast(2)
        dv_depart, t_coast, dv_arrive = self.calculate_burn()
        self.burn_tangent(dv_depart)
        self.coast(int(t_coast))
        self.burn_tangent(dv_arrive)
        self.coast(901)

    def coast(self, nsteps):
        self.set_dv(origin)
        for i in range(nsteps):
            self.stepv()

    def calculate_burn(self):
        return calculate_hohmann_transfer(magnitude(self.get_r()),
                                          self.get_r_target())

    def burn_tangent(self, dspeed):
        tangent = vdirection(self.get_v())
        self.set_dv(vscale(dspeed, tangent))
        self.stepv()

    def stepv(self):
        self.prev_r = self.get_r()
        self.step()

    def get_v(self):
        return infer_v(self.prev_r, self.prev_burn, self.get_r())

    def get_r_target(self):
        return self.m.sensors[4]

    view_update_period = 10

    def make_canvas(self):
        import canvas
        scale = max(magnitude(self.get_r()), self.get_r_target())
        c = canvas.Canvas(1.05 * scale)
        c.draw_circle(origin, self.get_r_target(), c.green)
        return c

    def show(self):
        c = self.canvas
        c.draw_dot(self.get_r(), c.white)
