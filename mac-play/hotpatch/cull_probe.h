/* SPDX-License-Identifier: MIT
 * Conservative early acceptance for large batches whose first vertex is clipped.
 * An inside vertex prevents the existing whole-box test from rejecting the batch.
 * This only skips the expensive box scan; it never rejects geometry.
 */
#ifndef MUGL_CULL_PROBE_H
#define MUGL_CULL_PROBE_H
#include <math.h>
#include <stddef.h>

static unsigned mugl_clip_code(const double *m, const float *p)
{
    double c[4];
    for (int r = 0; r < 4; r++)
        c[r] = m[r] * p[0] + m[4 + r] * p[1] + m[8 + r] * p[2] + m[12 + r];
    double e = 1e-5 * (1.0 + fabs(c[0]) + fabs(c[1]) + fabs(c[3]));
    return (unsigned)(c[0] > c[3] + e) | (unsigned)(c[0] < -c[3] - e) << 1 |
           (unsigned)(c[1] > c[3] + e) << 2 | (unsigned)(c[1] < -c[3] - e) << 3 |
           (unsigned)(c[3] < -e) << 4;
}

static int mugl_cull_visible_probe(const double *m, const void *positions, size_t stride, int count)
{
    if (count < 128) return 0;  /* small sprite/triangle batches keep the old path */
    const char *p = (const char *)positions;
    return !mugl_clip_code(m, (const float *)(p + (size_t)(count / 2) * stride)) ||
           !mugl_clip_code(m, (const float *)(p + (size_t)(count - 1) * stride));
}
#endif
