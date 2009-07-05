from mechanics import *
import problem

class ClearSkiesProblem(problem.Problem):
    bin_name = 'bin4'

    def run(self):
        for i in range(3000000):
            self.step()

    def get_r_station(self):
        return vadd(self.get_r(), (self.m.sensors[4],
                                   self.m.sensors[5]))
    def get_station_fuel(self):
        return self.m.sensors(6)
    def get_r_target(self, k):
        assert 0 <= k <= 10
        return vadd(self.get_r(), (self.m.sensors[3*k+7],
                                   self.m.sensors[3*k+8]))
    def get_target_collected(self, k):
        assert 0 <= k <= 10
        return self.m.sensors(3*k+9)
    def get_r_moon(self):
        return vadd(self.get_r(), (self.m.sensors[0x64],
                                   self.m.sensors[0x65]))

    view_update_period = 200

    def make_canvas(self):
        import canvas
        rs = [self.get_r(), self.get_r_station(), self.get_r_moon()]
        rs += map(self.get_r_target, range(11))
        scale = max(map(magnitude, rs))
        return canvas.Canvas(1.05 * scale)

    def show(self):
        c = self.canvas
        c.draw_dot(self.get_r(), c.blue)
        c.draw_dot(self.get_r_station(), c.red)
        c.draw_dot(self.get_r_moon(), c.white)
        for r_target in map(self.get_r_target, range(11)):
            c.draw_dot(r_target, c.green)
