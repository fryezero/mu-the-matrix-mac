/* SPDX-License-Identifier: MIT
 * Copyright (c) 2026 Frye
 * Authored self-check for the fast x87 translator. See ../LICENSE.
 *
 * An x86_64 macOS program, so it runs under Rosetta without Wine. mu-launch.sh runs it through
 * rosetta-timewalker's runtime_loader after macOS, Rosetta or the translator changed: the translator must report
 * that it was built ("RosettaRuntimex87 built") and every x87 result below must be exact. All values are exactly
 * representable in double precision, so the check does not depend on 80-bit intermediate precision.
 */
#include <stdint.h>
#include <stdio.h>
#include <string.h>

static uint64_t double_bits(double value)
{
    uint64_t bits;
    memcpy(&bits, &value, sizeof(bits));
    return bits;
}

__attribute__((noinline)) static double load_m32(float source)
{
    double result;
    __asm__ volatile("flds %1\n\tfstpl %0" : "=m"(result) : "m"(source));
    return result;
}

__attribute__((noinline)) static double sqrt_add(double square, double addend)
{
    double result;
    __asm__ volatile("fldl %1\n\tfsqrt\n\tfldl %2\n\tfaddp\n\tfstpl %0"
                     : "=m"(result) : "m"(square), "m"(addend));
    return result;
}

__attribute__((noinline)) static int32_t round_to_int(double value)
{
    int32_t result;
    __asm__ volatile("fldl %1\n\tfistpl %0" : "=m"(result) : "m"(value));
    return result;
}

/* long double is the 80-bit x87 type on x86_64 macOS: a translated loop, not just single instructions. */
__attribute__((noinline)) static long double half_sum(int count)
{
    long double sum = 0.0L;
    for (int i = 0; i < count; ++i)
        sum += (long double)i * 0.5L;
    return sum;
}

int main(void)
{
    int failures = 0;
    double a = load_m32(1.5f);
    double b = sqrt_add(6.25, 0.75);
    int32_t c = round_to_int(4.25);
    long double d = half_sum(1000);

    failures += double_bits(a) != UINT64_C(0x3ff8000000000000);
    failures += double_bits(b) != UINT64_C(0x400a000000000000);
    failures += c != 4;
    failures += (double)d != 249750.0;
    printf("x87 smoke: %s (fld %.17g, fsqrt+fadd %.17g, fistp %d, loop %.17g)\n",
           failures ? "FAIL" : "PASS", a, b, (int)c, (double)d);
    return failures ? 1 : 0;
}
