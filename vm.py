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

## field(0xab7d, 7, 4)
#. 7

def decode(insn):
    op = field(insn, 31, 28)
    if op == 0:
#        return 'S', (insn >> 24) & 0xF, (insn >> 14) & 0x
        return 'S', field(insn, 27, 24), field(insn, 23, 14), field(insn, 13, 0)
    if 1 <= op <= 6:
#        return 'D', op, (insn >> 14) & 0x003F, insn & 0x003F...
        return 'D', op, field(insn, 27, 14), field(insn, 13, 0)
    assert False

## decode(insns[1])
#. ('S', 3, 0, 265)

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

for addr, insn in enumerate(insns):
    print '%5d %08x %s' % (addr, insn, disassemble1(insn))

## ' '.join('%08x' % i for i in insns)
#. '00000000 03000109 00000000 00000000 030000f8 20010003 01400005 60008001 2001c000 03000107 01400005 60000009 2002c000 0140000c 60020007 03000108 00000000 01400005 6004000f 00000000 30048013 0140000c 60050012 0140000c 6004800c 03000104 03000106 00000000 00000000 30070010 4007401b 00000000 04003e80 2008001f 01400021 60078003 00000000 40074024 00000000 20080026 01400027 60094023 40074013 00000000 2008002b 0140002c 600a8029 00000000 2008002f 01400030 6007402e 01400005 600c801a 030000ff 00000000 00000000 01400021 600dc003 01400027 600d8039 00000000 0140002c 600f003b 01400030 600d803e 01400005 60100035 030000fa 01400005 6000c043 20114042 30118046 030000f9 01400005 6000c048 030000fe 01400021 600d8003 00000000 01400027 6013804d 00000000 0140002c 60144050 00000000 01400030 60150053 01400005 6015804b 20128058 30164059 10168047 0200005b 3017005c 3017405c 030000fb 00000000 01400005 6018005f 00000000 3018c062 4019005e 30118065 04000003 40000000 4019c068 101a4066 301a0068 401ac013 301a806c 03000102 00000000 01400027 601bc04d 00000000 0140002c 601c8071 00000000 01400030 601d4074 01400005 601dc06e 301e4068 1010807a 101ec06d 201f0045 301f407d 30164065 04000002 40200068 1020407f 3020806c 03000101 00000000 01400021 60214003 01400027 600d8087 0140002c 601c8089 01400030 600d808b 01400005 60234084 3023c068 10160090 10244083 2024804a 3024c093 1025007e 02000095 20258034 2000c097 2025c003 01000099 60260097 1006409b 301a4069 30204081 1027809d 0200009f 20280003 014000a1 60270003 2026c010 010000a4 6028c003 2011407c 3029c0a7 20128092 302a40a9 102a80a8 020000ab 302b00ac 302b40ac 401900ae 3029c0af 102c0066 402c4013 101a40b2 302cc068 101e40b4 302a40af 102d807f 402dc013 102040b8 302e4068 1023c0ba 03000100 00000000 01400021 602f4003 01400027 602f40bf 0140002c 602f40c1 01400030 602f40c3 01400005 603140bc 030000fd 01400005 6000c0c8 030000fc 01400005 6000c0cb 10010000 03000103 1033c000 014000a1 60340003 010000a4 60348003 03000105 00000000 01400005 603580d5 30280068 203600d9 00000000 00000000 203580da 403740d6 303780dc 1001c0df 103800db 00000000 40388068 2038c0d4 010000e4 60384003 20368003 203c8000 010000e7 603a00e6 203580d9 010000eb 603a00ea 00000000 202580ee 010000ef 603a00ed 00000000 500000f1 500040da 500080a9 5000c0a7 50010034 030000ce 0300004a 03000045 03000062 030000cd 030000ca 03000092 0300007c 030000c7 030000bb 030000b5 030000d4 030000a6 030000da 03000034 03000018 03000016 0300000e'

## data
#. [1.0, 0.0, 30.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1000.0, 0.0, 0.0, 2.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.1000000000000001, 42164.0, 0.0, 0.0, 1004.0, 0.0, 0.0, 0.0, 0.0, 1.5, 0.0, 1003.0, 0.0, 0.0, 0.0, 0.0, 1002.0, 0.0, 0.0, 0.0, 1001.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 6457000.0, 0.0, 0.0, 0.0, 0.0, -6357000.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 8357000.0, 0.0, 0.0, 6357000.0, 0.0, 0.0, 6557000.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 5.9999999999999999e+24, 0.0, 0.0, 6.6742799999999995e-11, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -6922.3353585219347, 0.0, 0.0, -4719.3179090671219, 0.0, 0.0, -7814.9327385133756, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -7875.2154332354548, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 10000.0, 0.0, 0.0, 0.0, 0.0, 25.0, 45.0, 0.0, 0.0, 0.0, 0.0, 0.0, 900.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 6357000.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
