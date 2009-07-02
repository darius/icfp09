import struct
import sys

def main():
    assert 2 == len(sys.argv)
    stem = sys.argv[1]
    compile(open(stem + '.py', 'w'),
            open(stem + '.c', 'w'),
            open(stem + '.obf', 'rb'))

def compile(pyfile, cfile, f):
    insns = []
    data = []
    for frame in range(2**14):
        bytes = f.read(12)
        if not bytes: break
        if frame % 2 == 0:
            d, i = bytes[:8], bytes[8:]
        else:
            i, d = bytes[:4], bytes[4:]
        insns.append(struct.unpack('<I', i)[0])
        data.append(d)
    write_data(pyfile, data)
    write_code(cfile, insns)

def write_data(pyfile, data):
    print >>pyfile, 'import struct'
    print >>pyfile, 'def unpack(b): return struct.unpack("<d", b)[0]'
    print >>pyfile, 'data = map(unpack, %r)' % data

def write_code(f, insns):
    print >>f, '#include <math.h>'
    print >>f, ''
    print >>f, 'int step(double *M,'
    print >>f, '         double *sensors,'
    print >>f, '         double *actuators,'
    print >>f, '         int *pstatus) {'
    print >>f, '  int status = *pstatus;'
    for pc, insn in enumerate(insns):
        compile1(f, pc, insn)
    print >>f, '  *pstatus = status;'
    print >>f, '  return 0;'
    print >>f, '}'

def compile1(f, pc, insn):
    def assign(expr):
        print >>f, '  M[%d] = %s;' % (pc, expr)
    op = field(insn, 31, 28)
    if op == 0:
        op = field(insn, 27, 24)
        r1 = field(insn, 13, 0)
        def compile_cmp():
            cmpi = field(insn, 23, 21)
            cmp = '< <= == >= >'.split()[cmpi]
            print >>f, '  status = (M[%d] %s 0.0);' % (r1, cmp)
        if   op == 0: pass
        elif op == 1: compile_cmp()
        elif op == 2: assign('sqrt(M[%d])' % r1)
        elif op == 3: assign('M[%d]' % r1)
        elif op == 4: assign('actuators[%d]' % r1)
        else:         assert False
    else:
        r1 = field(insn, 27, 14)
        r2 = field(insn, 13, 0)
        if   op == 1: assign('M[%d] + M[%d]' % (r1, r2))
        elif op == 2: assign('M[%d] - M[%d]' % (r1, r2))
        elif op == 3: assign('M[%d] * M[%d]' % (r1, r2))
        elif op == 4: assign('(M[%d] == 0.0 ? 0.0 : M[%d] / M[%d])'
                             % (r2, r1, r2))
        elif op == 5: print >>f, '  sensors[%d] = M[%d];' % (r1, r2)
        elif op == 6: assign('(status ? M[%d] : M[%d])' % (r1, r2))
        else:         assert False

def field(u32, hi, lo):
    return (u32 >> lo) & ((1 << (hi + 1 - lo)) - 1)


if __name__ == '__main__':
    main()
