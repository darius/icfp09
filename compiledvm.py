import ctypes
import struct

# These arrays go mostly unused. TODO: allocate only what's needed.
DataArray      = ctypes.c_double * (2**14)
SensorsArray   = ctypes.c_double * (2**14)
ActuatorsArray = ctypes.c_double * (2**14)
StatusArray    = ctypes.c_int * 1

class CompiledVM:

    def __init__(self, bin_name, loud=False):
        data_module = __import__(bin_name)
        self.lib       = ctypes.CDLL('lib%s.dylib' % bin_name)
        self.data      = DataArray(*data_module.data)
        self.sensors   = SensorsArray()
        self.actuators = ActuatorsArray()
        self.status    = StatusArray(0)
        self.updated   = set()
        self.nsteps    = 0
        self.trace     = []

    def write_trace(self, trace_file, team_id, scenario):
        def write(*args):
            trace_file.write(struct.pack(*args))
        write('<III', 0xCAFEBABE, team_id, scenario)
        for step, acts in self.trace:
            write('<II', step, len(acts))
            for a_id, value in acts:
                write('<Id', a_id, value)
        write('<II', self.nsteps, 0)

    def step(self):
        self.lib.step(self.data, self.sensors, self.actuators, self.status)
        if self.updated:
            acts = [(a, self.actuators[a]) for a in sorted(self.updated)]
            self.trace.append((self.nsteps, acts))
            self.updated.clear()
        self.nsteps += 1

    def actuate(self, actuator, value):
        value = float(value)
        self.updated.add(actuator)
        self.actuators[actuator] = value
