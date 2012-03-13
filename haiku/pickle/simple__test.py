#!/usr/bin/env python
# -*- coding: utf-8 -*-

# === haiku.pickle.simple__test -------------------------------------------===
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

# Python standard library, unit-testing
import unittest2

# Python patterns, scenario unit-testing
from python_patterns.unittest.scenario import ScenarioMeta, ScenarioTest

# Python standard library, string input/output
from StringIO import StringIO

# Haiku language, s-expression pickler
from haiku.pickle import SimpleExpressionPickler

SCENARIOS = [
  # Empty string (edge case):
  dict(lisp=u'',                      python={}),
  
  # Symbols:
  dict(lisp=u'abc',                   python={0:'abc'}),
  dict(lisp=u'a b c',                 python={0:'a',1:'b',2:'c'}),
  dict(lisp=u'#nil',                  python={0:''}, skip=['load']),
  dict(lisp=u'[byte-array IA==]',     python={0:' '}, skip=['load']),
  dict(lisp=u'[byte-array AA==]',     python={0:'\0'}, skip=['load']),
  dict(lisp=u'[byte-array AQIDBA==]', python={0:'\x01\x02\x03\x04'}, skip=['load']),
  
  # Constants:
  dict(lisp=u'#nil',                  python={0:None}),
  dict(lisp=u'#f',                    python={0:False}),
  dict(lisp=u'#t',                    python={0:True}),
  
  # Integers:
  dict(lisp=u'0',                     python={0:0L}),
  dict(lisp=u'1',                     python={0:1L}),
  dict(lisp=u'-1',                    python={0:-1L}),
  dict(lisp=u'36893488147419103232',  python={0:long(2**65)}),
  dict(lisp=u'-36893488147419103232', python={0:-long(2**65)}),
  
  # Unicode strings:
  dict(lisp=u'""',                    python={0:u''}),
  dict(lisp=u'"-"',                   python={0:u'-'}),
  dict(lisp=u'"\\""',                 python={0:u'"'}),
  dict(lisp=u'"tsch\xfcss!"',         python={0:u'tschüss!'}),
  dict(lisp=u'"\u3053\u3093\u306b\u3061\u306f\u4e16\u754c\uff01"', python={0:u'こんにちは世界！'}),
  
  # Lists:
  dict(lisp=u'[]',                    python={0:{}}),
  dict(lisp=u'[a]',                   python={0:{0:'a'}}),
  dict(lisp=u'[a b c]',               python={0:{0:'a',1:'b',2:'c'}}),
  dict(lisp=u'[1 -2 3]',              python={0:{0:1L,1:-2L,2:3L}}),
  dict(lisp=u'[a [b 1] [c 2]]',       python={0:{0:'a',1:{0:'b',1:1L},2:{0:'c',1:2L}}}),
  
  # Dictionaries:
  #dict(lisp=u'[:]',                               python={0:{}}),
  #dict(lisp=u'[: one 1]',                         python={0:{'one':1L}}),
  #dict(lisp=u'[: one 1 : two 2]',                 python={0:{'one':1L,'two':2L}}),
  #dict(lisp=u'[: one 1 : three (+ 1 2) : two 2]', python={0:{'one':1L,'two':2L,'three':['+',1L,2L]}}),
  
  # Integer arithmetic operators:
  dict(lisp=u'[+ 0 1]',               python={0:{0:'+',1:0L,2:1L}}),
  dict(lisp=u'[+ 2 3 4]',             python={0:{0:'+',1:2L,2:3L,3:4L}}),
  dict(lisp=u'[+ 5 6 7 8]',           python={0:{0:'+',1:5L,2:6L,3:7L,4:8L}}),
  dict(lisp=u'[- 0 1]',               python={0:{0:'-',1:0L,2:1L}}),
  dict(lisp=u'[- 2 3 4]',             python={0:{0:'-',1:2L,2:3L,3:4L}}),
  dict(lisp=u'[- 5 6 7 8]',           python={0:{0:'-',1:5L,2:6L,3:7L,4:8L}}),
  dict(lisp=u'[/ 0 1]',               python={0:{0:'/',1:0L,2:1L}}),
  dict(lisp=u'[/ 2 3 4]',             python={0:{0:'/',1:2L,2:3L,3:4L}}),
  dict(lisp=u'[/ 5 6 7 8]',           python={0:{0:'/',1:5L,2:6L,3:7L,4:8L}}),
  dict(lisp=u'[* 0 1]',               python={0:{0:'*',1:0L,2:1L}}),
  dict(lisp=u'[* 2 3 4]',             python={0:{0:'*',1:2L,2:3L,3:4L}}),
  dict(lisp=u'[* 5 6 7 8]',           python={0:{0:'*',1:5L,2:6L,3:7L,4:8L}}),
  dict(lisp=u'[** 0 8]',              python={0:{0:'**',1:0L,2:8L}}),
  dict(lisp=u'[** 1 4]',              python={0:{0:'**',1:1L,2:4L}}),
  dict(lisp=u'[** 2 3]',              python={0:{0:'**',1:2L,2:3L}}),
  dict(lisp=u'[** 3 3]',              python={0:{0:'**',1:3L,2:3L}}),
  dict(lisp=u'[** 7 2 5]',            python={0:{0:'**',1:7L,2:2L,3:5L}}),
  
  # Logical operators:
  dict(lisp=u'[& #f #f]',             python={0:{0:'&',1:False,2:False}}),
  dict(lisp=u'[& #f #t]',             python={0:{0:'&',1:False,2: True}}),
  dict(lisp=u'[& #t #f]',             python={0:{0:'&',1: True,2:False}}),
  dict(lisp=u'[& #t #t]',             python={0:{0:'&',1: True,2: True}}),
  dict(lisp=u'[| #f #f]',             python={0:{0:'|',1:False,2:False}}),
  dict(lisp=u'[| #f #t]',             python={0:{0:'|',1:False,2: True}}),
  dict(lisp=u'[| #t #f]',             python={0:{0:'|',1: True,2:False}}),
  dict(lisp=u'[| #t #t]',             python={0:{0:'|',1: True,2: True}}),
  dict(lisp=u'[^ #f #f]',             python={0:{0:'^',1:False,2:False}}),
  dict(lisp=u'[^ #f #t]',             python={0:{0:'^',1:False,2: True}}),
  dict(lisp=u'[^ #t #f]',             python={0:{0:'^',1: True,2:False}}),
  dict(lisp=u'[^ #t #t]',             python={0:{0:'^',1: True,2: True}}),
  dict(lisp=u'[~ #f]',                python={0:{0:'~',1:False}}),
  dict(lisp=u'[~ #t]',                python={0:{0:'~',1: True}}),
  
  # Relational operators:
  dict(lisp=u'[< 0 0]',               python={0:{0: '<',1:0L,2:0L}}),
  dict(lisp=u'[< 0 1]',               python={0:{0: '<',1:0L,2:1L}}),
  dict(lisp=u'[< 1 0]',               python={0:{0: '<',1:1L,2:0L}}),
  dict(lisp=u'[< 1 1]',               python={0:{0: '<',1:1L,2:1L}}),
  dict(lisp=u'[<= 0 0]',              python={0:{0:'<=',1:0L,2:0L}}),
  dict(lisp=u'[<= 0 1]',              python={0:{0:'<=',1:0L,2:1L}}),
  dict(lisp=u'[<= 1 0]',              python={0:{0:'<=',1:1L,2:0L}}),
  dict(lisp=u'[<= 1 1]',              python={0:{0:'<=',1:1L,2:1L}}),
  dict(lisp=u'[= 0 0]',               python={0:{0: '=',1:0L,2:0L}}),
  dict(lisp=u'[= 0 1]',               python={0:{0: '=',1:0L,2:1L}}),
  dict(lisp=u'[= 1 0]',               python={0:{0: '=',1:1L,2:0L}}),
  dict(lisp=u'[= 1 1]',               python={0:{0: '=',1:1L,2:1L}}),
  dict(lisp=u'[>= 0 0]',              python={0:{0:'>=',1:0L,2:0L}}),
  dict(lisp=u'[>= 0 1]',              python={0:{0:'>=',1:0L,2:1L}}),
  dict(lisp=u'[>= 1 0]',              python={0:{0:'>=',1:1L,2:0L}}),
  dict(lisp=u'[>= 1 1]',              python={0:{0:'>=',1:1L,2:1L}}),
  dict(lisp=u'[> 0 0]',               python={0:{0: '>',1:0L,2:0L}}),
  dict(lisp=u'[> 0 1]',               python={0:{0: '>',1:0L,2:1L}}),
  dict(lisp=u'[> 1 0]',               python={0:{0: '>',1:1L,2:0L}}),
  dict(lisp=u'[> 1 1]',               python={0:{0: '>',1:1L,2:1L}}),
  dict(lisp=u'[~= 0 0]',              python={0:{0:'~=',1:0L,2:0L}}),
  dict(lisp=u'[~= 0 1]',              python={0:{0:'~=',1:0L,2:1L}}),
  dict(lisp=u'[~= 1 0]',              python={0:{0:'~=',1:1L,2:0L}}),
  dict(lisp=u'[~= 1 1]',              python={0:{0:'~=',1:1L,2:1L}}),
  
  # String operators:
  dict(lisp=u'[+ "Hello, " "world!"]', python={0:{0:'+',1:u"Hello, ",2:u"world!"}}),
]

class TestSimpleExpressionPickler(unittest2.TestCase):
  """Test serialization and deserialization of Lisp code to/from Python
  objects using the `SimpleExpressionPickler` class."""
  __metaclass__ = ScenarioMeta
  _pickler = SimpleExpressionPickler
  def setUp(self, *args, **kwargs):
    self.pickler = self._pickler()
  class test_dump(ScenarioTest):
    scenarios = SCENARIOS
    def __test__(self, lisp, python, skip=[]):
      # Check if it is okay to run this scenario:
      if 'dump' in skip:
        self.skipTest(u"Scenario not compatible with pickle.dump(); skipping...")
      # Compare dump(StringIO) vs the prepared Lisp:
      ostream = StringIO()
      self.pickler.dump(ostream, python)
      self.assertEqual(
        u"".join([u"[", lisp, u"]"]),
        ostream.getvalue().decode('utf-8'))
  class test_dump_utf_16(ScenarioTest):
    scenarios = SCENARIOS
    def __test__(self, lisp, python, skip=[]):
      # Check if it is okay to run this scenario:
      if 'dump' in skip:
        self.skipTest(u"Scenario not compatible with pickle.dump(); skipping...")
      # Compare dump(StringIO) vs the prepared Lisp:
      ostream = StringIO()
      self.pickler.dump(ostream, python, encoding='utf-16')
      self.assertEqual(
        u"".join([u"[", lisp, u"]"]),
        ostream.getvalue().decode('utf-16'))
  class test_dumps(ScenarioTest):
    scenarios = SCENARIOS
    def __test__(self, lisp, python, skip=[]):
      # Check if it is okay to run this scenario:
      if 'dump' in skip:
        self.skipTest(u"Scenario not compatible with pickle.dump(); skipping...")
      # Compare dumps() vs the prepared Lisp:
      self.assertEqual(
        u"".join([u"[", lisp, u"]"]),
        self.pickler.dumps(python))
  class test_load(ScenarioTest):
    scenarios = SCENARIOS
    def __test__(self, lisp, python, skip=[]):
      # Check if it is okay to run this scenario:
      if 'load' in skip:
        self.skipTest(u"Scenario not compatible with pickle.load(); skipping...")
      # Compare loads(StringIO) vs the prepared Python:
      istream = StringIO(lisp.encode('utf-8')) # utf-8 is load()'s default
      actual = self.pickler.load(istream)
      self.assertEqual(actual, python)
  class test_load_utf_16(ScenarioTest):
    scenarios = SCENARIOS
    def __test__(self, lisp, python, skip=[]):
      # Check if it is okay to run this scenario:
      if 'load' in skip:
        self.skipTest(u"Scenario not compatible with pickle.load(); skipping...")
      # Compare loads(StringIO) vs the prepared Python:
      istream = StringIO(lisp.encode('utf-16'))
      actual = self.pickler.load(istream, encoding='utf-16')
      self.assertEqual(actual, python)
  class test_loads(ScenarioTest):
    scenarios = SCENARIOS
    def __test__(self, lisp, python, skip=[]):
      # Check if it is okay to run this scenario:
      if 'load' in skip:
        self.skipTest(u"Scenario not compatible with pickle.load(); skipping...")
      # Compare loads() vs the prepared Python:
      self.assertEqual(self.pickler.loads(lisp), python)

# ===----------------------------------------------------------------------===
# End of File
# ===----------------------------------------------------------------------===
