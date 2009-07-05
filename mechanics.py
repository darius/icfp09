from math import acos, atan2, cos, hypot, pi, sin, sqrt

GM = 6.67428e-11 * 6.0e24

one_degree = pi / 180.0


origin = (0., 0.)

def magnitude((x, y)):       return hypot(x, y)
def angle((x, y)):           return atan2(y, x)

def vnegate((x, y)):         return (-x, -y)
def vscale(c, (x, y)):       return (c*x, c*y)

def vadd((x0,y0), (x1,y1)):  return (x0+x1, y0+y1)
def vsub((x0,y0), (x1,y1)):  return (x0-x1, y0-y1)

def vaverage(v0, v1):        return vscale(0.5, vadd(v0, v1))

def dot((x0,y0), (x1,y1)):   return x0 * x1 + y0 * y1
def cross((x0,y0), (x1,y1)): return x0 * y1 - x1 * y0

def vdirection(v):           return vscale(1. / magnitude(v), v)

def relative_angle(v0, v1):
    return atan2(cross(v0, v1), dot(v0, v1))


def rotate((x,y), a):
    ca, sa = cos(a), sin(a)
    return (ca * x - sa * y, sa * x + ca * y)

def angles_approx_equal(a1, a2, tolerance):
    a = range_reduce(a1 - a2)
    mag_a = min(a, 2*pi - a)
    return mag_a < tolerance

def range_reduce(a):
    while a < 0:     a += 2*pi
    while 2*pi <= a: a -= 2*pi
    assert 0 <= a < 2*pi
    return a


def calculate_hohmann_transfer(r1, r2):
    dv_depart = sqrt(GM / r1) * (sqrt(2 * r2 / (r1 + r2)) - 1)
    dv_arrive = sqrt(GM / r2) * (1 - sqrt(2 * r1 / (r1 + r2)))
    t_coast   = pi * (r1 + r2) * sqrt((r1 + r2) / (8*GM))
    return dv_depart, t_coast, dv_arrive

def compute_rendezvous(r0, v0, rt, vt):
    """Compute two successive burns that take us from the state
    (r0, v0) to the state (rt, vt) (approximately)."""
    U = vsub(rt, vadd(r0, vscale(2., vadd(v0, gravity(r0)))))
    V = vsub(vt, vadd(v0, vscale(2., gravity(r0))))
    B0 = vsub(U, vscale(0.5, V))
    B1 = vsub(vscale(1.5, V), U)
    return B0, B1


def gravity(r):
    return vscale(-GM / magnitude(r)**3, r)

def tick(r, v, B):
    """Compute next position and velocity, given current position,
    velocity, and boost."""
    rn = vadd(r, vadd(v, vscale(0.5, vadd(B, gravity(r)))))
    vn = vadd(v, vadd(B, vaverage(gravity(r), gravity(rn))))
    return rn, vn

def infer_v(rp, Bp, r):
    """Compute current velocity given previous position, previous
    boost, and current position."""
    return vadd(vsub(r, rp), vscale(0.5, vadd(gravity(r), Bp)))
