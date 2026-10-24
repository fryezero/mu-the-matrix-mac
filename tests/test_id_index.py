"""Named-buffer index tests: collisions, capacity, reuse and full 32-bit IDs."""
import ctypes
from pathlib import Path
import random
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class IdIndexTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        source = Path(cls.temp.name) / 'index.c'
        source.write_text('''
#include <string.h>
#include "id_index.h"
static MuglIdEntry rows[16384];
void reset(void) { memset(rows,0,sizeof rows); }
int find(unsigned id, unsigned size) { return mugl_id_find(rows,size,id); }
int put(unsigned id, int row, unsigned size) { return mugl_id_insert(rows,size,id,row); }
unsigned bucket(unsigned id, unsigned size) { return (unsigned)mugl_id_hash(id,size); }
''')
        lib = Path(cls.temp.name) / 'index.so'
        subprocess.run(['clang', '-O2', '-shared', '-fPIC', '-Wall', '-Wextra', '-Werror',
                        '-I', str(ROOT / 'mac-play/hotpatch'), str(source), '-o', str(lib)], check=True)
        cls.lib = ctypes.CDLL(str(lib))
        cls.lib.find.argtypes = [ctypes.c_uint, ctypes.c_uint]
        cls.lib.find.restype = ctypes.c_int
        cls.lib.put.argtypes = [ctypes.c_uint, ctypes.c_int, ctypes.c_uint]
        cls.lib.put.restype = ctypes.c_int
        cls.lib.bucket.argtypes = [ctypes.c_uint, ctypes.c_uint]
        cls.lib.bucket.restype = ctypes.c_uint

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def setUp(self):
        self.lib.reset()

    def test_real_capacity_with_varied_32bit_names(self):
        keys = [((i * 65537 + 1) & 0xffffffff) for i in range(8192)]
        keys[-1] = 0xffffffff
        for row, key in enumerate(keys):
            self.assertEqual(self.lib.put(key, row, 16384), 1)
        for row, key in enumerate(keys):
            self.assertEqual(self.lib.find(key, 16384), row)
        self.assertEqual(self.lib.find(0, 16384), -1)
        self.assertEqual(self.lib.put(0, 7, 16384), 0)
        self.assertEqual(self.lib.find(0xfffffffe, 16384), -1)

    def test_collision_chain_and_wrapped_probing(self):
        keys = [i for i in range(1, 300) if self.lib.bucket(i, 8) == 7][:8]
        self.assertEqual(len(keys), 8)
        for row, key in enumerate(keys):
            self.assertEqual(self.lib.put(key, row, 8), 1)
        for row, key in enumerate(keys):
            self.assertEqual(self.lib.find(key, 8), row)
        self.assertEqual(self.lib.find(0xffffffff, 8), -1)
        self.assertEqual(self.lib.put(0xffffffff, 20, 8), 0)

    def test_reset_of_buffer_contents_does_not_change_name_to_row_mapping(self):
        # glDeleteBuffers retains each table row and its name in this proxy.
        # Reusing that name must still find that row, including row zero.
        for _ in range(100):
            self.assertEqual(self.lib.put(17, 0, 16384), 1)
            self.assertEqual(self.lib.find(17, 16384), 0)
        self.assertEqual(self.lib.find(18, 16384), -1)

    def test_seeded_updates_match_dictionary(self):
        rng = random.Random(42)
        reference = {}
        for _ in range(12000):
            key = rng.randrange(1, 5000)
            row = rng.randrange(8192)
            self.assertEqual(self.lib.put(key, row, 16384), 1)
            reference[key] = row
        for key, row in reference.items():
            self.assertEqual(self.lib.find(key, 16384), row)


if __name__ == '__main__':
    unittest.main()
