#!/usr/bin/env python
#
# Copyright 2009, Google Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#     * Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above
# copyright notice, this list of conditions and the following disclaimer
# in the documentation and/or other materials provided with the
# distribution.
#     * Neither the name of Google Inc. nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# originally from http://code.google.com/p/pywebsocket/source/browse/branches/update-key-gen/src/example/echo_client.py?r=252

import codecs
import logging
from md5 import md5
from optparse import OptionParser
import random
import re
import socket
import struct
import sys

def generate_request_security():
	"""Returns [(number, key1), (number, key2), eight_byte_token]"""
	return [generate_sec_websocket_key(), generate_sec_websocket_key(), generate_ws_datum()]

def generate_sec_websocket_key():
	# 4.1 16. let /spaces_n/ be a random integer from 1 to 12 inclusive.
	spaces = random.randint(1, 12)
	# 4.1 17. let /max_n/ be the largest integer not greater than
	#  4,294,967,295 divided by /spaces_n/.
	maxnum = 4294967295 / spaces
	# 4.1 18. let /number_n/ be a random integer from 0 to /max_n/
	# inclusive.
	number = random.randint(0, maxnum)
	# 4.1 19. let /product_n/ be the result of multiplying /number_n/ and
	# /spaces_n/ together.
	product = number * spaces
	# 4.1 20. let /key_n/ be a string consisting of /product_n/, expressed
	# in base ten using the numerals in the range U+0030 DIGIT ZERO (0) to
	# U+0039 DIGIT NINE (9).
	key = str(product)
	# 4.1 21. insert between one and twelve random characters from the
	# range U+0021 to U+002F and U+003A to U+007E into /key_n/ at random
	# positions.
	available_chars = range(0x21, 0x2f + 1) + range(0x3a, 0x7e + 1)
	n = random.randint(1, 12)
	for _ in range(n):
		ch = random.choice(available_chars)
		pos = random.randint(0, len(key))
		key = key[0:pos] + chr(ch) + key[pos:]
	# 4.1 22. insert /spaces_n/ U+0020 SPACE characters into /key_n/ at
	# random positions other than start or end of the string.
	for _ in range(spaces):
		pos = random.randint(1, len(key) - 1)
		key = key[0:pos] + ' ' + key[pos:]
	return number, key

def generate_ws_datum():
	# 4.1 26. let /key3/ be a string consisting of eight random bytes (or
	# equivalently, a random 64 bit integer encoded in a big-endian order).
	return ''.join([chr(random.randint(0, 255)) for _ in xrange(8)])

def hexify(s): return re.sub(".", lambda x: "%02x " % ord(x.group(0)), s)
