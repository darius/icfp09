import ctypes

import osf

# These arrays go mostly unused. TODO: allocate only what's needed.
DataArray      = ctypes.c_double * (2**14)
SensorsArray   = ctypes.c_double * (2**14)
ActuatorsArray = ctypes.c_double * (2**14)
StatusArray    = ctypes.c_int * 1

class CompiledVM:

    def __init__(self, bin_name):
        data_module = __import__(bin_name)
        self.lib       = ctypes.CDLL('%s.dylib' % bin_name)
        self.data      = DataArray(*data_module.data)
        self.sensors   = SensorsArray()
        self.actuators = ActuatorsArray()
        self.status    = StatusArray(0)
        self.updated   = set()
        self.nsteps    = 0
        self.trace     = []

    def write_trace(self, trace_file, team_id, scenario):
        osf.dump(trace_file, team_id, scenario, self.trace, self.nsteps)

    def step(self):
        self.lib.step(self.data, self.sensors, self.actuators, self.status)
        if self.updated:
            acts = [(a, self.actuators[a]) for a in sorted(self.updated)]
            self.trace.append((self.nsteps, acts))
            self.updated.clear()
        self.nsteps += 1

    def actuate(self, actuator, value):
        value = float(value)
        if value != self.actuators[actuator] or self.nsteps == 0:
            self.updated.add(actuator)
            self.actuators[actuator] = value
