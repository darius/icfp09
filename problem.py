import compiledvm

class Problem:

    def __init__(self, scenario, watching=False, team_id=468):
        self.scenario = scenario
        self.watching = watching
        self.team_id = team_id
        self.m = compiledvm.CompiledVM(self.bin_name)
        self.m.actuate(0x3E80, scenario)
        self.canvas = None
        if watching:
            self.set_up_canvas()

    bin_name = None             # abstract

    def make_osf(self):
        self.run()
        self.write_osf()

    def run(self):
        abstract

    def write_osf(self):
        self.m.write_trace(open('osf/%d.osf' % self.scenario, 'wb'),
                           self.team_id, 
                           self.scenario)

    def set_up_canvas(self):
        # A good scale for our canvas, one that just shows everything
        # in motion, depends on what's in the scenario. So first run a
        # step in a throwaway VM (so at least the positions of things
        # are available).
        p = self.__class__(self.scenario)
        p.step()
        self.canvas = p.make_canvas()

    def make_canvas(self):
        abstract

    def review(self, frames):
        for step, acts in frames:
            while self.m.nsteps < step:
                self.step()
            print 'Step', step  # TODO: show actuations on screen instead
            for actuator, value in acts:
                self.m.actuate(actuator, value)
        if self.watching:
            self.canvas.hold()

    def step(self):
        self.m.step()
        if self.watching:
            if (self.m.nsteps - 1) % self.view_update_period == 0:
                self.show()
                self.canvas.react()

    view_update_period = None   # abstract

    def show(self):
        abstract

    # These sensors happen to be the same in all contest problems:
    def get_score(self): return self.m.sensors[0]
    def get_fuel(self):  return self.m.sensors[1]
    def get_r(self):     return (-self.m.sensors[2], -self.m.sensors[3])

    # And so does this actuator:
    def set_dv(self, (dvx, dvy)):
        self.prev_burn = (dvx, dvy)
        self.m.actuate(0x2, dvx)
        self.m.actuate(0x3, dvy)
