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

# Haiku language, pickler abstract base class
from base import BasePickler

# Haiku language, type definitions
from haiku.types import ByteArray, UnicodeString, Sequence, Dictionary, \
  Boolean, Integer, Omega

# Python patterns, lookahead generator
from python_patterns.itertools import lookahead

# Python standard library, Base64 encoding
from binascii import b2a_base64

class SimpleExpressionPickler(BasePickler):
  """Implements a serialization format for a variant of classic Lisp s-
  expression notation, here renamed “Simple Expressions”. Simple expressions
  are Lisp's lambda calculus expressed through parenthetical prefix notation.
  Simple expressions are meant to be the least complex syntax for for
  representing Lisp as Unicode text--a practical compromise between binary-
  encoded canonical expressions and much more human-readable meta expressions.
  
    >>> from haiku.pickle import SimpleExpressionPickler
    >>> pickler = SimpleExpressionPickler()
    >>> pickler.loads(u'(+ 1 2 3)')
    [['+', 1L, 2L, 3L]]
    >>> pickler.loads(u'(+ 1 2)\n(print "Hello world!")')
    [['+', 1L, 2L], ['print', u'Hello world!']]
    >>> pickler.dumps(['*',3L,['+',1L,6L]])
    u'(* 3 (+ 1 6))'
  """
  # Numbers (integers) are one or more decimal digits, optionally starting
  # with either a plus or minus sign. (Note: there cannot be any whitespace
  # between the +/- sign and the digits, or else the sign will be interpreted
  # as an identifier.)
  num_initial    = "0123456789+-"
  num_subsequent = "0123456789"
  
  # Identifiers include what in most other languages would be considered
  # symbols/operators. Aside from some select punctuation, it's pretty much
  # anything-goes with respect to non-whitespace, non-control ASCII
  # characters.
  id_initial    = u"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!?*+-/%\\&|^~<=>"
  id_subsequent = id_initial + num_subsequent

  def dump(self, ostream, *args, **kwargs):
    """Serializes a Python-represented Lisp expression into s-expression
    notation with Unicode encoding (`'utf-8'` unless overridden with the
    optional keyword parameter `'encoding'`), and writes the resulting string
    to the duck-typed `ostream` file-like object."""
    kwargs.setdefault('encoding', 'utf-8')
    # FIXME: `dump()` and `dumps()` should be rewritten so that `dump()` does
    #        all of the work, and `dumps()` calls dump with a `StringIO`
    #        object. That way s-expressions can be written to disk as they are
    #        generated, instead of having to generate the entire s-expression
    #        string first, as is the case now.
    return ostream.write(self.dumps(*args).encode(kwargs['encoding']))

  def dumps(self, *args):
    """Serialize a Python-represented Lisp expression into s-expression
    notation in a Unicode string.
    
      >>> from haiku.pickle import SimpleExpressionPickler
      >>> pickler = SimpleExpressionPickler()
      >>> pickler.dumps(['*',3L,['+',1L,6L]])
      u'(* 3 (+ 1 6))'
    """
    # `dumps()` is allowed an infinite number of positional arguemnts, each of
    # which must be a Python-represented Lisp expression. These are converted
    # into s-expression notation, then joined together with whitespace.
    if len(args) < 1:
      return u""
    elif len(args) > 1:
      return u" ".join(map(self.dumps, args))
    # Otherwise only one positional arguement is given, and our task is to
    # convert it to s-expression notation.
    expression = args[0]

    # None/nil value:
    if isinstance(expression, Omega):
      return u"#nil"

    # Boolean literals:
    elif isinstance(expression, Boolean):
      if expression == True:
        return u"#t"
      else:
        return u"#f"

    # Integer literals:
    elif isinstance(expression, Integer):
      return unicode(expression)

    # Byte-array literals:
    elif isinstance(expression, ByteArray):
      # An empty byte-array is the #nil value
      if not len(expression):
        return u"#nil"
      # A byte-array that meets the definition of an identifier is embedded
      # directly:
      if expression[0] in self.id_initial:
        if reduce(lambda x,y:x and y,
              map(lambda c:c in self.id_subsequent, expression[1:]), True):
          return u"%s" % expression
      # All other byte-arrays are Base64-encoded
      return u"%s" % ('(byte-array '+b2a_base64(expression).strip()+')')

    # Sequences:
    elif isinstance(expression, Sequence):
      return u"("+self.dumps(*expression)+u")"

    # Unicode literals:
    elif isinstance(expression, UnicodeString):
      return u'"'+expression.replace(u'"',u'\\"')+u'"'

    # In the middle of implementation I realized the syntax was ambiguous and
    # a little clunky. There's got to be a better way to do it. Since we're
    # not using dictionaries (yet), I've commented out the code that deals
    # with them. -MF
    #
    # FIXME: figure out exactly what dictionary syntax should look like.
    #
    # Dictionaries:
    #elif isinstance(expression, Dictionary):
    #  return u"("+u" ".join(
    #    [u" ".join([
    #      u":",
    #      self.dumps(key),
    #      self.dumps(expression[key]),
    #    ]) for key in sorted(expression.keys())]
    #  )+u")"

  def load(self, istream, **kwargs):
    """Deserializes a Lisp expression from an input stream in “Simple
    Expression” notation to Python objects."""
    # FIXME: refactor `loads()` functionality into `load()`, performing
    #        tokenization with a buffer so that large expressions can be
    #        deserialized without having to first load the entire expression
    #        into memory.
    kwargs.setdefault('encoding', 'utf-8')
    expression = istream.read().decode(kwargs['encoding'])
    return self.loads(expression)

  def loads(self, *args):
    """Deserializes a Lisp expression from a Unicode represented string in
    “Simple Expression” notation to Python objects."""
    
    if len(args) < 1:
      return []
    elif len(args) > 1:
      return [self.loads(arg) for arg in args]

    def tokenize(self, iterable):
      from tokenize import TokenError
      
      INITIAL  = 0
      SYMBOL   = 1
      CONSTANT = 2
      NUMBER   = 3
      UNICODE  = 4
      
      parens = u""
      parenmap = {u")": u"("}
      
      value = u""
      count = 0
      state = INITIAL
      for c,n in lookahead(iterable):
        if state == INITIAL:
          #
          if not len(c.strip()): continue
          
          #
          elif c == u"(": parens+=c; yield '('; continue
          elif c == u")":
            if parens[-1] != parenmap[c]:
              raise TokenError
            else:
              parens = parens[:-1]
              yield ')'; continue
          
          #
          #elif c == u":":
          #  yield ':'
          #  continue
          
          #
          elif c in self.id_initial:
            if c in self.num_initial and n in self.num_subsequent:
              state = NUMBER
              value = c
              # Pass-through to NUMBER handler below
            else:
              state = SYMBOL
              value = c
              # Pass-through to SYMBOL handler below
          
          #
          elif c == u"#":
            state = CONSTANT
            value = u""
            # Pass-through to CONSTANT handler below
          
          #
          elif c in self.num_initial:
            state = NUMBER
            value = c
          
          #
          elif c == u"\"":
            state = UNICODE
            value = ''
            count = 0
            continue
        
        if state == SYMBOL or state == CONSTANT:
          # Wait for n in id_initial:
          if not len(value):
            if n is None:              raise TokenError
            elif not len(n.strip()):   continue
            elif n in self.id_initial: value+=n; continue
            else:                      raise TokenError
          # Fill until n not in id_subsequent:
          else:
            if n is not None and len(n.strip()) and n in self.id_subsequent:
              value += n
              continue
            else:
              if state == SYMBOL:
                state = INITIAL
                yield ByteArray(value.encode('utf-8'))
                continue
              elif state == CONSTANT:
                if   value == u"nil": state=INITIAL; yield None;  continue
                elif value == u"f":   state=INITIAL; yield False; continue
                elif value == u"t":   state=INITIAL; yield True;  continue
                else:                 raise TokenError
              else:
                raise TokenError
        
        if state == NUMBER:
          # Wait for n in num_initial:
          if not len(value):
            if n is None:               raise TokenError
            elif not len(n.strip()):    continue
            elif n in self.num_initial: value+=n; continue
            else:                       raise TokenError
          # Fill until n not in num_subsequent:
          else:
            if n is not None and len(n.strip()) and n in self.num_subsequent:
              value += n
              continue
            else:
              if state == NUMBER:
                state = INITIAL
                yield Integer(value)
              else:
                raise TokenError
        
        if state == UNICODE:
          if c is None:
            raise TokenError, u"unexpected end-of-file within unicode string"
          if c == u"\"":
            if not count%2:
              state = INITIAL
              yield UnicodeString(value.replace('\\"','"'))
              continue
          value += unicode(c)
          if c == u"\\": count += 1
          else:          count  = 0
          continue
      
      if len(parens):
        raise TokenError
      
      raise StopIteration
    
    def parse(tokens):
      """Parses a sequence of tokens into an abstract syntax tree, represented
      in Python as a nested list."""
      # All s-expressions must be enclosed with parentheses; an empty s-expression
      # is represented as “()”--the tokens ‘(’ and ‘)’. So it should never happen
      # that parse() is called on an empty token stream.
      if len(tokens) == 0:
        raise SyntaxError(u'unexpected EOF while parsing')

      # Our approach for parsing is to look at only the single next token in the
      # stream at a time. This is sufficient for parsing the very simple syntax of
      # crypto-Lisp.
      token = tokens.pop(0)

      # If an open-paren is encountered, we use recursion to handle the nested
      # s-expression.
      if '(' == token:
        l = []
        while ')' != tokens[0]:
          l.append(parse(tokens))
        tokens.pop(0) # the ')'
        
        # If the key-value operator `:` is encountered as the first element of
        # the list, a dictionary object is created. Successive key-value pairs
        # are combined together into a single `dict`.
        #if len(l) and ':' == l[0]:
        #  if not len(l)%3:
        #    raise SyntaxError(u'invalid number of parameters for dictionary construction')
        #  if not reduce(lambda x,y:x and y, map(lambda i:':'==l[i], xrange(0, len(l), 3))):
        #    raise SyntaxError(u'expected key-value operator ‘:’')
        #  if not reduce(lambda x,y:x and y, map(lambda i:isinstance(l[i+1], ByteArray), xrange(0, len(l), 3))):
        #    raise SyntaxError(u'key must be a symbol/byte-array')
        #  d = {}
        #  while ':' == token:
        #    if len(tokens) < 2:
        #      raise SyntaxError(u'key-value operator ‘:’ without key/value”')
        #    key    = tokens.pop(0)
        #    value  = tokens.pop(0)
        #    d[key] = value
        #    if not len(tokens) or ':' != tokens[0]:
        #      break
        #    token  = tokens.pop(0)
        #  return d

        return Sequence(l)

      # In a well-formed token stream, the close-paren should only be encountered
      # following an open-paren in the context above. Any close-paren encountered
      # at this point is unmatched.
      elif ')' == token:
        raise SyntaxError(u'unmatched ‘)’ in token stream')

      # Lisp has a very simple syntax: if it is not a lisp demarked by
      # parentheses, it is an atomic value.
      else:
        return token
    
    expression = []
    tokens = list(tokenize(self, args[0]))
    while tokens: expression.append(parse(tokens))
    return expression

# ===----------------------------------------------------------------------===
# End of File
# ===----------------------------------------------------------------------===
