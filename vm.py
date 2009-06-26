import math
import struct

def read_uint(f):
    chars = f.read(4)
    if not chars: return None
    return struct.unpack('<I', chars)[0]

def read_double(f):
    chars = f.read(8)
    if not chars: return None
    return struct.unpack('<d', chars)[0]

insns = []
data = []
f = open('bin1.obf', 'rb')
for frame in range(2**14):
    if frame % 2 == 0:          # WTF is this randomness?
        d = read_double(f)
        i = read_uint(f)
    else:
        i = read_uint(f)
        d = read_double(f)
    if i is None and d is None:
        break
    insns.append(i)
    data.append(d)

def field(u32, hi, lo):
    return (u32 >> lo) & ((1 << (hi + 1 - lo)) - 1)

def decode(insn):
    op = field(insn, 31, 28)
    if op == 0:
        return 'S', field(insn, 27, 24), field(insn, 23, 14), field(insn, 13, 0)
    if 1 <= op <= 6:
        return 'D', op, field(insn, 27, 14), field(insn, 13, 0)
    assert False

def disassemble1(insn):
    sd, _, __, ___ = decode(insn)
    if sd == 'S':
        _, op, imm, r1 = decode(insn)
        if op == 0: return 'noop'
        if op == 1:
            cmpi = field(insn, 23, 20)
            cmp = '< <= = >= >'.split()[cmpi] # XXX boundscheck
            return 'status = (M[%d] %s 0.0)' % (r1, cmp)
        if op == 2: return 'sqrt M[%d]' % r1
        if op == 3: return 'M[%d]' % r1
        if op == 4: return 'read %d' % r1
        return 'XXX %d' % op
    if sd == 'D':
        _, op, r1, r2 = decode(insn)
        if op == 1: return 'M[%d] + M[%d]' % (r1, r2)
        if op == 2: return 'M[%d] - M[%d]' % (r1, r2)
        if op == 3: return 'M[%d] * M[%d]' % (r1, r2)
        if op == 4: return 'write %d <- M[%d]' % (r1, r2)
        if op == 5: return 'M[%d] + M[%d]' % (r1, r2)
        if op == 6: return 'status ? M[%d] : M[%d]' % (r1, r2)
    assert False

def disassemble():
    for addr, insn in enumerate(insns):
        show(addr, insn)

def show(addr, insn):
    print ('%5d %10g %-30s %08x'
           % (addr, data[addr], disassemble1(insn), insn))

scenario = 1001.0

# Sensor ports
s_score, s_fuel, s_sx, s_sy, s_tx, s_ty = range(6)

# Actuator ports
a_dvx, a_dvy, a_config = 2, 3, 0x3E80

status = False

def step():
    for pc, insn in enumerate(insns):
        show(pc, insn)
        sd, _, __, ___ = decode(insn)
        if sd == 'S':
            s_insn(pc, insn)
        elif sd == 'D':
            d_insn(pc, insn)
        else:
            assert False

def get(addr):
    if addr < len(data):
        return data[addr]
    return 0.0

def update(pc, value):
    data[pc] = value
    print 'set %d = %g' % (pc, value)

def d_insn(pc, insn):
    _, op, r1, r2 = decode(insn)
    if op == 1:
        update(pc, get(r1) + get(r2))
    elif op == 2:
        update(pc, get(r1) - get(r2))
    elif op == 3:
        update(pc, get(r1) * get(r2))
    elif op == 4:
        output(r1, get(r2))
    elif op == 5:
        update(pc, get(r1) / get(r2) if get(r2) != 0.0 else 0.0)
    elif op == 6:
        update(pc, get(r1) if status else get(r2))
    else:
        assert False

def s_insn(pc, insn):
    _, op, imm, r1 = decode(insn)
    if op == 0:
        return
    m = get(r1)
    if op == 1:
        global status
        cmpi = field(insn, 23, 20)
        if   cmpi == 0: status = (m <  0.0)
        elif cmpi == 1: status = (m <= 0.0)
        elif cmpi == 2: status = (m == 0.0)
        elif cmpi == 3: status = (m >= 0.0)
        elif cmpi == 4: status = (m >  0.0)
        else: assert False
    elif op == 2:
        update(pc, math.sqrt(m))
    elif op == 3:
        update(pc, m)
    elif op == 4:
        update(pc, input(r1))
    else:
        assert False

def output(sensor, value):
    print 'sensor %d <- %g' % (sensor, value)

def input(actuator):
    if actuator == a_dvx:
        return 0.0
    if actuator == a_dvy:
        return 0.0
    if actuator == a_config:
        return scenario
    assert False

if __name__ == '__main__':
#    disassemble()
    step()
