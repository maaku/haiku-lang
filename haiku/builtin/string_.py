#!/usr/bin/env python
# -*- coding: utf-8 -*-

# === haiku.builtin.string_ -----------------------------------------------===
# Copyright © 2011-2012, RokuSigma Inc. and contributors. See AUTHORS for more
# details.
#
# Some rights reserved.
#
# Redistribution and use in source and binary forms of the software as well as
# documentation, with or without modification, are permitted provided that the
# following conditions are met:
#
#  * Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#  * The names of the copyright holders or contributors may not be used to
#    endorse or promote products derived from this software without specific
#    prior written permission.
#
# THIS SOFTWARE AND DOCUMENTATION IS PROVIDED BY THE COPYRIGHT HOLDERS AND
# CONTRIBUTORS “AS IS” AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT
# NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE AND
# DOCUMENTATION, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# ===----------------------------------------------------------------------===

""

import operator

from haiku.builtin import builtinEnvironment
from haiku.pickle import CanonicalExpressionPickler
from haiku.types import *
__all__ = []

# ===----------------------------------------------------------------------===

_cat, = map(Symbol,
'cat'.split())

from operator import concat

builtinEnvironment[_cat] = Procedure(
  params      = Tuple([
      (1, (SymbolCompatible, UnicodeCompatible)),
      (2, (SymbolCompatible, UnicodeCompatible)),
    ]),
  defaults    = Tuple(),
  ellipsis    = False,
  environment = builtinEnvironment,
  body        = lambda eval_,env:concat(env[1], env[2]),
)

# ===----------------------------------------------------------------------===

_encode, _decode = map(Symbol,
'encode   decode'.split())

builtinEnvironment[_encode] = Procedure(
  params      = Tuple([
      (1,          UnicodeCompatible),
      ('encoding', SymbolCompatible),
    ]),
  defaults    = Tuple([
      ('encoding', 'utf-8'),
    ]),
  ellipsis    = False,
  environment = builtinEnvironment,
  body        = lambda eval_,env:env[1].encode(env['encoding']),
)

builtinEnvironment[_decode] = Procedure(
  params      = Tuple([
      (1,          SymbolCompatible),
      ('encoding', SymbolCompatible),
    ]),
  defaults    = Tuple([
      ('encoding', 'utf-8'),
    ]),
  ellipsis    = False,
  environment = builtinEnvironment,
  body        = lambda eval_,env:env[1].decode(env['encoding']),
)

# ===----------------------------------------------------------------------===
# End of File
# ===----------------------------------------------------------------------===
