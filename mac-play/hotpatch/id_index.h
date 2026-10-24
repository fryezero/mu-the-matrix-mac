/* SPDX-License-Identifier: MIT
 * Append-only GLuint-name index. Rows in the existing buffer tables never move
 * or disappear, including after glDeleteBuffers; only their contents reset.
 * Zero is the GL default binding and is not a named buffer. Table sizes are
 * nonzero powers of two, twice the corresponding row capacity.
 */
#ifndef MUGL_ID_INDEX_H
#define MUGL_ID_INDEX_H
#include <stddef.h>
#include <stdint.h>
typedef struct { uint32_t key; int row; } MuglIdEntry;

static size_t mugl_id_hash(uint32_t id, size_t size)
{
    id ^= id >> 16; id *= UINT32_C(0x7feb352d);
    id ^= id >> 15; id *= UINT32_C(0x846ca68b); id ^= id >> 16;
    return id & (size - 1);
}
static int mugl_id_find(const MuglIdEntry *table, size_t size, uint32_t id)
{
    if (!id) return -1;
    size_t slot = mugl_id_hash(id, size);
    for (size_t i = 0; i < size; i++, slot = (slot + 1) & (size - 1)) {
        if (!table[slot].key) return -1;
        if (table[slot].key == id) return table[slot].row;
    }
    return -1;
}
static int mugl_id_insert(MuglIdEntry *table, size_t size, uint32_t id, int row)
{
    if (!id) return 0;
    size_t slot = mugl_id_hash(id, size);
    for (size_t i = 0; i < size; i++, slot = (slot + 1) & (size - 1)) {
        if (!table[slot].key || table[slot].key == id) {
            table[slot].key = id; table[slot].row = row; return 1;
        }
    }
    return 0;
}
#endif
