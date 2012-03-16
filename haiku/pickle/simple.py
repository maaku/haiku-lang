#!/usr/bin/env python
# -*- coding: utf-8 -*-

# === haiku.pickle.simple -------------------------------------------------===
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

# Python standard library, Base64 encoding
from binascii import b2a_base64

# Python standard library, iteration tools
from itertools import count, izip

# Python patterns, lookahead generator
from python_patterns.itertools import lookahead

# Haiku language, type definitions
from haiku.types import *

# Haiku language, pickler abstract base class
from .base import BasePickler

__all__ = [
  'SimpleExpressionPickler',
]

# ===----------------------------------------------------------------------===

class SimpleExpressionPickler(BasePickler):
  """Implements a serialization format for a variant of classic Lisp s-
  expression notation--here renamed “Simple Expressions”--for the Lisp-like,
  tuple-oriented language that is haiku. Simple expressions are the lambda
  calculus expressed through parenthetical prefix notation using a tuple (map/
  dictionary in Python-speak) as the most basic type. Simple expressions are
  meant to be the least complex syntax for for representing haiku code or data
  as Unicode text--a practical compromise between binary-encoded canonical
  expressions and much more human-readable meta expressions.

    >>> from haiku.pickle import SimpleExpressionPickler
    >>> pickler = SimpleExpressionPickler()
    >>> pickler.loads(u'[+ 1 2 3]')
    {0L: {0L: '+', 1L: 1L, 2L: 2L, 3L: 3L}}
    >>> pickler.loads(u'[+ 1 2]\n[print "Hello world!"]')
    {0L: {0L: '+', 1L: 1L, 2L: 2L}, 1L: {0L: 'print', 1L: u'Hello world!'}}
    >>> pickler.dumps({0:'*',1:3,2:{0:'+',1:1,2:6}})
    u'[* 3 [+ 1 6]]'
  """
  # Various syntax/token constants, used within the load() and dump() methods.
  TUPLE_OPEN      = u"["
  TUPLE_CLOSE     = u"]"
  EVAL_DATA_OPEN  = u"{"
  EVAL_DATA_CLOSE = u"}"
  SEQUENCE_OPEN   = u"("
  SEQUENCE_CLOSE  = u")"

  ASSOCIATION_OPERATOR    = u":"
  QUOTE_OPERATOR          = u"'"
  UNQUOTE_OPERATOR        = u","
  UNQUOTE_SPLICE_OPERATOR = u"`"
  CONSTANT_INDICATOR      = u"#"
  COMMENT_INDICATOR       = u";"

  # Integers are one or more decimal digits, optionally starting with either a
  # plus or minus sign. (Note: there cannot be any whitespace between the +/-
  # sign and the digits, or else the sign will be misinterpreted as an
  # identifier.)
  INTEGER_INITIAL    = u"0123456789+-"
  INTEGER_SUBSEQUENT = u"0123456789"

  # Identifiers include what in most other languages would be considered
  # symbols/operators. Aside from some select punctuation, it's pretty much
  # anything-goes with respect to non-whitespace, non-control ASCII
  # characters.
  ID_INITIAL    = u"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!?*+-/%\\&|^~<=>"
  ID_SUBSEQUENT = ID_INITIAL + INTEGER_SUBSEQUENT

  # In the case of syntax, there is ambiguity in the result of the tokenizer.
  # Is `u":"` a Unicode string or the association operator? For that reason
  # the tokenizer returns a 2-tuple, with the first element specifying the
  # type (literal or syntax), and the second is the actual literal/syntax
  # value.
  TOKEN_LITERAL = 0
  TOKEN_SYNTAX  = 1

  def dump(self, ostream, *args, **kwargs):
    """Serializes a Python-represented haiku expression into simple-expression
    notation with Unicode encoding (`'utf-8'` unless overridden with the
    optional keyword parameter `'encoding'`), and writes the resulting string
    to the duck-typed `ostream` file-like object."""
    encoding = kwargs.pop('encoding', 'utf-8')
    # FIXME: `dump()` and `dumps()` should be rewritten so that `dump()` does
    #   all of the work, and `dumps()` calls dump with a `StringIO` object.
    #   That way simple-expressions can be written to disk as they are
    #   generated, instead of having to generate the entire s-expression
    #   string first, as is the case now.
    return ostream.write(self.dumps(*args, **kwargs).encode(encoding))

  def dumps(self, *args):
    """Serialize a Python-represented haiku expression into simple-expression
    notation in a Unicode string.

      >>> from haiku.pickle import SimpleExpressionPickler
      >>> pickler = SimpleExpressionPickler()
      >>> pickler.dumps({0:'*',1:3,2:{0:'+',1:1,2:6}})
      u'[* 3 [+ 1 6]]'
    """
    # `dumps()` is allowed an infinite number of positional arguemnts, each of
    # which must be a Python-represented haiku expression. These are converted
    # into simple-expression notation, then joined together with whitespace.
    if len(args) < 1:
      return u""
    elif len(args) > 1:
      return u" ".join(map(self.dumps, args))

    # Otherwise only one positional arguement is given, and our task is to
    # convert it to s-expression notation.
    return self._serialize(args[0])

  def load(self, istream, **kwargs):
    """Deserializes a haiku expression from an input stream in “Simple
    Expression” notation to Python objects."""
    # FIXME: refactor `loads()` functionality into `load()`, performing
    #        tokenization with a buffer so that large expressions can be
    #        deserialized without having to first load the entire expression
    #        into memory.
    encoding = kwargs.pop('encoding', 'utf-8')
    expression = istream.read().decode(encoding)
    return self.loads(expression, **kwargs)

  def loads(self, *args):
    """Deserializes a haiku expression from a Unicode represented string in
    “Simple Expression” notation to Python objects."""
    # `loads()` is allowed an infinite number of positional arguemnts, each of
    # which must be a simple expression Unicode string. These are converted
    # into Python objects, then combined together into a single Tuple.
    if len(args) < 1:
      return {}
    elif len(args) > 1:
      return Tuple([izip(count(), (self.loads(arg) for arg in args))])
    # Otherwise only one positional arguement is given, and our task is to
    # convert it to Python objects from s-expression notation.
    expression = args[0]

    return self._parse(self._tokenize(args[0]))

  def _serialize(self, expression):
    ""
    # None/nil/omega value:
    if isinstance(expression, OmegaCompatible):
      return u"".join([self.CONSTANT_INDICATOR, u"nil"])

    # Boolean literals:
    elif isinstance(expression, BooleanCompatible):
      if expression:
        return u"".join([self.CONSTANT_INDICATOR, u"t"])
      else:
        return u"".join([self.CONSTANT_INDICATOR, u"f"])

    # Integral numeric literals:
    elif isinstance(expression, IntegerCompatible):
      return unicode(expression)

    # Rational numeric literals:
    elif isinstance(expression, FractionCompatible):
      return u"".join([
        self.TUPLE_OPEN,
        u" ".join([
          u"rational",
          self.dumps(expression.numerator),
          self.dumps(expression.denominator),
        ]),
        self.TUPLE_CLOSE])

    # Unicode literals:
    elif isinstance(expression, UnicodeCompatible):
      return u"".join([u'"', expression.replace(u'"',u'\\"'), u'"'])

    # Byte-array literals:
    elif isinstance(expression, BytesCompatible):
      # An empty byte-array is the #nil value
      if not len(expression):
        return u"".join([self.CONSTANT_INDICATOR, u"nil"])

      # A byte-array that meets the definition of an identifier is embedded
      # directly:
      if expression[0] in self.ID_INITIAL:
        if all(c in self.ID_SUBSEQUENT for c in expression[1:]):
          return unicode(expression)

      # All other byte-arrays are Base64-encoded:
      return u"".join([
        self.TUPLE_OPEN,
        u" ".join([
          u"byte-array",
          b2a_base64(expression).strip()
        ]),
        self.TUPLE_CLOSE])

    # Sets:
    elif isinstance(expression, SetCompatible):
      return u"".join([
        self.TUPLE_OPEN,
        u" ".join([u"set", self.dumps(*sorted(expression))]),
        self.TUPLE_CLOSE])

    # FIXME: implement meta-values

    # Tuples(/maps/dictionaries):
    elif isinstance(expression, TupleCompatible):
      args = []
      kwargs = Tuple(expression)
      kwargs_keys = kwargs.keys()
      for key in count():
        if key in kwargs_keys:
          args.append(kwargs.pop(key))
        else:
          break
      return u"".join([
        self.TUPLE_OPEN,
        u"".join([
          self.dumps(*args),
          (len(args) and len(kwargs)) and u" " or u"",
          u" ".join(
            u"".join([
              self.dumps(key),
              self.ASSOCIATION_OPERATOR,
              self.dumps(expression[key]),
            ]) for key in sorted(kwargs.keys()))]),
        self.TUPLE_CLOSE])

    # Relations:
    elif isinstance(expression, RelationCompatible):
      raise NotImplementedError

    # Sequences(/lists):
    elif isinstance(expression, SequenceCompatible):
      return u"".join([
        self.SEQUENCE_OPEN,
        self.dumps(*expression),
        self.SEQUENCE_CLOSE])

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
    raise ValueError, (
      u"unrecognized input (not a valid expression): '%s'" % repr(expression))

  def _tokenize(self, iterable):
    """Takes a `unicode` string or other iterator of Unicode characters and
    divides it into lexicographical tokens. Acts as a generator returning
    2-tuples identifying the type of the token (syntax vs. literal) and the
    token value."""
    # The approach we take is that of a DFA (deterministic finite automaton),
    # a type of state machine. The five constants below are used to indicate
    # which state we are in.
    INITIAL, COMMENT, SYMBOL, CONSTANT, NUMBER, UNICODE = range(6)

    # The Unicode characters used for parenthetical syntax (tuples, evaluated
    # data, and sequences):
    parens               = []
    parenopen_tuple      = set([u'['])
    parenopen_eval_data  = set([u'{'])
    parenopen_sequence   = set([u'('])
    parenopen            = parenopen_sequence.union(
                             parenopen_eval_data.union(parenopen_tuple))
    parenclose_tuple     = set([u']'])
    parenclose_eval_data = set([u'}'])
    parenclose_sequence  = set([u')'])
    parenclose           = parenclose_sequence.union(
                             parenclose_eval_data.union(parenclose_tuple))
    parenmap = {
      u']': set([u'[']),
      u'}': set([u'{']),
      u')': set([u'(']),
    }

    # The Unicode characters which can be used to begin and end a Unicode
    # string literal:
    unicodemap = {
      u'"':  set([u'"']),
      u'”':  set([u'„', u'“', u'”']),
      u'’':  set([u'‚', u'‘', u'’']),
      u'»':  set([u'«', u'»']),
      u'«':  set([u'«', u'»']),
      u'‹':  set([u'‹', u'›']),
      u'›':  set([u'‹', u'›']),
      u'「':  set([u'」']),
      u'『':  set([u'』']),
    }
    unicodeopen  = reduce(lambda l,r:l.union(r), unicodemap.values())
    unicodeclose = set(unicodemap.keys())

    # The five special syntax characters for key/value mapping, quoting and
    # unquoting special forms, and constant values.
    association_operator    = set([u':'])
    quote_operator          = set([u"'"])
    unquote_operator        = set([u","])
    unquote_splice_operator = set([u"`"])
    constant_indicator      = set([u'#'])

    # Line comments/documentation:
    comment_indicator = set([u';'])

    # Set the initial state of the DFA:
    value   = u""
    count   = 0
    initial = u""
    state   = INITIAL
    # For the purposes of this DFA implementation, it is sufficient to look
    # at the current and next lexigraphical element only. We use the Python-
    # patterns `lookahead` generator to help us out here:
    for c,n in lookahead(iterable):
      if state == INITIAL:
        # Remove whitespace from consideration:
        if not len(c.strip()): continue

        # Handle the various single-character syntax operators:
        elif c in association_operator:    yield (self.TOKEN_SYNTAX, self.ASSOCIATION_OPERATOR);    continue
        elif c in quote_operator:          yield (self.TOKEN_SYNTAX, self.QUOTE_OPERATOR);          continue
        elif c in unquote_operator:        yield (self.TOKEN_SYNTAX, self.UNQUOTE_OPERATOR);        continue
        elif c in unquote_splice_operator: yield (self.TOKEN_SYNTAX, self.UNQUOTE_SPLICE_OPERATOR); continue

        # Transition to states handling sequential, nested syntaxes (maps,
        # evaluated data, sequences):
        elif c in parenopen:
          if   c in parenopen_tuple:     token = self.TUPLE_OPEN
          elif c in parenopen_eval_data: token = self.EVAL_DATA_OPEN
          elif c in parenopen_sequence:  token = self.SEQUENCE_OPEN
          else:
            raise self.TokenError, (
              u"internal error: unexpected matched opening syntax: "
              u"%s" % repr(c))
          parens.append(c); yield (self.TOKEN_SYNTAX, token); continue
        elif c in parenclose:
          if   c in parenclose_tuple:     token = self.TUPLE_CLOSE
          elif c in parenclose_eval_data: token = self.EVAL_DATA_CLOSE
          elif c in parenclose_sequence:  token = self.SEQUENCE_CLOSE
          else:
            raise self.TokenError, (
              u"internal error: unexpected matched closing syntax: "
              u"%s" % repr(c))
          if not parens:
            raise self.TokenError, (
              u"unexpected closing syntax at top level: %s" % repr(c))
          if parens[-1] not in parenmap[c]:
            raise self.TokenError, (
              u"mismatched opening and closing syntax: "
              u"%s does not match %s" % (repr(parens[-1]), repr(c)))
          parens = parens[:-1]
          yield (self.TOKEN_SYNTAX, token); continue

        # Transition to state handling Unicode string:
        elif c in unicodeopen:
          state, value, count, initial = UNICODE, u"", 0, c; continue

        # Transition to state handling named constants:
        elif c in constant_indicator:
          state, value = CONSTANT, u"" # Pass-through to CONSTANT handler below

        # Transition to states handling symbols and numeric types:
        # Transition to state handling line comments:
        elif c in comment_indicator:
          state, initial = COMMENT, state; continue

        elif c in self.SYMBOL_INITIAL:
          # Handle the special case of number prefixed with +/- sign:
          if c in self.INTEGER_INITIAL and n in self.INTEGER_SUBSEQUENT:
            state, value = NUMBER, c # Pass-through to NUMBER handler below
          # Otherwise it's an identifer for sure:
          else:
            state, value = SYMBOL, c # Pass-through to SYMBOL handler below
        elif c in self.INTEGER_INITIAL:
          state, value = NUMBER, c # Pass-through to NUMBER handler below

      # Comments are easy: eat whitespace until newline is reached
      if COMMENT == state:
        if len(u"".join([c, u"a"]).splitlines()) > 1:
          state, initial = initial, u""

      # Generally constants and symbols are treated similarly--they both read
      # in an identiier and yield. However whitespace is allowed between the
      # constant indicator and the name of the constant. Here we skip past
      # that whitespace:
      if CONSTANT == state and not len(value):
        if n is None:
          raise self.TokenError, (
            u"unexpected end-of-file before constant identifier")
        elif not len(n.strip()):   continue
        elif n in self.SYMBOL_INITIAL: value+=n; continue
        else:
          if n in comment_indicator:
            state, initial = COMMENT, state; continue
          raise self.TokenError, (
            u"unexpected character: %s; expected constant identifier" % repr(n))

      if state in (SYMBOL, CONSTANT):
        # Fill until n not in SYMBOL_SUBSEQUENT:
        if n is not None and len(n.strip()) and n in self.SYMBOL_SUBSEQUENT:
          value += n; continue
        # Then reset DFA, process, and yield:
        else:
          if SYMBOL == state:
            yield (self.TOKEN_LITERAL, Bytes(value.encode('utf-8')))
          elif CONSTANT == state:
            if   value == u"nil": yield (self.TOKEN_LITERAL, None)
            elif value == u"f":   yield (self.TOKEN_LITERAL, False)
            elif value == u"t":   yield (self.TOKEN_LITERAL, True)
            else:
              raise self.TokenError, (
                u"unrecognized constant name: %s" % repr(value))
          state = INITIAL; continue

      if state == NUMBER:
        # Fill until n not in INTEGER_SUBSEQUENT:
        if n is not None and len(n.strip()) and n in self.INTEGER_SUBSEQUENT:
          value += n; continue
        # Then reset DFA, process, and yield:
        else:
          state = INITIAL; yield (self.TOKEN_LITERAL, Integer(value)); continue

      if state == UNICODE:
        if c is None:
          raise self.TokenError, (
            u"unexpected end-of-file within unicode string")
        elif c in unicodeclose and initial in unicodemap[c] and not count%2:
          state = INITIAL; yield (
            self.TOKEN_LITERAL,
            Unicode(value.replace(u'\\"',u'"'))); continue
        if c == u"\\": count += 1
        else:          count  = 0
        if not (c == u"\\" and (n == u"\\" or initial in unicodemap.get(n, ())) and count%2):
          value += unicode(c)
        continue

    if len(parens):
      raise self.TokenError, (
        u"unexpected end-of-file with unmatched opening/closing syntax: "
        u"%s" % u", ".join(repr(x) for x in parens))

    if COMMENT == state:
      raise self.TokenError, (
        u"unexpected end-of-file within comment")

    # If we've made it this far, then we've exhausted the input, and are not
    # in a state of expecting more input. As a generator we signal that we are
    # done creating new tokens by raising a StopIteration exception.
    raise StopIteration

  def _parse(self, tokens):
    """Parses a sequence of tokens into an abstract syntax tree, represented
    as nested Python objects."""
    # Used in a few locations where a sentinel value is required that is not
    # also a valid Python-represented haiku expression.
    SENTINEL = object()

    # The short-hand quote syntax is transformed into a special-form lambda
    # expression. To prevent magic string values, the names are specified here
    # in `quotedmap`.
    quotedmap = {
      self.QUOTE_OPERATOR:          'quote',
      self.UNQUOTE_OPERATOR:        'unquote',
      self.UNQUOTE_SPLICE_OPERATOR: 'unquote-splice',
    }

    # `parenmap` matches opening to closing tokens.
    parenmap = {
      self.TUPLE_OPEN:     self.TUPLE_CLOSE,
      self.EVAL_DATA_OPEN: self.EVAL_DATA_CLOSE,
      self.SEQUENCE_OPEN:  self.SEQUENCE_CLOSE,
    }

    # Initialize DFA and related state variables:
    key    = SENTINEL
    count  = Integer(0)
    tuple_ = Tuple()

    quotes = []
    counts = []
    tuples = []
    parens = []

    for c, n in lookahead(tokens):
      # Our approach for parsing is to look at only the next two tokens in
      # the stream at a time. This is sufficient for parsing the very simple
      # syntax of Lisp.
      ct, cv = c
      nt, nv = n or (None, None)

      if self.TOKEN_LITERAL == ct:
        value = cv
        # Pass-through to key, value insertion below

      elif self.ASSOCIATION_OPERATOR == cv:
        if key is SENTINEL:
          raise self.SyntaxError, (
            u"detached association operator; no key specified")
        continue

      elif cv in (self.QUOTE_OPERATOR, self.UNQUOTE_OPERATOR, self.UNQUOTE_SPLICE_OPERATOR):
        quotes.append(quotedmap[cv]); continue

      elif cv in parenmap.keys():
        counts.append(count);  count  = Integer(0)
        tuples.append(tuple_); tuple_ = Tuple()
        parens.append(parenmap[cv]); continue

      elif cv in parenmap.values():
        if key is not SENTINEL:
          raise self.SyntaxError, (
            u"unexpected closing syntax at top level")
        if parens.pop(-1) != cv:
          raise self.SyntaxError, (
            u"mis-matched open/close syntax")

        if self.TUPLE_CLOSE == cv:
          value = tuple_
        elif self.EVAL_DATA_CLOSE == cv:
          value = Tuple([(Integer(0), quotedmap[self.QUOTE_OPERATOR]),
                         (Integer(1), Tuple([(k, Tuple([(Integer(0), quotedmap[self.UNQUOTE_OPERATOR]),
                                                        (Integer(1), v)]))
                                             for k,v in tuple_.items()]))])
        elif self.SEQUENCE_CLOSE == cv:
          if sorted(tuple_.keys()) != [Integer(x) for x in xrange(len(tuple_))]:
            raise self.SyntaxError, (
              u"illegal association operator within sequence expression")
          value = Sequence([tuple_[k] for k in sorted(tuple_.keys())])
        count  = counts.pop(-1)
        tuple_ = tuples.pop(-1)
        # Pass-through to key, value insertion below

      # Quote, unquote, unquote-splice handling:
      for quote in reversed(quotes):
        value = Tuple([(Integer(0), quote),
                       (Integer(1), value)])
      quotes = []

      if key is SENTINEL:
        if n == (self.TOKEN_SYNTAX, self.ASSOCIATION_OPERATOR):
          key = value; continue
        else:
          key = count; count += Integer(1)

      # Special unicode key handling:
      if isinstance(key, UnicodeCompatible):
        key = Unicode(Unicode(u"").join([Unicode(u"\ufeff"), key]))

      # Key, value insertion:
      tuple_[key] = value
      key = SENTINEL

    return tuple_

# ===----------------------------------------------------------------------===
# End of File
# ===----------------------------------------------------------------------===
