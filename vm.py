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
        print ('%5d %10g %-30s %08x'
               % (addr, data[addr], disassemble1(insn), insn))

if __name__ == '__main__':
    disassemble()
