import struct
import sys

def main():
    assert 2 == len(sys.argv)
    stem = sys.argv[1]
    compile(open(stem + '.py', 'w'),
            open(stem + '.c', 'w'),
            open(stem + '.obf', 'rb'))

insns = []
data = []

def compile(pyfile, cfile, f):
    for frame in range(2**14):
        bytes = f.read(12)
        if not bytes: break
        if frame % 2 == 0:
            d, i = struct.unpack('<dI', bytes)
        else:
            i, d = struct.unpack('<Id', bytes)
        insns.append(i)
        data.append(d)
    write_data(pyfile)
    write_code(cfile)

def write_data(pyfile):
    print >>pyfile, 'data = %r' % data

def write_code(f):
    print >>f, '#include <math.h>'
    print >>f, ''
    print >>f, 'int step(double *M,'
    print >>f, '         double *sensors,'
    print >>f, '         double *actuators,'
    print >>f, '         int *status) {'
    for pc, insn in enumerate(insns):
        compile1(f, pc, insn)
    print >>f, '  return 0;'
    print >>f, '}'

# XXX the M[] refs must allow out of the initialized range, I think?

def compile1(f, pc, insn):
    def assign(expr):
        print >>f, '  M[%d] = %s;' % (pc, expr)
        #print >>f, '  printf("set %d = %%g\\n", M[%d]);' % (pc, pc)
    if insn_kind(insn) == 'S':
        op, r1 = decode_S(insn)
        def compile_cmp():
            cmpi = field(insn, 23, 21)
            cmp = '< <= == >= >'.split()[cmpi]
            print >>f, '  *status = (M[%d] %s 0.0);' % (r1, cmp)
        if   op == 0: pass
        elif op == 1: compile_cmp()
        elif op == 2: assign('sqrt(M[%d])' % r1)
        elif op == 3: assign('M[%d]' % r1)
        elif op == 4: assign(get_actuator(r1))
        else:         assert False
    else:
        op, r1, r2 = decode_D(insn)
        if   op == 1: assign('M[%d] + M[%d]' % (r1, r2))
        elif op == 2: assign('M[%d] - M[%d]' % (r1, r2))
        elif op == 3: assign('M[%d] * M[%d]' % (r1, r2))
        elif op == 4: assign('(M[%d] == 0.0 ? 0.0 : M[%d] / M[%d])'
                             % (r2, r1, r2))
        elif op == 5: print >>f, '  sensors[%d] = M[%d];' % (r1, r2)
        elif op == 6: assign('(*status ? M[%d] : M[%d])' % (r1, r2))
        else:         assert False

def get_actuator(r1):
    if r1 == 16000: return '1001.0' # XXX
    return 'actuators[%d]' % r1

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
