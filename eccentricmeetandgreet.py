from mechanics import *
import meetandgreet

class EccentricMeetAndGreetProblem(meetandgreet.MeetAndGreetProblem):
    bin_name = 'bin3'

    def run(self):
        self.set_dv(origin)
        for i in range(500000):
            self.step()

    view_update_period = 5

    def make_canvas(self):
        import canvas
        self.prev_r = self.get_r()
        prev_t = self.get_t()
        self.step()
        v = self.get_v()
        vt = infer_v(prev_t, origin, self.get_t())

        def furthest(r0, v0):
            r = magnitude(r0)
            v = magnitude(v0)
            return 2*GM*r / (2*GM - r*v**2)

        scale = max(furthest(self.get_r(), v),
                    furthest(self.get_t(), vt))
        return canvas.Canvas(1.05 * scale)
