"""
Command-line option parser, because I'm too lazy for optparse's set-up.
Example:

import clop
options = clop.parse('bin_name scenario:int')
print options.bin_name, options.scenario

TODO: implement as a wrapper around optparse?
"""

import sys


def parse(spec, argv=None):
    if argv is None: argv = sys.argv
    vars = spec.split()
    if len(vars) != len(argv[1:]):
        print >>sys.stderr, 'Usage: %s %s' % (argv[0], spec)
        sys.exit(1)
    result = dict(map(parse_arg, zip(vars, argv[1:])))
    return Struct(**result)

def parse_arg((spec, string)):
    if ':' in spec:
        name, typename = spec.split(':')
        type_ = parse_type(typename)
        try:
            value = type_(string)
        except ValueError:
            XXX
    else:
        name = spec
        value = string
    return name, value

def parse_type(spec):
    if spec == 'int': return int
    assert False

class Struct:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


## options = parse('bin_name scenario:int', 'program bin1 42'.split())
## options.bin_name, options.scenario
#. ('bin1', 42)
