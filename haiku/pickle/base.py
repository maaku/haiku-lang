#!/usr/bin/env python
# -*- coding: utf-8 -*-

# === haiku.pickle.base ---------------------------------------------------===
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

from abc import ABCMeta, abstractmethod

__all__ = [
  'BasePickler',
]

class BasePickler(object):
  """A pickler provides a mechanism for serializing Lisp-like code and data
  expressions of a tuple-oriented language into standard, widely-understood
  formats. The `BasePPickler` class provides an abstract interface to these
  serializers."""
  __metaclass__ = ABCMeta

  # Python provides access to the tokenizing codes of its own interpreter. We
  # won't be using the Python tokenizer but we will re-use its TokenError
  # exception:
  from tokenize import TokenError

  # Not a typo: SyntaxError is a built-in Python exception, which we want to
  # make a property of this `BasePickler` as well.
  SyntaxError = SyntaxError

  @abstractmethod
  def dump(self, ostream, *args, **kwargs):
    ""
    # FIXME: implement a version that relies upon `self.dumps`, then remove
    #   the @abstractmethod decorator.
    return super(BasePickler, self).dump(*args, **kwargs)

  @abstractmethod
  def dumps(self, *args, **kwargs):
    ""
    # FIXME: implement a version that relies upon `self.dump`, then remove the
    #   @abstractmethod decorator.
    return super(BasePickler, self).dumps(*args, **kwargs)

  @abstractmethod
  def load(self, istream, *args, **kwargs):
    ""
    # FIXME: implement a version that relies upon `self.loads`, then remove
    #   the @abstractmethod decorator.
    return super(BasePickler, self).load(*args, **kwargs)

  @abstractmethod
  def loads(self, *args, **kwargs):
    ""
    # FIXME: implement a version that relies upon `self.load`, then remove the
    #   @abstractmethod decorator.
    return super(BasePickler, self).loads(*args, **kwargs)

# ===----------------------------------------------------------------------===
# End of File
# ===----------------------------------------------------------------------===
