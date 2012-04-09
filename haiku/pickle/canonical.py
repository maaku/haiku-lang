#!/usr/bin/env python
# -*- coding: utf-8 -*-

# === haiku.pickle.canonical ----------------------------------------------===
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

# Python standard library, iteration tools
from itertools import count

from python_patterns.itertools import lookahead

# Haiku language, type definitions
from haiku.types import *

from haiku.utils.serialization import i2bytearray, i2varnumber, s2varstring

from .base import BasePickler

__all__ = [
  'CanonicalExpressionPickler',
]

# ===----------------------------------------------------------------------===

# c-expression syntax:
#
#  <c-tuple>:: “[” <c-expr>* “]”
#   <c-expr>:: <c-part> | “'” <c-expr> | “,” <c-expr> | “`” <c-expr>
#   <c-part>:: <atom> | <c-expr>
#     <atom>:: <decimal> “:” [octet array of <decimal> length]
#  <decimal>:: <nzddigit> <ddigit>*
# <nzddigit>:: “1” | “2” | “3” | “4” | “5” | “6” | “7” | “8” | “9”
#   <ddigit>:: “0” | <nzddigit>
#
# That's it!

class CanonicalExpressionPickler(BasePickler):
  ""
  ASSOCIATION_OPERATOR = u"="

  def dumps(self, *args):
    """Serialize a Python-represented haiku expression into canonical-
    expression notation.

      >>> from haiku.pickle import CanonicalExpressionPickler
      >>> pickler = CanonicalExpressionPickler()
      >>> pickler.dumps({0:'*',1:3,2:{0:'+',1:1,2:6}})
      '(1:*(7:integer1:3)(1:+(7:integer:1:17:integer:1:6))'
    """
    # `dumps()` is allowed an infinite number of positional arguemnts, each of
    # which must be a Python-represented haiku expression. These are converted
    # into simple-expression notation, then joined together.
    if len(args) < 1:
      return ''
    elif len(args) > 1:
      return ''.join(map(self.dumps, args))

    # Otherwise only one positional arguement is given, and our task is to
    # convert it to s-expression notation.
    return self._serialize(args[0])

  def load(self, istream):
    return []

  def _serialize(self, expression):
    """Translates a Python-represented haiku expression into a byte string
    in “Canonical Expression” notation."""
    # None/nil/omega value:
    if isinstance(expression, OmegaCompatible):
      return s2varstring('')

    # Boolean literals:
    elif isinstance(expression, BooleanCompatible):
      if expression:
        return ''.join([
          self.TUPLE_OPEN.encode('utf-8'),
          s2varstring('true'),
          self.TUPLE_CLOSE.encode('utf-8')])
      else:
        return ''.join([
          self.TUPLE_OPEN.encode('utf-8'),
          s2varstring('false'),
          self.TUPLE_CLOSE.encode('utf-8')])

    # Integral numeric literals:
    elif isinstance(expression, IntegerCompatible):
      return ''.join([
        self.TUPLE_OPEN.encode('utf-8'),
        s2varstring('integer'),
        s2varstring(expression and i2bytearray(expression) or ''),
        self.TUPLE_CLOSE.encode('utf-8')])

    # Rational numeric literals:
    elif isinstance(expression, FractionCompatible):
      return ''.join([
        self.TUPLE_OPEN.encode('utf-8'),
        s2varstring('rational'),
        self._serialize(expression.numerator),
        self._serialize(expression.denominator),
        self.TUPLE_CLOSE.encode('utf-8')])

    # Unicode literals:
    elif isinstance(expression, UnicodeCompatible):
      return ''.join([
        self.TUPLE_OPEN.encode('utf-8'),
        s2varstring('string'),
        s2varstring(expression.encode('utf-8')),
        self.TUPLE_CLOSE.encode('utf-8')])

    # Byte-array literals:
    elif isinstance(expression, SymbolCompatible):
      return s2varstring(expression)

    # Sets:
    elif isinstance(expression, SetCompatible):
      return ''.join([
        self.TUPLE_OPEN.encode('utf-8'),
        s2varstring('set'),
        ''.join(self._serialize(elem) for elem in sorted(expression)),
        self.TUPLE_CLOSE.encode('utf-8')])

    # FIXME: implement meta-values

    # Tuples(/maps/dictionaries):
    elif isinstance(expression, TupleCompatible):
      special_pattern = lambda expr:(
        len(expr) == 2 and set(expr.keys()) == set(range(2)))
      # Output special forms:
      if special_pattern(expression):
        if expression[0] == self.QUOTE_PROCEDURE:
          #if (isinstance(expression[1], TupleCompatible) and
          #    all(special_pattern(expression[1][key]) and
          #        expression[1][key][0] == self.UNQUOTE_PROCEDURE
          #        for key in expression[1].keys())):
          #  return ''.join([
          #    self.EVAL_DATA_OPEN.encode('utf-8'),
          #    self.dumps(expression[1]),
          #    self.EVAL_DATA_CLOSE.encode('utf-8')])
          return ''.join([
            self.QUOTE_OPERATOR.encode('utf-8'),
            self._serialize(expression[1])])
        if expression[0] == self.UNQUOTE_PROCEDURE:
          return ''.join([
            self.UNQUOTE_OPERATOR.encode('utf-8'),
            self._serialize(expression[1])])
        if expression[0] == self.UNQUOTE_SPLICE_PROCEDURE:
          return ''.join([
            self.UNQUOTE_SPLICE_OPERATOR.encode('utf-8'),
            self._serialize(expression[1])])

      args = []
      kwargs = Tuple(expression)
      kwargs_keys = kwargs.keys()
      for key in count():
        if key in kwargs_keys:
          args.append(kwargs.pop(key))
        else:
          break
      return ''.join([
        self.TUPLE_OPEN.encode('utf-8'),
        ''.join([
          ''.join(self._serialize(arg) for arg in args),
          ''.join(
            ''.join([
              self.ASSOCIATION_OPERATOR.encode('utf-8'),
              self._serialize(key),
              self._serialize(expression[key]),
            ]) for key in sorted(kwargs.keys()))]),
        self.TUPLE_CLOSE.encode('utf-8')])

    # Relations:
    elif isinstance(expression, RelationCompatible):
      raise NotImplementedError

    # Sequences(/lists):
    elif isinstance(expression, SequenceCompatible):
      return ''.join([
        self.SEQUENCE_OPEN.encode('utf-8'),
        ''.join(self._serialize(elem) for elem in expression),
        self.SEQUENCE_CLOSE.encode('utf-8')])

    # Matrices:
    elif isinstance(expression, MatrixCompatible):
      raise NotImplementedError

    # Procedures(/lambdas):
    elif isinstance(expression, Procedure):
      raise NotImplementedError

    # That's it! We should have matched one of the previous cases and returned
    # already if we were a valid Python-represented haiku expression. So we
    # can assume the caller passed us something in error and report the
    # problem:
    raise ValueError(
      u"unrecognized input (not a valid expression): '%s'" % repr(expression))

  def _tokenize(self, iterable):
    ""
    INITIAL, LENGTH, SEPARATOR, SYMBOL = range(4)

    parenopen_tuple      = set([self.TUPLE_OPEN.encode('utf-8')])
    parenopen_eval_data  = set([self.EVAL_DATA_OPEN.encode('utf-8')])
    parenopen_sequence   = set([self.SEQUENCE_OPEN.encode('utf-8')])
    parenopen            = parenopen_sequence.union(
                             parenopen_eval_data.union(parenopen_tuple))
    parenclose_tuple     = set([self.TUPLE_CLOSE.encode('utf-8')])
    parenclose_eval_data = set([self.EVAL_DATA_CLOSE.encode('utf-8')])
    parenclose_sequence  = set([self.SEQUENCE_CLOSE.encode('utf-8')])
    parenclose           = parenclose_sequence.union(
                            parenclose_eval_data.union(parenclose_tuple))
    parenmap = {
      self.TUPLE_CLOSE.encode('utf-8'):     self.TUPLE_OPEN.encode('utf-8'),
      self.EVAL_DATA_CLOSE.encode('utf-8'): self.EVAL_DATA_OPEN.encode('utf-8'),
      self.SEQUENCE_CLOSE.encode('utf-8'):  self.SEQUENCE_OPEN.encode('utf-8'),
    }

    association_operator    = set([self.ASSOCIATION_OPERATOR.encode('utf-8')])
    quote_operator          = set([self.QUOTE_OPERATOR.encode('utf-8')])
    unquote_operator        = set([self.UNQUOTE_OPERATOR.encode('utf-8')])
    unquote_splice_operator = set([self.UNQUOTE_SPLICE_OPERATOR.encode('utf-8')])

    parens = []
    state = INITIAL
    for c,n in lookahead(iterable):
      if state == INITIAL:
        if c in association_operator:    yield self.ASSOCIATION_OPERATOR;    continue
        if c in quote_operator:          yield self.QUOTE_OPERATOR;          continue
        if c in unquote_operator:        yield self.UNQUOTE_OPERATOR;        continue
        if c in unquote_splice_operator: yield self.UNQUOTE_SPLICE_OPERATOR; continue

        if c in parenopen:
          if   c in parenopen_tuple:     token = self.TUPLE_OPEN
          elif c in parenopen_eval_data: token = self.EVAL_DATA_OPEN
          elif c in parenopen_sequence:  token = self.SEQUENCE_OPEN
          else:
            raise self.SyntaxError(
              u"internal error: unexpected matched opening syntax: "
              u"%s" % repr(c))
          parens.append(c); yield token; continue

        if c in parenclose:
          if   c in parenclose_tuple:     token = self.TUPLE_CLOSE
          elif c in parenclose_eval_data: token = self.EVAL_DATA_CLOSE
          elif c in parenclose_sequence:  token = self.SEQUENCE_CLOSE
          else:
            raise self.SyntaxError(
              u"internal error: unexpected matched closing syntax: "
              u"%s" % repr(c))
          if not parens:
            raise self.SyntaxError(
              u"unexpected closing syntax at top level: %s" % repr(c))
          if parens[-1] not in parenmap[c]:
            raise self.SyntaxError(
              u"mismatched opening and closing syntax: "
              u"%s does not match %s" % (repr(parens[-1]), repr(c)))
          parens = parens[:-1]; yield token; continue

        if c in '123456789':
          state, value = LENGTH, c
          # Pass-through to LENGTH handler below

      if state == LENGTH:
        # Fill until n is not a digit:
        if n is not None and n in '0123456789':
          value += n; continue
        # Then reset DFA, process, and yield:
        else:
          state, count = SEPARATOR, int(value); continue

      if state == SEPARATOR:
        if c != ':':
          raise self.SyntaxError(
            u"expected separator, found unexpected character instead: "
            u"%s" % repr(c))
        state, bytes = SYMBOL, []; continue

      if state == SYMBOL:
        bytes.append(c)
        count -= 1
        if not count:
          state = INITIAL; yield ''.join(bytes); continue

    # If we've made it this far, then we've exhausted the input, and are not
    # in a state of expecting more input. As a generator we signal that we are
    # now done creating new tokens by raising a StopIteration exception.
    raise StopIteration

# ===----------------------------------------------------------------------===
# End of File
# ===----------------------------------------------------------------------===
