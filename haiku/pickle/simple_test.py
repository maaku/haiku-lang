#!/usr/bin/env python
# -*- coding: utf-8 -*-

# === haiku.pickle.simple_test --------------------------------------------===
# Copyright © 2011, RokuSigma Inc. (Mark Friedenbach <mark@roku-sigma.com>)
# as an unpublished work.
#
# RokuSigma Inc. (the “Company”) Confidential
#
# NOTICE: All information contained herein is, and remains the property of the
# Company. The intellectual and technical concepts contained herein are
# proprietary to the Company and may be covered by U.S. and Foreign Patents,
# patents in process, and are protected by trade secret or copyright law.
# Dissemination of this information or reproduction of this material is
# strictly forbidden unless prior written permission is obtained from the
# Company. Access to the source code contained herein is hereby forbidden to
# anyone except current Company employees, managers or contractors who have
# executed Confidentiality and Non-disclosure agreements explicitly covering
# such access.
#
# The copyright notice above does not evidence any actual or intended
# publication or disclosure of this source code, which includes information
# that is confidential and/or proprietary, and is a trade secret, of the
# Company. ANY REPRODUCTION, MODIFICATION, DISTRIBUTION, PUBLIC PERFORMANCE,
# OR PUBLIC DISPLAY OF OR THROUGH USE OF THIS SOURCE CODE WITHOUT THE EXPRESS
# WRITTEN CONSENT OF THE COMPANY IS STRICTLY PROHIBITED, AND IN VIOLATION OF
# APPLICABLE LAWS AND INTERNATIONAL TREATIES. THE RECEIPT OR POSSESSION OF
# THIS SOURCE CODE AND/OR RELATED INFORMATION DOES NOT CONVEY OR IMPLY ANY
# RIGHTS TO REPRODUCE, DISCLOSE OR DISTRIBUTE ITS CONTENTS, OR TO MANUFACTURE,
# USE, OR SELL ANYTHING THAT IT MAY DESCRIBE, IN WHOLE OR IN PART.
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
  dict(lisp=u'',                      python=[]),
  
  # Symbols:
  dict(lisp=u'abc',                   python=['abc']),
  dict(lisp=u'a b c',                 python=['a','b','c']),
  dict(lisp=u'#nil',                  python=[''], skip=['load']),
  dict(lisp=u'(byte-array IA==)',     python=[' '], skip=['load']),
  dict(lisp=u'(byte-array AA==)',     python=['\0'], skip=['load']),
  dict(lisp=u'(byte-array AQIDBA==)', python=['\x01\x02\x03\x04'], skip=['load']),
  
  # Constants:
  dict(lisp=u'#nil',                  python=[None]),
  dict(lisp=u'#f',                    python=[False]),
  dict(lisp=u'#t',                    python=[True]),
  
  # Integers:
  dict(lisp=u'0',                     python=[0L]),
  dict(lisp=u'1',                     python=[1L]),
  dict(lisp=u'-1',                    python=[-1L]),
  dict(lisp=u'36893488147419103232',  python=[long(2**65)]),
  dict(lisp=u'-36893488147419103232', python=[-long(2**65)]),
  
  # Unicode strings:
  dict(lisp=u'""',                    python=[u'']),
  dict(lisp=u'"-"',                   python=[u'-']),
  dict(lisp=u'"\\""',                 python=[u'"']),
  dict(lisp=u'"tsch\xfcss!"',         python=[u'tschüss!']),
  dict(lisp=u'"\u3053\u3093\u306b\u3061\u306f\u4e16\u754c\uff01"', python=[u'こんにちは世界！']),
  
  # Lists:
  dict(lisp=u'()',                    python=[[]]),
  dict(lisp=u'(a)',                   python=[['a']]),
  dict(lisp=u'(a b c)',               python=[['a','b','c']]),
  dict(lisp=u'(1 -2 3)',              python=[[1L,-2L,3L]]),
  dict(lisp=u'(a (b 1) (c 2))',       python=[['a',['b',1L],['c',2L]]]),
  
  # Dictionaries:
  #dict(lisp=u'(:)',                               python=[{}]),
  #dict(lisp=u'(: one 1)',                         python=[{'one':1L}]),
  #dict(lisp=u'(: one 1 : two 2)',                 python=[{'one':1L,'two':2L}]),
  #dict(lisp=u'(: one 1 : three (+ 1 2) : two 2)', python=[{'one':1L,'two':2L,'three':['+',1L,2L]}]),
  
  # Integer arithmetic operators:
  dict(lisp=u'(+ 0 1)',               python=[['+',0L,1L]]),
  dict(lisp=u'(+ 2 3 4)',             python=[['+',2L,3L,4L]]),
  dict(lisp=u'(+ 5 6 7 8)',           python=[['+',5L,6L,7L,8L]]),
  dict(lisp=u'(- 0 1)',               python=[['-',0L,1L]]),
  dict(lisp=u'(- 2 3 4)',             python=[['-',2L,3L,4L]]),
  dict(lisp=u'(- 5 6 7 8)',           python=[['-',5L,6L,7L,8L]]),
  dict(lisp=u'(/ 0 1)',               python=[['/',0L,1L]]),
  dict(lisp=u'(/ 2 3 4)',             python=[['/',2L,3L,4L]]),
  dict(lisp=u'(/ 5 6 7 8)',           python=[['/',5L,6L,7L,8L]]),
  dict(lisp=u'(* 0 1)',               python=[['*',0L,1L]]),
  dict(lisp=u'(* 2 3 4)',             python=[['*',2L,3L,4L]]),
  dict(lisp=u'(* 5 6 7 8)',           python=[['*',5L,6L,7L,8L]]),
  dict(lisp=u'(** 0 8)',              python=[['**',0L,8L]]),
  dict(lisp=u'(** 1 4)',              python=[['**',1L,4L]]),
  dict(lisp=u'(** 2 3)',              python=[['**',2L,3L]]),
  dict(lisp=u'(** 3 3)',              python=[['**',3L,3L]]),
  dict(lisp=u'(** 7 2 5)',            python=[['**',7L,2L,5L]]),
  
  # Logical operators:
  dict(lisp=u'(& #f #f)',             python=[['&',False,False]]),
  dict(lisp=u'(& #f #t)',             python=[['&',False, True]]),
  dict(lisp=u'(& #t #f)',             python=[['&', True,False]]),
  dict(lisp=u'(& #t #t)',             python=[['&', True, True]]),
  dict(lisp=u'(| #f #f)',             python=[['|',False,False]]),
  dict(lisp=u'(| #f #t)',             python=[['|',False, True]]),
  dict(lisp=u'(| #t #f)',             python=[['|', True,False]]),
  dict(lisp=u'(| #t #t)',             python=[['|', True, True]]),
  dict(lisp=u'(^ #f #f)',             python=[['^',False,False]]),
  dict(lisp=u'(^ #f #t)',             python=[['^',False, True]]),
  dict(lisp=u'(^ #t #f)',             python=[['^', True,False]]),
  dict(lisp=u'(^ #t #t)',             python=[['^', True, True]]),
  dict(lisp=u'(~ #f)',                python=[['~',False]]),
  dict(lisp=u'(~ #t)',                python=[['~', True]]),
  
  # Relational operators:
  dict(lisp=u'(< 0 0)',               python=[[ '<',0L,0L]]),
  dict(lisp=u'(< 0 1)',               python=[[ '<',0L,1L]]),
  dict(lisp=u'(< 1 0)',               python=[[ '<',1L,0L]]),
  dict(lisp=u'(< 1 1)',               python=[[ '<',1L,1L]]),
  dict(lisp=u'(<= 0 0)',              python=[['<=',0L,0L]]),
  dict(lisp=u'(<= 0 1)',              python=[['<=',0L,1L]]),
  dict(lisp=u'(<= 1 0)',              python=[['<=',1L,0L]]),
  dict(lisp=u'(<= 1 1)',              python=[['<=',1L,1L]]),
  dict(lisp=u'(= 0 0)',               python=[[ '=',0L,0L]]),
  dict(lisp=u'(= 0 1)',               python=[[ '=',0L,1L]]),
  dict(lisp=u'(= 1 0)',               python=[[ '=',1L,0L]]),
  dict(lisp=u'(= 1 1)',               python=[[ '=',1L,1L]]),
  dict(lisp=u'(>= 0 0)',              python=[['>=',0L,0L]]),
  dict(lisp=u'(>= 0 1)',              python=[['>=',0L,1L]]),
  dict(lisp=u'(>= 1 0)',              python=[['>=',1L,0L]]),
  dict(lisp=u'(>= 1 1)',              python=[['>=',1L,1L]]),
  dict(lisp=u'(> 0 0)',               python=[[ '>',0L,0L]]),
  dict(lisp=u'(> 0 1)',               python=[[ '>',0L,1L]]),
  dict(lisp=u'(> 1 0)',               python=[[ '>',1L,0L]]),
  dict(lisp=u'(> 1 1)',               python=[[ '>',1L,1L]]),
  dict(lisp=u'(~= 0 0)',              python=[['~=',0L,0L]]),
  dict(lisp=u'(~= 0 1)',              python=[['~=',0L,1L]]),
  dict(lisp=u'(~= 1 0)',              python=[['~=',1L,0L]]),
  dict(lisp=u'(~= 1 1)',              python=[['~=',1L,1L]]),
  
  # String operators:
  dict(lisp=u'(+ "Hello, " "world!")', python=[['+',u"Hello, ",u"world!"]]),
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
      self.pickler.dump(ostream, *python)
      self.assertEqual(lisp, ostream.getvalue().decode('utf-8'))
  class test_dump_utf_16(ScenarioTest):
    scenarios = SCENARIOS
    def __test__(self, lisp, python, skip=[]):
      # Check if it is okay to run this scenario:
      if 'dump' in skip:
        self.skipTest(u"Scenario not compatible with pickle.dump(); skipping...")
      # Compare dump(StringIO) vs the prepared Lisp:
      ostream = StringIO()
      self.pickler.dump(ostream, *python, encoding='utf-16')
      self.assertEqual(lisp, ostream.getvalue().decode('utf-16'))
  class test_dumps(ScenarioTest):
    scenarios = SCENARIOS
    def __test__(self, lisp, python, skip=[]):
      # Check if it is okay to run this scenario:
      if 'dump' in skip:
        self.skipTest(u"Scenario not compatible with pickle.dump(); skipping...")
      # Compare dumps() vs the prepared Lisp:
      self.assertEqual(lisp, self.pickler.dumps(*python))
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
