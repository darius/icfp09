import struct
import sys

def main():
    assert 2 == len(sys.argv)
    stem = sys.argv[1]
    compile(open('%s.py' % stem, 'w'),
            open('%s.c' % stem, 'w'),
            open('obf/%s.obf' % stem, 'rb'))

def compile(pyfile, cfile, infile):
    insns = []
    data = []
    for frame in range(2**14):
        bytes = infile.read(12)
        if not bytes: break
        if frame % 2 == 0:
            d, i = bytes[:8], bytes[8:]
        else:
            i, d = bytes[:4], bytes[4:]
        insns.append(struct.unpack('<I', i)[0])
        data.append(d)
    write_data(make_writer(pyfile), data)
    write_code(make_writer(cfile), insns)

def make_writer(file):
    def write(format, *args):
        print >>file, format % args
    return write

def write_data(out, data):
    out('import struct')
    out('def unpack(b): return struct.unpack("<d", b)[0]')
    out('data = map(unpack, %r)', data)

def write_code(out, insns):
    out('#include <math.h>')
    out('')
    out('int step(double *M,')
    out('         double *sensors,')
    out('         double *actuators,')
    out('         int *pstatus) {')
    out('  int status = *pstatus;')
    # This compiler does one optimization of its own: it keeps only
    # forward-referenced variables in the M array. The others become
    # local variables in the C code.
    local_vars = set()
    state_vars = set()
    for pc, insn in enumerate(insns):
        compile1(out, pc, insn, local_vars, state_vars)
    out('  *pstatus = status;')
    out('  return 0;')
    out('}')

def compile1(out, pc, insn, local_vars, state_vars):
    def assign(format, *args):
        if pc in state_vars:
            out('  M[%d] = (%s);', pc, format % args)
        else:
            local_vars.add(pc)
            out('  double v%d = (%s);', pc, format % args)
    def M(v):
        if pc <= v: state_vars.add(v)
        return ('v%d' if v in local_vars else 'M[%d]') % v
    op = field(insn, 31, 28)
    if op == 0:
        op = field(insn, 27, 24)
        r1 = field(insn, 13, 0)
        def compile_cmp():
            relation = '< <= == >= >'.split()[field(insn, 23, 21)]
            out('  status = (%s %s 0.0);', M(r1), relation)
        if   op == 0: pass
        elif op == 1: compile_cmp()
        elif op == 2: assign('sqrt(%s)', M(r1))
        elif op == 3: assign('%s', M(r1))
        elif op == 4: assign('actuators[%d]', r1)
        else:         assert False
    else:
        r1 = field(insn, 27, 14)
        r2 = field(insn, 13, 0)
        if   op == 1: assign('%s + %s', M(r1), M(r2))
        elif op == 2: assign('%s - %s', M(r1), M(r2))
        elif op == 3: assign('%s * %s', M(r1), M(r2))
        elif op == 4: assign('%s == 0.0 ? 0.0 : %s / %s', M(r2), M(r1), M(r2))
        elif op == 5: out('  sensors[%d] = %s;', r1, M(r2))
        elif op == 6: assign('status ? %s : %s', M(r1), M(r2))
        else:         assert False

def field(u32, hi, lo):
    return (u32 >> lo) & ((1 << (hi + 1 - lo)) - 1)


if __name__ == '__main__':
    main()
