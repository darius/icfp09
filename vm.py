import math
import struct
import sys

def main():
    assert 2 == len(sys.argv)
    vm = VM()
    vm.load(sys.argv[1])
    vm.disassemble()

scenario = None


class VM:

    # Setup

    def __init__(self, trace_file=None, loud=False):
        self.trace = trace_file
        self.loud = loud
        self.clear()

    def clear(self):
        self.insns = []
        self.data = []
        self.sensors = {}
        self.actuators = {}
        self.updated = set()
        self.status = False
        self.nsteps = 0

    def load(self, filename):
        f = open(filename, 'rb')
        for frame in range(2**14):
            bytes = f.read(12)
            if not bytes: break
            if frame % 2 == 0:
                d, i = struct.unpack('<dI', bytes)
            else:
                i, d = struct.unpack('<Id', bytes)
            self.insns.append(i)
            self.data.append(d)

    # Write the submitted-trace file
            
    def write_trace_header(self, team_id, scenario):
        self.trace.write(struct.pack('<I', 0xCAFEBABE))
        self.trace.write(struct.pack('<I', team_id))
        self.trace.write(struct.pack('<I', scenario))

    def write_trace_frame(self):
        if not self.updated: return
        self.trace.write(struct.pack('<I', self.nsteps))
        self.trace.write(struct.pack('<I', len(self.updated)))
        for a in sorted(self.updated):
            self.trace.write(struct.pack('<I', a))
            self.trace.write(struct.pack('<d', self.actuators[a]))

    def write_trace_end(self):
        self.trace.write(struct.pack('<I', self.nsteps))
        self.trace.write(struct.pack('<I', 0))

    # Interpret instructions

    def disassemble(self):
        for addr, insn in enumerate(self.insns):
            self.show(addr, insn)

    def show(self, addr, insn):
        print ('%5d %10g %-30s %08x'
               % (addr, self.data[addr], self.disassemble1(insn), insn))

    def step(self):
        for pc, insn in enumerate(self.insns):
            if self.loud: self.show(pc, insn)
            if insn_kind(insn) == 'S':
                self.do_S(pc, insn)
            else:
                self.do_D(pc, insn)
        self.end_step()
        self.updated.clear()
        self.nsteps += 1

    def end_step(self):
        if self.loud: print 'step'
        if self.trace:
            self.write_trace_frame()

    def disassemble1(self, insn):
        if insn_kind(insn) == 'S':
            return self.disassemble_S(insn)
        else:
            return self.disassemble_D(insn)

    def disassemble_S(self, insn):
        op, r1 = decode_S(insn)
        if op == 0: return 'noop'
        if op == 1: return self.disassemble_cmp(insn, r1)
        if op == 2: return 'sqrt M[%d]' % r1
        if op == 3: return 'M[%d]' % r1
        if op == 4: return 'read %d' % r1
        assert False

    def do_S(self, pc, insn):
        op, r1 = decode_S(insn)
        if   op == 0: pass
        elif op == 1: self.do_cmp(insn, r1)
        elif op == 2: self.set(pc, math.sqrt(self.get(r1)))
        elif op == 3: self.set(pc, self.get(r1))
        elif op == 4: self.set(pc, self.input(r1))
        else:         assert False

    def disassemble_cmp(self, insn, r1):
        cmpi = field(insn, 23, 21)
        cmp = '< <= = >= >'.split()[cmpi]
        return 'status = (M[%d] %s 0.0)' % (r1, cmp)

    def do_cmp(self, insn, r1):
        cmpi = field(insn, 23, 21)
        if   cmpi == 0: self.status = (self.get(r1) <  0.0)
        elif cmpi == 1: self.status = (self.get(r1) <= 0.0)
        elif cmpi == 2: self.status = (self.get(r1) == 0.0)
        elif cmpi == 3: self.status = (self.get(r1) >= 0.0)
        elif cmpi == 4: self.status = (self.get(r1) >  0.0)
        else: assert False

    def disassemble_D(self, insn):
        op, r1, r2 = decode_D(insn)
        if op == 1: return 'M[%d] + M[%d]' % (r1, r2)
        if op == 2: return 'M[%d] - M[%d]' % (r1, r2)
        if op == 3: return 'M[%d] * M[%d]' % (r1, r2)
        if op == 4: return 'M[%d] / M[%d]' % (r1, r2)
        if op == 5: return 'write %d <- M[%d]' % (r1, r2)
        if op == 6: return 'status ? M[%d] : M[%d]' % (r1, r2)
        assert False

    def do_D(self, pc, insn):
        op, r1, r2 = decode_D(insn)
        if   op == 1: self.set(pc, self.get(r1) + self.get(r2))
        elif op == 2: self.set(pc, self.get(r1) - self.get(r2))
        elif op == 3: self.set(pc, self.get(r1) * self.get(r2))
        elif op == 4: self.set(pc, self.get(r1) / self.get(r2)
                               if self.get(r2) != 0.0
                               else 0.0)
        elif op == 5: self.output(r1, self.get(r2))
        elif op == 6: self.set(pc, self.get(r1)
                               if self.status
                               else self.get(r2))
        else:         assert False

    def get(self, addr):
        return self.data[addr] if addr < len(self.data) else 0.0

    def set(self, pc, value):
        self.data[pc] = value
        if self.loud: print 'set %d = %g' % (pc, value)

    # Sense/act

    def output(self, sensor, value):
        self.sensors[sensor] = value
        if self.loud: print 'sensor %d <- %g' % (sensor, value)

    def input(self, actuator):
        return self.actuators[actuator]

    def actuate(self, actuator, value):
        value = float(value)
        if value != self.actuators.get(actuator):
            self.updated.add(actuator)
        self.actuators[actuator] = value


def insn_kind(insn):
    return 'S' if field(insn, 31, 28) == 0 else 'D'

def decode_S(insn):
    return field(insn, 27, 24), field(insn, 13, 0)

def decode_D(insn):
    return field(insn, 31, 28), field(insn, 27, 14), field(insn, 13, 0)

def field(u32, hi, lo):
    return (u32 >> lo) & ((1 << (hi + 1 - lo)) - 1)


if __name__ == '__main__':
    main()
