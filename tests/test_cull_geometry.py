"""Conservative culling comparisons against the previous bounding-box predicate."""
import ctypes
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class Vertex(ctypes.Structure):
    _fields_ = [('t', ctypes.c_float * 2), ('c', ctypes.c_float * 4),
                ('n', ctypes.c_float * 3), ('v', ctypes.c_float * 3)]


class CullGeometryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        source = Path(cls.tmp.name) / 'check.c'
        source.write_text(r'''
#include "cull_geometry.h"
#include <stdint.h>
int check(const double *m, const MuglCullVertex *v, int n, int probes) {
    return mugl_cull_geometry(m, v, n, probes);
}
/* Independent scalar form of the original full-box predicate. */
static unsigned old_code(const double *m, const float *p) {
    double c[4];
    for (int r=0;r<4;r++) c[r]=m[r]*p[0]+m[r+4]*p[1]+m[r+8]*p[2]+m[r+12];
    double e=1e-5*(1+fabs(c[0])+fabs(c[1])+fabs(c[3]));
    return (unsigned)(c[0]>c[3]+e) | (unsigned)(c[0]<-c[3]-e)<<1 |
           (unsigned)(c[1]>c[3]+e)<<2 | (unsigned)(c[1]<-c[3]-e)<<3 | (unsigned)(c[3]<-e)<<4;
}
static int reference(const double *m, const MuglCullVertex *v, int n) {
    if (n<3 || !old_code(m,v[0].v)) return 0;
    float lo[3],hi[3];
    for(int j=0;j<3;j++) lo[j]=hi[j]=v[0].v[j];
    for(int i=0;i<n;i++) for(int j=0;j<3;j++) {
        float x=v[i].v[j]; if(isnan(x)) return 0;
        if(x<lo[j])lo[j]=x; if(x>hi[j])hi[j]=x;
    }
    unsigned all=31;
    for(int k=0;k<8;k++){float p[3]={k&1?hi[0]:lo[0],k&2?hi[1]:lo[1],k&4?hi[2]:lo[2]};all &= old_code(m,p);}
    return all!=0;
}
static uint32_t state=1701;
static float random_value(void) {
    state ^= state<<13; state ^= state>>17; state ^= state<<5;
    return ((state & 65535) / 65535.f - .5f)*8;
}
int random_comparisons(int count) {
    MuglCullVertex vertices[192] = {0};
    state=1701;
    for(int c=0;c<count;c++) {
        double m[16]={0}; m[0]=m[5]=m[10]=1; m[15]=1;
        m[3]=random_value()*.1; m[7]=random_value()*.1; m[11]=random_value()*.1;
        m[12]=random_value(); m[13]=random_value();
        int n=3+c%190;
        float center[3]={random_value(),random_value(),random_value()};
        for(int i=0;i<n;i++)for(int j=0;j<3;j++)vertices[i].v[j]=center[j]+random_value()*.3f;
        if(c%5==0) vertices[n/2].v[c%3]=NAN;
        if(c%11==0) vertices[n-1].v[c%3]=INFINITY;
        int expected=reference(m,vertices,n);
        if(expected!=mugl_cull_geometry(m,vertices,n,0) || expected!=mugl_cull_geometry(m,vertices,n,1))return c+1;
    }
    return 0;
}
''')
        lib = Path(cls.tmp.name) / 'check.so'
        subprocess.run(['clang', '-O2', '-ffp-contract=off', '-std=c11', '-shared', '-fPIC',
                        '-Wall', '-Wextra', '-Werror', '-I', str(ROOT / 'mac-play/hotpatch'),
                        str(source), '-o', str(lib)], check=True)
        cls.lib = ctypes.CDLL(str(lib))
        cls.lib.check.argtypes = [ctypes.POINTER(ctypes.c_double), ctypes.POINTER(Vertex), ctypes.c_int, ctypes.c_int]
        cls.lib.check.restype = ctypes.c_int
        cls.lib.random_comparisons.argtypes = [ctypes.c_int]
        cls.lib.random_comparisons.restype = ctypes.c_int

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def check(self, points, expected):
        matrix = (ctypes.c_double * 16)(1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1)
        v = (Vertex * len(points))()
        for vertex, point in zip(v, points):
            vertex.v[:] = point
        for probes in [0, 1]:
            self.assertEqual(self.lib.check(matrix, v, len(v), probes), expected)

    def test_edge_crossing_and_small_batches(self):
        for size in [3, 127, 128, 690]:
            with self.subTest(size=size):
                points = [(2, 0, 0)] * size
                self.check(points, 1)
                points[size // 2] = (0, 0, 0)
                self.check(points, 0)
                points[size // 2] = (2, 0, 0)
                points[-1] = (0, 0, 0)
                self.check(points, 0)

    def test_visible_box_without_inside_vertices(self):
        self.check([(-2, -2, 0), (2, -2, 0), (0, 2, 0)] * 64, 0)

    def test_nonfinite_and_clip_plane_margin(self):
        for x in [float('nan'), float('inf'), -float('inf')]:
            points = [(2, 0, 0)] * 192
            points[96] = (x, 0, 0)
            self.check(points, 0)
        self.check([(1.000001, 0, 0)] * 192, 0)
        self.check([(1.001, 0, 0)] * 192, 1)

    def test_100000_seeded_reference_comparisons(self):
        self.assertEqual(self.lib.random_comparisons(100000), 0)


if __name__ == '__main__':
    unittest.main()
