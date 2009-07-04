bins = ['bin%d' % i for i in range(1, 6)]

# XXX the dylib stuff is OS-X-specific:

template = """\
CFLAGS := -g2 -O2 -Wall -W -fPIC -fno-common
DLIBFLAGS := -dynamiclib -undefined dynamic_lookup -single_module

all: %(dylibs)s

clean:
	rm -f *.o *.so *.dylib dbg bin?.[co] bin?.py*

%(clauses)s
"""

def rules(bin_name):
    return """\
%.dylib: %.o
	gcc $(DLIBFLAGS) -o %.dylib %.o

%.o: %.c

%.c: obf/%.obf compile.py
	python compile.py %
""".replace('%', bin_name)

dylibs = ' '.join('%s.dylib' % b for b in bins)
clauses = '\n\n'.join(rules(b) for b in bins)

print template % dict(dylibs=dylibs, clauses=clauses)
