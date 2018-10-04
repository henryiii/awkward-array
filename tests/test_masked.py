#!/usr/bin/env python

# Copyright (c) 2018, DIANA-HEP
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
# 
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
# 
# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import unittest

import numpy

from awkward import *

class Test(unittest.TestCase):
    def runTest(self):
        pass

    def test_masked_get(self):
        a = MaskedArray([True, False, True, False, True, False, True, False, True, False], [0.0, 1.1, 2.2, 3.3, 4.4, 5.5, 6.6, 7.7, 8.8, 9.9], maskedwhen=True)
        self.assertEqual(a.tolist(), [None, 1.1, None, 3.3, None, 5.5, None, 7.7, None, 9.9])
        self.assertTrue(MaskedArray.is_masked(a[0]))
        self.assertFalse(MaskedArray.is_masked(a[1]))
        self.assertEqual(a[5:].tolist(), [5.5, None, 7.7, None, 9.9])
        self.assertFalse(MaskedArray.is_masked(a[5:][0]))
        self.assertTrue(MaskedArray.is_masked(a[5:][1]))
        self.assertEqual(a[[3, 2, 1]].tolist(), [3.3, None, 1.1])
        self.assertEqual(a[[True, True, True, True, True, False, False, False, False, False]].tolist(), [None, 1.1, None, 3.3, None])

    def test_masked_get_flip(self):
        a = MaskedArray([False, True, False, True, False, True, False, True, False, True], [0.0, 1.1, 2.2, 3.3, 4.4, 5.5, 6.6, 7.7, 8.8, 9.9], maskedwhen=False)
        self.assertEqual(a.tolist(), [None, 1.1, None, 3.3, None, 5.5, None, 7.7, None, 9.9])
        self.assertTrue(MaskedArray.is_masked(a[0]))
        self.assertFalse(MaskedArray.is_masked(a[1]))
        self.assertEqual(a[5:].tolist(), [5.5, None, 7.7, None, 9.9])
        self.assertFalse(MaskedArray.is_masked(a[5:][0]))
        self.assertTrue(MaskedArray.is_masked(a[5:][1]))
        self.assertEqual(a[[3, 2, 1]].tolist(), [3.3, None, 1.1])
        self.assertEqual(a[[True, True, True, True, True, False, False, False, False, False]].tolist(), [None, 1.1, None, 3.3, None])

    # def test_bitmasked_get(self):
    #     a = BitMaskedArray.fromboolmask([True, False, True, False, True, False, True, False, True, False], [0.0, 1.1, 2.2, 3.3, 4.4, 5.5, 6.6, 7.7, 8.8, 9.9], maskedwhen=True, lsb=True)
    #     self.assertEqual(a.tolist(), [None, 1.1, None, 3.3, None, 5.5, None, 7.7, None, 9.9])
    #     self.assertTrue(MaskedArray.is_masked(a[0]))
    #     self.assertFalse(MaskedArray.is_masked(a[1]))
    #     self.assertEqual(a[5:].tolist(), [5.5, None, 7.7, None, 9.9])
    #     self.assertFalse(MaskedArray.is_masked(a[5:][0]))
    #     self.assertTrue(MaskedArray.is_masked(a[5:][1]))
    #     self.assertEqual(a[[3, 2, 1]].tolist(), [3.3, None, 1.1])
    #     self.assertEqual(a[[True, True, True, True, True, False, False, False, False, False]].tolist(), [None, 1.1, None, 3.3, None])

    #     a = BitMaskedArray.fromboolmask([True, False, True, False, True, False, True, False, True, False], [0.0, 1.1, 2.2, 3.3, 4.4, 5.5, 6.6, 7.7, 8.8, 9.9], maskedwhen=True, lsb=False)
    #     self.assertEqual(a.tolist(), [None, 1.1, None, 3.3, None, 5.5, None, 7.7, None, 9.9])
    #     self.assertTrue(MaskedArray.is_masked(a[0]))
    #     self.assertFalse(MaskedArray.is_masked(a[1]))
    #     self.assertEqual(a[5:].tolist(), [5.5, None, 7.7, None, 9.9])
    #     self.assertFalse(MaskedArray.is_masked(a[5:][0]))
    #     self.assertTrue(MaskedArray.is_masked(a[5:][1]))
    #     self.assertEqual(a[[3, 2, 1]].tolist(), [3.3, None, 1.1])
    #     self.assertEqual(a[[True, True, True, True, True, False, False, False, False, False]].tolist(), [None, 1.1, None, 3.3, None])

    # def test_bitmasked_get_flip(self):
    #     a = BitMaskedArray.fromboolmask([False, True, False, True, False, True, False, True, False, True], [0.0, 1.1, 2.2, 3.3, 4.4, 5.5, 6.6, 7.7, 8.8, 9.9], maskedwhen=False, lsb=True)
    #     self.assertEqual(a.tolist(), [None, 1.1, None, 3.3, None, 5.5, None, 7.7, None, 9.9])
    #     self.assertTrue(MaskedArray.is_masked(a[0]))
    #     self.assertFalse(MaskedArray.is_masked(a[1]))
    #     self.assertEqual(a[5:].tolist(), [5.5, None, 7.7, None, 9.9])
    #     self.assertFalse(MaskedArray.is_masked(a[5:][0]))
    #     self.assertTrue(MaskedArray.is_masked(a[5:][1]))
    #     self.assertEqual(a[[3, 2, 1]].tolist(), [3.3, None, 1.1])
    #     self.assertEqual(a[[True, True, True, True, True, False, False, False, False, False]].tolist(), [None, 1.1, None, 3.3, None])

    #     a = BitMaskedArray.fromboolmask([False, True, False, True, False, True, False, True, False, True], [0.0, 1.1, 2.2, 3.3, 4.4, 5.5, 6.6, 7.7, 8.8, 9.9], maskedwhen=False, lsb=False)
    #     self.assertEqual(a.tolist(), [None, 1.1, None, 3.3, None, 5.5, None, 7.7, None, 9.9])
    #     self.assertTrue(MaskedArray.is_masked(a[0]))
    #     self.assertFalse(MaskedArray.is_masked(a[1]))
    #     self.assertEqual(a[5:].tolist(), [5.5, None, 7.7, None, 9.9])
    #     self.assertFalse(MaskedArray.is_masked(a[5:][0]))
    #     self.assertTrue(MaskedArray.is_masked(a[5:][1]))
    #     self.assertEqual(a[[3, 2, 1]].tolist(), [3.3, None, 1.1])
    #     self.assertEqual(a[[True, True, True, True, True, False, False, False, False, False]].tolist(), [None, 1.1, None, 3.3, None])

    # def test_bitmasked_arrow(self):
    #     # Apache Arrow layout example
    #     # https://github.com/apache/arrow/blob/master/format/Layout.md#null-bitmaps
    #     a = BitMaskedArray.fromboolmask([True, True, False, True, False, True], [0, 1, 999, 2, 999, 3], maskedwhen=False, lsb=True)
    #     self.assertEqual(a.tolist(), [0, 1, None, 2, None, 3])

    #     # extra gunk at the end of the array
    #     a = BitMaskedArray.fromboolmask([True, True, False, True, False, True, True, True], [0, 1, 999, 2, 999, 3], maskedwhen=False, lsb=True)
    #     self.assertEqual(a.tolist(), [0, 1, None, 2, None, 3])

    #     # opposite sign
    #     a = BitMaskedArray.fromboolmask([True, True, False, True, False, True, False, False], [0, 1, 999, 2, 999, 3], maskedwhen=False, lsb=True)
    #     self.assertEqual(a.tolist(), [0, 1, None, 2, None, 3])

    #     # doubled
    #     a = BitMaskedArray.fromboolmask([True, True, False, True, False, True, True, True, False, True, False, True], [0, 1, 999, 2, 999, 3, 0, 1, 999, 2, 999, 3], maskedwhen=False, lsb=True)
    #     self.assertEqual(a.tolist(), [0, 1, None, 2, None, 3, 0, 1, None, 2, None, 3])
