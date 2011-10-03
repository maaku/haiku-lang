#!/usr/bin/env python
# -*- coding: utf-8 -*-

# === haiku.pickle.base ---------------------------------------------------===
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

from abc import ABCMeta, abstractmethod

class BasePickler(object):
  """A pickler provides a mechanism for serializing Lisp expressions into
  standard, widely-understood formats."""
  __metaclass__ = ABCMeta

  @abstractmethod
  def dump(self, ostream, *args, **kwargs):
    """"""
    return super(BasePickler, self).dump(*args, **kwargs)

  @abstractmethod
  def dumps(self, *args, **kwargs):
    """"""
    return super(BasePickler, self).dumps(*args, **kwargs)

  @abstractmethod
  def load(self, istream, *args, **kwargs):
    """"""
    return super(BasePickler, self).load(*args, **kwargs)

  @abstractmethod
  def loads(self, *args, **kwargs):
    """"""
    return super(BasePickler, self).loads(*args, **kwargs)

# ===----------------------------------------------------------------------===
# End of File
# ===----------------------------------------------------------------------===
