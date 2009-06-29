import math
import struct
import sys

scenario = None

insns = []
data = []

def load(filename):
    f = open(filename, 'rb')
    for frame in range(2**14):
        bytes = f.read(12)
        if not bytes: break
        if frame % 2 == 0:
            d, i = struct.unpack('<dI', bytes)
        else:
            i, d = struct.unpack('<Id', bytes)
        insns.append(i)
        data.append(d)

status = False

def main():
    assert 2 == len(sys.argv)
    load(sys.argv[1])
    disassemble()

def disassemble():
    for addr, insn in enumerate(insns):
        show(addr, insn)

def show(addr, insn):
    print ('%5d %10g %-30s %08x'
           % (addr, data[addr], disassemble1(insn), insn))

def step():
    for pc, insn in enumerate(insns):
        show(pc, insn)
        if insn_kind(insn) == 'S':
            do_S(pc, insn)
        else:
            do_D(pc, insn)

def disassemble1(insn):
    if insn_kind(insn) == 'S':
        return disassemble_S(insn)
    else:
        return disassemble_D(insn)

def disassemble_S(insn):
    op, r1 = decode_S(insn)
    if op == 0: return 'noop'
    if op == 1: return disassemble_cmp(insn, r1)
    if op == 2: return 'sqrt M[%d]' % r1
    if op == 3: return 'M[%d]' % r1
    if op == 4: return 'read %d' % r1
    assert False

def do_S(pc, insn):
    op, r1 = decode_S(insn)
    if   op == 0: pass
    elif op == 1: do_cmp(insn, r1)
    elif op == 2: update(pc, math.sqrt(get(r1)))
    elif op == 3: update(pc, get(r1))
    elif op == 4: update(pc, input(r1))
    else:         assert False

def disassemble_cmp(insn, r1):
    cmpi = field(insn, 23, 20)
    cmp = '< <= = >= >'.split()[cmpi]
    return 'status = (M[%d] %s 0.0)' % (r1, cmp)

def do_cmp(insn, r1):
    global status
    cmpi = field(insn, 23, 21)
    if   cmpi == 0: status = (get(r1) <  0.0)
    elif cmpi == 1: status = (get(r1) <= 0.0)
    elif cmpi == 2: status = (get(r1) == 0.0)
    elif cmpi == 3: status = (get(r1) >= 0.0)
    elif cmpi == 4: status = (get(r1) >  0.0)
    else: assert False

def disassemble_D(insn):
    op, r1, r2 = decode_D(insn)
    if op == 1: return 'M[%d] + M[%d]' % (r1, r2)
    if op == 2: return 'M[%d] - M[%d]' % (r1, r2)
    if op == 3: return 'M[%d] * M[%d]' % (r1, r2)
    if op == 5: return 'M[%d] / M[%d]' % (r1, r2)
    if op == 4: return 'write %d <- M[%d]' % (r1, r2)
    if op == 6: return 'status ? M[%d] : M[%d]' % (r1, r2)
    assert False

def do_D(pc, insn):
    op, r1, r2 = decode_D(insn)
    if   op == 1: update(pc, get(r1) + get(r2))
    elif op == 2: update(pc, get(r1) - get(r2))
    elif op == 3: update(pc, get(r1) * get(r2))
    elif op == 4: update(pc, get(r1) / get(r2) if get(r2) != 0.0 else 0.0)
    elif op == 5: output(r1, get(r2))
    elif op == 6: update(pc, get(r1) if status else get(r2))
    else:         assert False

def insn_kind(insn):
    return 'S' if field(insn, 31, 28) == 0 else 'D'

def decode_S(insn):
    return field(insn, 27, 24), field(insn, 13, 0)

def decode_D(insn):
    return field(insn, 31, 28), field(insn, 27, 14), field(insn, 13, 0)

def field(u32, hi, lo):
    return (u32 >> lo) & ((1 << (hi + 1 - lo)) - 1)

def get(addr):
    if addr < len(data):
        return data[addr]
    return 0.0

def update(pc, value):
    data[pc] = value
    print 'set %d = %g' % (pc, value)

def output(sensor, value):
    print 'sensor %d <- %g' % (sensor, value)

def input(actuator):
    # XXX hook this up to the scenario properly
    if actuator == 0x3E80:
        return scenario
    return 0.0

if __name__ == '__main__':
    main()
