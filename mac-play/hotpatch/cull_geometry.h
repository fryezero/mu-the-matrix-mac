/* SPDX-License-Identifier: MIT
 * GL-only batch visibility kernel, shared by the proxy and offline diagnostics.
 * No game addresses, state reads, executable patches or gameplay inputs.
 */
#ifndef MUGL_CULL_GEOMETRY_H
#define MUGL_CULL_GEOMETRY_H
#include "cull_probe.h"
#if defined(__SSE__)
#include <xmmintrin.h>
#endif

typedef struct { float t[2], c[4], n[3], v[3]; } MuglCullVertex;

/* probes=0 retains the original full-scan path for diagnostic comparisons.
 * Return 1 only when the whole batch is outside one of the existing clip planes.
 */
static int mugl_cull_geometry(const double *m, const MuglCullVertex *v, int n, int probes)
{
    if (n < 3 || !mugl_clip_code(m, v[0].v)) return 0;
    if (probes && mugl_cull_visible_probe(m, v[0].v, sizeof(*v), n)) return 0;
    float l[3], h[3];
#if defined(__SSE__)
    /* n[2] plus v[0..2] fills one legal 16-byte load; ignore the normal lane. */
    __m128 lo = _mm_loadu_ps(&v[0].n[2]), hi = lo, bad = _mm_cmpunord_ps(lo, lo);
    for (int i = 1; i < n; i++) {
        __m128 p = _mm_loadu_ps(&v[i].n[2]);
        lo = _mm_min_ps(lo, p); hi = _mm_max_ps(hi, p);
        bad = _mm_or_ps(bad, _mm_cmpunord_ps(p, p));
    }
    if (_mm_movemask_ps(bad) & 14) return 0;
    float a[4], b[4]; _mm_storeu_ps(a, lo); _mm_storeu_ps(b, hi);
    for (int k = 0; k < 3; k++) { l[k] = a[k + 1]; h[k] = b[k + 1]; }
#else
    /* Portable tests exercise the same predicate; Wine builds use SSE above. */
    for (int k = 0; k < 3; k++) l[k] = h[k] = v[0].v[k];
    for (int i = 0; i < n; i++) for (int k = 0; k < 3; k++) {
        float p = v[i].v[k];
        if (isnan(p)) return 0;
        if (p < l[k]) l[k] = p;
        if (p > h[k]) h[k] = p;
    }
#endif
    unsigned all = 31;
    for (int k = 0; all && k < 8; k++) {
        float p[3] = { k & 1 ? h[0] : l[0], k & 2 ? h[1] : l[1], k & 4 ? h[2] : l[2] };
        all &= mugl_clip_code(m, p);
    }
    return all != 0;
}
#endif
