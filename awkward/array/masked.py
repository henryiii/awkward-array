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

import collections
import numbers

import awkward.array.base
import awkward.util

class MaskedArray(awkward.array.base.AwkwardArrayWithContent):
    ### WTF were the designers of numpy.ma thinking?
    # @staticmethod
    # def is_masked(x):
    #     return awkward.util.numpy.ma.is_masked(x)
    # masked = awkward.util.numpy.ma.masked

    @staticmethod
    def is_masked(x):
        if isinstance(x, MaskedArray):
            # numpy.ma.is_masked(array) if any element is masked
            if x.maskedwhen:
                return x.mask.any()
            else:
                return not x.mask.all()
        else:
            # numpy.ma.is_masked(x) if x represents a masked constant
            return x is MaskedArray.masked
    masked = None

    def __init__(self, mask, content, maskedwhen=True):
        self.mask = mask
        self.content = content
        self.maskedwhen = maskedwhen

    def copy(self, mask=None, content=None, maskedwhen=None):
        out = self.__class__.__new__(self.__class__)
        out._mask = self._mask
        out._content = self._content
        out._maskedwhen = self._maskedwhen
        if mask is not None:
            out._mask = mask
        if content is not None:
            out._content = content
        if maskedwhen is not None:
            out._maskedwhen = maskedwhen
        return out

    def deepcopy(self, mask=None, content=None):
        out = self.copy(mask=mask, content=content)
        out._mask = awkward.util.deepcopy(out._mask)
        out._content = awkward.util.deepcopy(out._content)
        return out

    def empty_like(self, **overrides):
        mine = {}
        mine["maskedwhen"] = overrides.pop("maskedwhen", self._maskedwhen)
        if isinstance(self._content, awkward.util.numpy.ndarray):
            return self.copy(content=awkward.util.numpy.empty_like(self._content), **mine)
        else:
            return self.copy(content=self._content.empty_like(**overrides), **mine)

    def zeros_like(self, **overrides):
        mine = {}
        mine["maskedwhen"] = overrides.pop("maskedwhen", self._maskedwhen)
        if isinstance(self._content, awkward.util.numpy.ndarray):
            return self.copy(content=awkward.util.numpy.zeros_like(self._content), **mine)
        else:
            return self.copy(content=self._content.zeros_like(**overrides), **mine)

    def ones_like(self, **overrides):
        mine = {}
        mine["maskedwhen"] = overrides.pop("maskedwhen", self._maskedwhen)
        if isinstance(self._content, awkward.util.numpy.ndarray):
            return self.copy(content=awkward.util.numpy.ones_like(self._content), **mine)
        else:
            return self.copy(content=self._content.ones_like(**overrides), **mine)

    @property
    def mask(self):
        return self._mask

    @mask.setter
    def mask(self, value):
        value = awkward.util.toarray(value, awkward.util.MASKTYPE, awkward.util.numpy.ndarray)
        if len(value.shape) != 1:
            raise TypeError("mask must have 1-dimensional shape")
        if not issubclass(value.dtype.type, (awkward.util.numpy.bool_, awkward.util.numpy.bool)):
            value = (value != 0)
        self._mask = value

    @property
    def boolmask(self):
        return self._mask

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, value):
        self._content = awkward.util.toarray(value, awkward.util.DEFAULTTYPE)

    @property
    def maskedwhen(self):
        return self._maskedwhen

    @maskedwhen.setter
    def maskedwhen(self, value):
        self._maskedwhen = bool(value)

    @property
    def dtype(self):
        return self._content.dtype

    def __len__(self):
        return len(self._content)

    @property
    def shape(self):
        return self._content.shape

    @property
    def type(self):
        return self._content.type

    @property
    def base(self):
        return self._content.base

    def _valid(self):
        if len(self._mask) != len(self._content):
            raise ValueError("mask length ({0}) is not equal to content length ({1})".format(len(self._mask), len(self._content)))

    def __iter__(self):
        self._valid()
        for i, x in enumerate(self._content):
            if self._mask[i] == self._maskedwhen:
                yield self.masked
            else:
                yield x

    def __getitem__(self, where):
        self._valid()

        if awkward.util.isstringslice(where):
            return self.copy(content=self._content[where])

        if isinstance(where, tuple) and len(where) == 0:
            return self
        if not isinstance(where, tuple):
            where = (where,)
        head, tail = where[0], where[1:]

        if isinstance(head, awkward.util.integer):
            if self._mask[head] == self._maskedwhen:
                if tail != ():
                    raise ValueError("masked element ({0}) is not subscriptable".format(self.masked))
                return self.masked
            else:
                return self._content[(head,) + tail]

        else:
            mask = self._mask[head]
            if tail != () and ((self.maskedwhen and mask.any()) or (not self.maskedwhen and not self.mask.all())):
                raise ValueError("masked element ({0}) is not subscriptable".format(self.masked))
            else:
                return self.copy(mask=mask, content=self._content[(head,) + tail])
        
    def __array_ufunc__(self, ufunc, method, *inputs, **kwargs):
        import awkward.array.objects
        self._valid()

        if method != "__call__":
            return NotImplemented

        inputs = list(inputs)
        intersection = None
        for i in range(len(inputs)):
            if isinstance(inputs[i], MaskedArray):
                if intersection is None:
                    intersection = inputs[i]._mask
                else:
                    intersection &= inputs[i]._mask
                inputs[i] = inputs[i]._content

        result = getattr(ufunc, method)(*inputs, **kwargs)

        if isinstance(result, tuple):
            return tuple(awkward.array.objects.Methods.maybemixin(type(x), MaskedArray)(intersection, x) if isinstance(x, (awkward.util.numpy.ndarray, awkward.array.base.AwkwardBase)) else x for x in result)
        elif method == "at":
            return None
        else:
            return awkward.array.objects.Methods.maybemixin(type(result), MaskedArray)(intersection, result)

    def any(self):
        return self._content[self._mask].any()

    def all(self):
        return self._content[self._mask].all()

    @classmethod
    def concat(cls, first, *rest):
        raise NotImplementedError

    def pandas(self):
        raise NotImplementedError

# class MaskedArray(awkward.array.base.AwkwardArray):
#     def __init__(self, mask, content, maskedwhen=True):
#         self.mask = mask
#         self.content = content
#         self.maskedwhen = maskedwhen

#     @property
#     def mask(self):
#         return self._mask

#     @mask.setter
#     def mask(self, value):
#         value = self._toarray(value, self.MASKTYPE, (numpy.ndarray, awkward.array.base.AwkwardArray))

#         if len(value.shape) != 1:
#             raise TypeError("mask must have 1-dimensional shape")
#         if value.shape[0] == 0:
#             value = value.view(self.MASKTYPE)
#         if not issubclass(value.dtype.type, (numpy.bool_, numpy.bool)):
#             raise TypeError("mask must have boolean dtype")

#         self._mask = value

#     @property
#     def boolmask(self):
#         return self._mask

#     @boolmask.setter
#     def boolmask(self, value):
#         self.mask = value

#     @property
#     def content(self):
#         return self._content

#     @content.setter
#     def content(self, value):
#         self._content = self._toarray(value, self.CHARTYPE, (numpy.ndarray, awkward.array.base.AwkwardArray))
        
#     @property
#     def maskedwhen(self):
#         return self._maskedwhen

#     @maskedwhen.setter
#     def maskedwhen(self, value):
#         self._maskedwhen = bool(value)

#     @property
#     def dtype(self):
#         return self._content.dtype

#     @property
#     def shape(self):
#         return self._content.shape

#     def __len__(self):
#         return len(self._content)

#     def __getitem__(self, where):
#         if self._isstring(where):
#             return MaskedArray(self._mask, self._content[where], maskedwhen=self._maskedwhen)

#         if not isinstance(where, tuple):
#             where = (where,)
#         head, tail = where[0], where[1:]

#         if isinstance(head, (numbers.Integral, numpy.integer)):
#             if self._mask[head] == self._maskedwhen:
#                 return numpy.ma.masked
#             else:
#                 return self._content[self._singleton(where)]
#         else:
#             return MaskedArray(self._mask[head], self._content[self._singleton(where)], maskedwhen=self._maskedwhen)

class BitMaskedArray(MaskedArray):
    def __init__(self, mask, content, maskedwhen=True, lsb=True):
        raise NotImplementedError

    def copy(self, index=None, content=None):
        raise NotImplementedError

    def deepcopy(self, index=None, content=None):
        raise NotImplementedError

    def empty_like(self, **overrides):
        raise NotImplementedError

    def zeros_like(self, **overrides):
        raise NotImplementedError

    def ones_like(self, **overrides):
        raise NotImplementedError

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, value):
        raise NotImplementedError

    @property
    def type(self):
        raise NotImplementedError

    def __len__(self):
        raise NotImplementedError

    @property
    def shape(self):
        raise NotImplementedError

    @property
    def dtype(self):
        raise NotImplementedError

    @property
    def base(self):
        raise NotImplementedError

    def _valid(self):
        raise NotImplementedError

    def __iter__(self):
        raise NotImplementedError

    def __getitem__(self, where):
        raise NotImplementedError

    def __setitem__(self, where, what):
        raise NotImplementedError

    def __delitem__(self, where, what):
        raise NotImplementedError

    def __array_ufunc__(self, ufunc, method, *inputs, **kwargs):
        raise NotImplementedError

    def any(self):
        raise NotImplementedError

    def all(self):
        raise NotImplementedError

    @classmethod
    def concat(cls, first, *rest):
        raise NotImplementedError

    def pandas(self):
        raise NotImplementedError

# class BitMaskedArray(MaskedArray):
#     @staticmethod
#     def fromboolmask(mask, content, maskedwhen=True, lsb=True):
#         out = BitMaskedArray([], content, maskedwhen=maskedwhen, lsb=lsb)
#         out.boolmask = mask
#         return out

#     def __init__(self, mask, content, maskedwhen=True, lsb=True):
#         self.mask = mask
#         self.content = content
#         self.maskedwhen = maskedwhen
#         self.lsb = lsb

#     @property
#     def mask(self):
#         return self._mask

#     @mask.setter
#     def mask(self, value):
#         value = self._toarray(value, self.BITMASKTYPE, (numpy.ndarray, awkward.array.base.AwkwardArray))

#         if len(value.shape) != 1:
#             raise TypeError("mask must have 1-dimensional shape")

#         self._mask = value.view(self.BITMASKTYPE)

#     @property
#     def boolmask(self):
#         out = numpy.unpackbits(self._mask)
#         if self._lsb:
#             out = out.reshape(-1, 8)[:,::-1].reshape(-1)
#         return out.view(self.MASKTYPE)[:len(self._content)]

#     @boolmask.setter
#     def boolmask(self, value):
#         value = numpy.array(value, copy=False)

#         if len(value.shape) != 1:
#             raise TypeError("boolmask must have 1-dimensional shape")
#         if not issubclass(value.dtype.type, (numpy.bool, numpy.bool_)):
#             raise TypeError("boolmask must have boolean type")

#         if self._lsb:
#             # maybe pad the length for reshape
#             length = 8*((len(value) + 8 - 1) >> 3)   # ceil(len(value) / 8.0) * 8
#             if length != len(value):
#                 out = numpy.empty(length, dtype=numpy.bool_)
#                 out[:len(value)] = value
#             else:
#                 out = value

#             # reverse the order in groups of 8
#             out = out.reshape(-1, 8)[:,::-1].reshape(-1)

#         else:
#             # numpy.packbits encodes as msb (most significant bit); already in the right order
#             out = value

#         self._mask = numpy.packbits(out)
        
#     @property
#     def lsb(self):
#         return self._lsb

#     @lsb.setter
#     def lsb(self, value):
#         self._lsb = bool(value)

#     def _maskat(self, where):
#         bytepos = numpy.right_shift(where, 3)    # where // 8
#         bitpos  = where - 8*bytepos              # where % 8

#         if self.lsb:
#             bitmask = numpy.left_shift(1, bitpos)
#         else:
#             bitmask = numpy.right_shift(128, bitpos)

#         if isinstance(bitmask, numpy.ndarray):
#             bitmask = bitmask.astype(self.BITMASKTYPE)
#         else:
#             bitmask = self.BITMASKTYPE.type(bitmask)

#         return bytepos, bitmask

#     def _maskwhere(self, where):
#         if isinstance(where, (numbers.Integral, numpy.integer)):
#             bytepos, bitmask = self._maskat(where)
#             return numpy.bitwise_and(self._mask[bytepos], bitmask) != 0

#         elif isinstance(where, slice):
#             # assumes a small slice; for a big slice, it could be faster to unpack the whole mask
#             return self._maskwhere(numpy.arange(*where.indices(len(self._content))))

#         else:
#             where = numpy.array(where, copy=False)
#             if len(where.shape) == 1 and issubclass(where.dtype.type, numpy.integer):
#                 byteposes, bitmasks = self._maskat(where)
#                 numpy.bitwise_and(bitmasks, self._mask[byteposes], bitmasks)
#                 return bitmasks.astype(numpy.bool_)
        
#             elif len(where.shape) == 1 and issubclass(where.dtype.type, (numpy.bool, numpy.bool_)):
#                 # scales with the size of the mask anyway, so go ahead and unpack the whole mask
#                 unpacked = numpy.unpackbits(self._mask).view(self.MASKTYPE)

#                 if self.lsb:
#                     unpacked = unpacked.reshape(-1, 8)[:,::-1].reshape(-1)[:len(where)]
#                 else:
#                     unpacked = unpacked[:len(where)]

#                 return unpacked[where]

#             else:
#                 raise TypeError("cannot interpret shape {0}, dtype {1} as a fancy index or mask".format(where.shape, where.dtype))

#     def _setmask(self, where, valid):
#         if isinstance(where, (numbers.Integral, numpy.integer)):        
#             bytepos, bitmask = self._maskat(where)
#             if self._maskedwhen != valid:
#                 self._mask[bytepos] |= bitmask
#             else:
#                 self._mask[bytepos] &= numpy.bitwise_not(bitmask)

#         elif isinstance(where, slice):
#             # assumes a small slice; for a big slice, it could be faster to unpack the whole mask
#             self._setmask(numpy.arange(*where.indices(len(self._content))), valid)

#         else:
#             where = numpy.array(where, copy=False)
#             if len(where.shape) == 1 and issubclass(where.dtype.type, numpy.integer):
#                 bytepos, bitmask = self._maskat(where)
#                 if self._maskedwhen != valid:
#                     numpy.bitwise_or.at(self._mask, bytepos, bitmask)
#                 else:
#                     numpy.bitwise_and.at(self._mask, bytepos, numpy.bitwise_not(bitmask))

#             elif len(where.shape) == 1 and issubclass(where.dtype.type, (numpy.bool, numpy.bool_)):
#                 tmp = self.boolmask
#                 if self._maskedwhen != valid:
#                     tmp[where] = True
#                 else:
#                     tmp[where] = False
#                 self.boolmask = tmp

#             else:
#                 raise TypeError("cannot interpret shape {0}, dtype {1} as a fancy index or mask".format(where.shape, where.dtype))

#     def __getitem__(self, where):
#         if self._isstring(where):
#             return MaskedArray(self._mask, self._content[where], maskedwhen=self._maskedwhen)

#         if not isinstance(where, tuple):
#             where = (where,)
#         head, tail = where[0], where[1:]

#         if isinstance(head, (numbers.Integral, numpy.integer)):
#             if self._maskwhere(head) == self._maskedwhen:
#                 return numpy.ma.masked
#             else:
#                 return self._content[self._singleton(where)]

#         else:
#             return MaskedArray(self._maskwhere(head), self._content[self._singleton(where)], maskedwhen=self._maskedwhen)
