#!/usr/bin/env python

import os
import sys
import unittest
from client import TestClient
from server import TestServer
from tracecontext import Traceparent, Tracestate

client = None
server = None

def environ(name, default = None):
	if not name in os.environ:
		if default:
			os.environ[name] = default
		else:
			raise EnvironmentError('environment variable {} is not defined'.format(name))
	return os.environ[name]

STRICT_LEVEL = int(environ('STRICT_LEVEL', '2'))
print('STRICT_LEVEL: {}'.format(STRICT_LEVEL))

def setUpModule():
	global client
	global server
	environ('SERVICE_ENDPOINT')
	client = client or TestClient(host = '127.0.0.1', port = 7777, timeout = 5)
	server = server or TestServer(host = '127.0.0.1', port = 7777, timeout = 3)
	server.start()
	with client.scope() as scope:
		response = scope.send_request()

def tearDownModule():
	server.stop()

class TestBase(unittest.TestCase):
	import re
	traceparent_name_re = re.compile(r'^traceparent$', re.IGNORECASE)
	traceparent_format = r'^([0-9a-f]{2})-([0-9a-f]{32})-([0-9a-f]{16})-([0-9a-f]{2})$'
	traceparent_format_re = re.compile(traceparent_format)
	tracestate_name_re = re.compile(r'^tracestate$', re.IGNORECASE)

	def make_request(self, headers, count = 1):
		import pprint
		with client.scope() as scope:
			arguments = {
				'url': environ('SERVICE_ENDPOINT'),
				'headers': headers,
				'arguments': [],
			}
			for idx in range(count):
				arguments['arguments'].append({'url': scope.url(str(idx)), 'arguments': []})
			response = scope.send_request(arguments = arguments)
			verbose = ['', '']
			verbose.append('Harness trying to send the following request to your service {0}'.format(arguments['url']))
			verbose.append('')
			verbose.append('POST {} HTTP/1.1'.format(arguments['url']))
			for key, value in arguments['headers']:
				verbose.append('{}: {}'.format(key, value))
			verbose.append('')
			verbose.append(pprint.pformat(arguments['arguments']))
			verbose.append('')
			results = response['results'][0]
			if 'exception' in results:
				verbose.append('Harness got an exception {}'.format(results['exception']))
				verbose.append('')
				verbose.append(results['msg'])
			else:
				verbose.append('Your service {} responded with HTTP status {}'.format(arguments['url'], results['status']))
				verbose.append('')
				for key, value in results['headers']:
					verbose.append('{}: {}'.format(key, value))
				verbose.append('')
				if isinstance(results['body'], str):
					verbose.append(results['body'])
				else:
					verbose.append(pprint.pformat(results['body']))
			for idx in range(count):
				if str(idx) in response:
					verbose.append('Your service {} made the following callback to harness'.format(arguments['url']))
					verbose.append('')
					for key, value in response[str(idx)]['headers']:
						verbose.append('{}: {}'.format(key, value))
					verbose.append('')
			verbose.append('')
			verbose = os.linesep.join(verbose)
			if 'HARNESS_DEBUG' in os.environ:
				print(verbose)
			result = []
			for idx in range(count):
				self.assertTrue(str(idx) in response, 'your test service failed to make a callback to the test harness {}'.format(verbose))
				result.append(response[str(idx)])
			return result

	def get_traceparent(self, headers):
		retval = []
		for key, value in headers:
			if self.traceparent_name_re.match(key):
				retval.append((key, value))
		self.assertEqual(len(retval), 1, 'expect one traceparent header, got {} {!r}'.format('more' if retval else 'zero', retval))
		return Traceparent.from_string(retval[0][1])

	def get_tracestate(self, headers):
		tracestate = Tracestate()
		for key, value in headers:
			if self.tracestate_name_re.match(key):
				tracestate.from_string(value)
		return tracestate

	def make_single_request_and_get_tracecontext(self, headers):
		headers = self.make_request(headers)[0]['headers']
		return (self.get_traceparent(headers), self.get_tracestate(headers))

class TraceContextTest(TestBase):
	def test_both_traceparent_and_tracestate_missing(self):
		'''
		harness sends a request without traceparent or tracestate
		expects a valid traceparent from the output header
		'''
		traceparent, tracestate = self.make_single_request_and_get_tracecontext([])

	def test_traceparent_included_tracestate_missing(self):
		'''
		harness sends a request with traceparent but without tracestate
		expects a valid traceparent from the output header, with the same trace_id but different parent_id
		'''
		traceparent, tracestate = self.make_single_request_and_get_tracecontext([
			['traceparent', '00-12345678901234567890123456789012-1234567890123456-01'],
		])
		self.assertEqual(traceparent.trace_id.hex(), '12345678901234567890123456789012')
		self.assertNotEqual(traceparent.parent_id.hex(), '1234567890123456')

	def test_traceparent_duplicated(self):
		'''
		harness sends a request with two traceparent headers
		expects a valid traceparent from the output header, with a newly generated trace_id
		'''
		traceparent, tracestate = self.make_single_request_and_get_tracecontext([
			['traceparent', '00-12345678901234567890123456789011-1234567890123456-01'],
			['traceparent', '00-12345678901234567890123456789012-1234567890123456-01'],
		])
		self.assertNotEqual(traceparent.trace_id.hex(), '12345678901234567890123456789011')
		self.assertNotEqual(traceparent.trace_id.hex(), '12345678901234567890123456789012')

	def test_traceparent_header_name(self):
		'''
		harness sends an invalid traceparent using wrong names
		expects a valid traceparent from the output header, with a newly generated trace_id
		'''
		traceparent, tracestate = self.make_single_request_and_get_tracecontext([
			['trace-parent', '00-12345678901234567890123456789012-1234567890123456-01'],
		])
		self.assertNotEqual(traceparent.trace_id.hex(), '12345678901234567890123456789012')

		traceparent, tracestate = self.make_single_request_and_get_tracecontext([
			['trace.parent', '00-12345678901234567890123456789012-1234567890123456-01'],
		])
		self.assertNotEqual(traceparent.trace_id.hex(), '12345678901234567890123456789012')

	def test_traceparent_header_name_valid_casing(self):
		'''
		harness sends a valid traceparent using different combination of casing
		expects a valid traceparent from the output header
		'''
		traceparent, tracestate = self.make_single_request_and_get_tracecontext([
			['TraceParent', '00-12345678901234567890123456789012-1234567890123456-01'],
		])
		self.assertEqual(traceparent.trace_id.hex(), '12345678901234567890123456789012')

		traceparent, tracestate = self.make_single_request_and_get_tracecontext([
			['TrAcEpArEnT', '00-12345678901234567890123456789012-1234567890123456-01'],
		])
		self.assertEqual(traceparent.trace_id.hex(), '12345678901234567890123456789012')

		traceparent, tracestate = self.make_single_request_and_get_tracecontext([
			['TRACEPARENT', '00-12345678901234567890123456789012-1234567890123456-01'],
		])
		self.assertEqual(traceparent.trace_id.hex(), '12345678901234567890123456789012')

	def test_traceparent_version_0x00(self):
		'''
		harness sends an invalid traceparent with extra trailing characters
		expects a valid traceparent from the output header, with a newly generated trace_id
		'''
		traceparent, tracestate = self.make_single_request_and_get_tracecontext([
			['traceparent', '00-12345678901234567890123456789012-1234567890123456-01.'],
		])
		self.assertNotEqual(traceparent.trace_id.hex(), '12345678901234567890123456789012')

		traceparent, tracestate = self.make_single_request_and_get_tracecontext([
			['traceparent', '00-12345678901234567890123456789012-1234567890123456-01-what-the-future-will-be-like'],
		])
		self.assertNotEqual(traceparent.trace_id.hex(), '12345678901234567890123456789012')

	def test_traceparent_version_0xcc(self):
		'''
		harness sends an valid traceparent with future version 204 (0xcc)
		expects a valid traceparent from the output header with the same trace_id
		'''
		traceparent, tracestate = self.make_single_request_and_get_tracecontext([
			['traceparent', 'cc-12345678901234567890123456789012-1234567890123456-01'],
		])
		self.assertEqual(traceparent.trace_id.hex(), '12345678901234567890123456789012')

		traceparent, tracestate = self.make_single_request_and_get_tracecontext([
			['traceparent', 'cc-12345678901234567890123456789012-1234567890123456-01-what-the-future-will-be-like'],
		])
		self.assertEqual(traceparent.trace_id.hex(), '12345678901234567890123456789012')

		traceparent, tracestate = self.make_single_request_and_get_tracecontext([
			['traceparent', 'cc-12345678901234567890123456789012-1234567890123456-01.what-the-future-will-be-like'],
		])
		self.assertNotEqual(traceparent.trace_id.hex(), '12345678901234567890123456789012')

	def test_traceparent_version_0xff(self):
		'''
		harness sends an invalid traceparent with version 255 (0xff)
		expects a valid traceparent from the output header, with a newly generated trace_id
		'''
		traceparent, tracestate = self.make_single_request_and_get_tracecontext([
			['traceparent', 'ff-12345678901234567890123456789012-1234567890123456-01'],
		])
		self.assertNotEqual(traceparent.trace_id.hex(), '12345678901234567890123456789012')

	def test_traceparent_version_illegal_characters(self):
		'''
		harness sends an invalid traceparent with illegal characters in version
		expects a valid traceparent from the output header, with a newly generated trace_id
		'''
		traceparent, tracestate = self.make_single_request_and_get_tracecontext([
			['traceparent', '.0-12345678901234567890123456789012-1234567890123456-01'],
		])
		self.assertNotEqual(traceparent.trace_id.hex(), '12345678901234567890123456789012')

		traceparent, tracestate = self.make_single_request_and_get_tracecontext([
			['traceparent', '0.-12345678901234567890123456789012-1234567890123456-01'],
		])
		self.assertNotEqual(traceparent.trace_id.hex(), '12345678901234567890123456789012')

	def test_traceparent_version_too_long(self):
		'''
		harness sends an invalid traceparent with version more than 2 HEXDIG
		expects a valid traceparent from the output header, with a newly generated trace_id
		'''
		traceparent, tracestate = self.make_single_request_and_get_tracecontext([
			['traceparent', '000-12345678901234567890123456789012-1234567890123456-01'],
		])
		self.assertNotEqual(traceparent.trace_id.hex(), '12345678901234567890123456789012')

		traceparent, tracestate = self.make_single_request_and_get_tracecontext([
			['traceparent', '0000-12345678901234567890123456789012-1234567890123456-01'],
		])
		self.assertNotEqual(traceparent.trace_id.hex(), '12345678901234567890123456789012')

	def test_traceparent_version_too_short(self):
		'''
		harness sends an invalid traceparent with version less than 2 HEXDIG
		expects a valid traceparent from the output header, with a newly generated trace_id
		'''
		traceparent, tracestate = self.make_single_request_and_get_tracecontext([
			['traceparent', '0-12345678901234567890123456789012-1234567890123456-01'],
		])
		self.assertNotEqual(traceparent.trace_id.hex(), '12345678901234567890123456789012')

	def test_traceparent_trace_id_all_zero(self):
		'''
		harness sends an invalid traceparent with trace_id = 00000000000000000000000000000000
		expects a valid traceparent from the output header, with a newly generated trace_id
		'''
		traceparent, tracestate = self.make_single_request_and_get_tracecontext([
			['traceparent', '00-00000000000000000000000000000000-1234567890123456-01'],
		])
		self.assertNotEqual(traceparent.trace_id.hex(), '00000000000000000000000000000000')

	def test_traceparent_trace_id_illegal_characters(self):
		'''
		harness sends an invalid traceparent with illegal characters in trace_id
		expects a valid traceparent from the output header, with a newly generated trace_id
		'''
		traceparent, tracestate = self.make_single_request_and_get_tracecontext([
			['traceparent', '00-.2345678901234567890123456789012-1234567890123456-01'],
		])
		self.assertNotEqual(traceparent.trace_id.hex(), '.2345678901234567890123456789012')

		traceparent, tracestate = self.make_single_request_and_get_tracecontext([
			['traceparent', '00-1234567890123456789012345678901.-1234567890123456-01'],
		])
		self.assertNotEqual(traceparent.trace_id.hex(), '1234567890123456789012345678901.')

	def test_traceparent_trace_id_too_long(self):
		'''
		harness sends an invalid traceparent with trace_id more than 32 HEXDIG
		expects a valid traceparent from the output header, with a newly generated trace_id
		'''
		traceparent, tracestate = self.make_single_request_and_get_tracecontext([
			['traceparent', '00-123456789012345678901234567890123-1234567890123456-01'],
		])
		self.assertNotEqual(traceparent.trace_id.hex(), '123456789012345678901234567890123')
		self.assertNotEqual(traceparent.trace_id.hex(), '12345678901234567890123456789012')
		self.assertNotEqual(traceparent.trace_id.hex(), '23456789012345678901234567890123')

	def test_traceparent_trace_id_too_short(self):
		'''
		harness sends an invalid traceparent with trace_id less than 32 HEXDIG
		expects a valid traceparent from the output header, with a newly generated trace_id
		'''
		traceparent, tracestate = self.make_single_request_and_get_tracecontext([
			['traceparent', '00-1234567890123456789012345678901-1234567890123456-01'],
		])
		self.assertNotEqual(traceparent.trace_id.hex(), '1234567890123456789012345678901')

	def test_traceparent_parent_id_all_zero(self):
		'''
		harness sends an invalid traceparent with parent_id = 0000000000000000
		expects a valid traceparent from the output header, with a newly generated trace_id
		'''
		traceparent, tracestate = self.make_single_request_and_get_tracecontext([
			['traceparent', '00-12345678901234567890123456789012-0000000000000000-01'],
		])
		self.assertNotEqual(traceparent.trace_id.hex(), '12345678901234567890123456789012')

	def test_traceparent_parent_id_illegal_characters(self):
		'''
		harness sends an invalid traceparent with illegal characters in parent_id
		expects a valid traceparent from the output header, with a newly generated trace_id
		'''
		traceparent, tracestate = self.make_single_request_and_get_tracecontext([
			['traceparent', '00-12345678901234567890123456789012-.234567890123456-01'],
		])
		self.assertNotEqual(traceparent.trace_id.hex(), '12345678901234567890123456789012')

		traceparent, tracestate = self.make_single_request_and_get_tracecontext([
			['traceparent', '00-12345678901234567890123456789012-123456789012345.-01'],
		])
		self.assertNotEqual(traceparent.trace_id.hex(), '12345678901234567890123456789012')

	def test_traceparent_parent_id_too_long(self):
		'''
		harness sends an invalid traceparent with parent_id more than 16 HEXDIG
		expects a valid traceparent from the output header, with a newly generated trace_id
		'''
		traceparent, tracestate = self.make_single_request_and_get_tracecontext([
			['traceparent', '00-12345678901234567890123456789012-12345678901234567-01'],
		])
		self.assertNotEqual(traceparent.trace_id.hex(), '12345678901234567890123456789012')

	def test_traceparent_parent_id_too_short(self):
		'''
		harness sends an invalid traceparent with parent_id less than 16 HEXDIG
		expects a valid traceparent from the output header, with a newly generated trace_id
		'''
		traceparent, tracestate = self.make_single_request_and_get_tracecontext([
			['traceparent', '00-12345678901234567890123456789012-123456789012345-01'],
		])
		self.assertNotEqual(traceparent.trace_id.hex(), '12345678901234567890123456789012')

	def test_traceparent_trace_flags_illegal_characters(self):
		'''
		harness sends an invalid traceparent with illegal characters in trace_flags
		expects a valid traceparent from the output header, with a newly generated trace_id
		'''
		traceparent, tracestate = self.make_single_request_and_get_tracecontext([
			['traceparent', '00-12345678901234567890123456789012-1234567890123456-.0'],
		])
		self.assertNotEqual(traceparent.trace_id.hex(), '12345678901234567890123456789012')

		traceparent, tracestate = self.make_single_request_and_get_tracecontext([
			['traceparent', '00-12345678901234567890123456789012-1234567890123456-0.'],
		])
		self.assertNotEqual(traceparent.trace_id.hex(), '12345678901234567890123456789012')

	def test_traceparent_trace_flags_too_long(self):
		'''
		harness sends an invalid traceparent with trace_flags more than 2 HEXDIG
		expects a valid traceparent from the output header, with a newly generated trace_id
		'''
		traceparent, tracestate = self.make_single_request_and_get_tracecontext([
			['traceparent', '00-12345678901234567890123456789012-1234567890123456-001'],
		])
		self.assertNotEqual(traceparent.trace_id.hex(), '12345678901234567890123456789012')

	def test_traceparent_trace_flags_too_short(self):
		'''
		harness sends an invalid traceparent with trace_flags less than 2 HEXDIG
		expects a valid traceparent from the output header, with a newly generated trace_id
		'''
		traceparent, tracestate = self.make_single_request_and_get_tracecontext([
			['traceparent', '00-12345678901234567890123456789012-1234567890123456-1'],
		])
		self.assertNotEqual(traceparent.trace_id.hex(), '12345678901234567890123456789012')

	def test_traceparent_ows_handling(self):
		'''
		harness sends an valid traceparent with heading and trailing OWS
		expects a valid traceparent from the output header
		'''
		traceparent, tracestate = self.make_single_request_and_get_tracecontext([
			['traceparent', ' 00-12345678901234567890123456789012-1234567890123456-01'],
		])
		self.assertEqual(traceparent.trace_id.hex(), '12345678901234567890123456789012')

		traceparent, tracestate = self.make_single_request_and_get_tracecontext([
			['traceparent', '\t00-12345678901234567890123456789012-1234567890123456-01'],
		])
		self.assertEqual(traceparent.trace_id.hex(), '12345678901234567890123456789012')

		traceparent, tracestate = self.make_single_request_and_get_tracecontext([
			['traceparent', '00-12345678901234567890123456789012-1234567890123456-01 '],
		])
		self.assertEqual(traceparent.trace_id.hex(), '12345678901234567890123456789012')

		traceparent, tracestate = self.make_single_request_and_get_tracecontext([
			['traceparent', '00-12345678901234567890123456789012-1234567890123456-01\t'],
		])
		self.assertEqual(traceparent.trace_id.hex(), '12345678901234567890123456789012')

		traceparent, tracestate = self.make_single_request_and_get_tracecontext([
			['traceparent', '\t 00-12345678901234567890123456789012-1234567890123456-01 \t'],
		])
		self.assertEqual(traceparent.trace_id.hex(), '12345678901234567890123456789012')

	def test_tracestate_included_traceparent_missing(self):
		'''
		harness sends a request with tracestate but without traceparent
		expects a valid traceparent from the output header
		expects the tracestate to be discarded
		'''
		traceparent, tracestate1 = self.make_single_request_and_get_tracecontext([
			['tracestate', 'foo=1'],
		])
		traceparent, tracestate2 = self.make_single_request_and_get_tracecontext([
			['tracestate', 'foo=1,bar=2'],
		])
		self.assertEqual(len(tracestate1), len(tracestate2))

	def test_tracestate_included_traceparent_included(self):
		'''
		harness sends a request with both tracestate and traceparent
		expects a valid traceparent from the output header with the same trace_id
		expects the tracestate to be inherited
		'''
		traceparent, tracestate = self.make_single_request_and_get_tracecontext([
			['traceparent', '00-12345678901234567890123456789012-1234567890123456-00'],
			['tracestate', 'foo=1,bar=2'],
		])
		self.assertEqual(traceparent.trace_id.hex(), '12345678901234567890123456789012')
		self.assertEqual(tracestate['foo'], '1')
		self.assertEqual(tracestate['bar'], '2')

	def test_tracestate_header_name(self):
		'''
		harness sends an invalid tracestate using wrong names
		expects the tracestate to be discarded
		'''
		traceparent, tracestate = self.make_single_request_and_get_tracecontext([
			['traceparent', '00-12345678901234567890123456789012-1234567890123456-00'],
			['trace-state', 'foo=1'],
		])
		self.assertRaises(KeyError, lambda: tracestate['foo'])

		traceparent, tracestate = self.make_single_request_and_get_tracecontext([
			['traceparent', '00-12345678901234567890123456789012-1234567890123456-00'],
			['trace.state', 'foo=1'],
		])
		self.assertRaises(KeyError, lambda: tracestate['foo'])

	def test_tracestate_header_name_valid_casing(self):
		'''
		harness sends a valid tracestate using different combination of casing
		expects the tracestate to be inherited
		'''
		traceparent, tracestate = self.make_single_request_and_get_tracecontext([
			['traceparent', '00-12345678901234567890123456789012-1234567890123456-00'],
			['TraceState', 'foo=1'],
		])
		self.assertEqual(tracestate['foo'], '1')

		traceparent, tracestate = self.make_single_request_and_get_tracecontext([
			['traceparent', '00-12345678901234567890123456789012-1234567890123456-00'],
			['TrAcEsTaTe', 'foo=1'],
		])
		self.assertEqual(tracestate['foo'], '1')

		traceparent, tracestate = self.make_single_request_and_get_tracecontext([
			['traceparent', '00-12345678901234567890123456789012-1234567890123456-00'],
			['TRACESTATE', 'foo=1'],
		])
		self.assertEqual(tracestate['foo'], '1')

	def test_tracestate_empty_header(self):
		'''
		harness sends a request with empty tracestate header
		expects the tracestate to be discarded
		'''
		traceparent, tracestate = self.make_single_request_and_get_tracecontext([
			['traceparent', '00-12345678901234567890123456789012-1234567890123456-00'],
			['tracestate', ''],
		])
		self.assertEqual(traceparent.trace_id.hex(), '12345678901234567890123456789012')

		traceparent, tracestate = self.make_single_request_and_get_tracecontext([
			['traceparent', '00-12345678901234567890123456789012-1234567890123456-00'],
			['tracestate', 'foo=1'],
			['tracestate', ''],
		])
		self.assertEqual(traceparent.trace_id.hex(), '12345678901234567890123456789012')
		self.assertEqual(tracestate['foo'], '1')

		traceparent, tracestate = self.make_single_request_and_get_tracecontext([
			['traceparent', '00-12345678901234567890123456789012-1234567890123456-00'],
			['tracestate', ''],
			['tracestate', 'foo=1'],
		])
		self.assertEqual(traceparent.trace_id.hex(), '12345678901234567890123456789012')
		self.assertEqual(tracestate['foo'], '1')

	def test_tracestate_multiple_headers_different_keys(self):
		'''
		harness sends a request with multiple tracestate headers, each contains different set of keys
		expects a combined tracestate
		'''
		traceparent, tracestate = self.make_single_request_and_get_tracecontext([
			['traceparent', '00-12345678901234567890123456789012-1234567890123456-00'],
			['tracestate', 'foo=1,bar=2'],
			['tracestate', 'rojo=1,congo=2'],
			['tracestate', 'baz=3'],
		])
		self.assertEqual(traceparent.trace_id.hex(), '12345678901234567890123456789012')
		self.assertTrue(str(tracestate).index('foo=1') < str(tracestate).index('bar=2'))
		self.assertTrue(str(tracestate).index('bar=2') < str(tracestate).index('rojo=1'))
		self.assertTrue(str(tracestate).index('rojo=1') < str(tracestate).index('congo=2'))
		self.assertTrue(str(tracestate).index('congo=2') < str(tracestate).index('baz=3'))

	def test_tracestate_duplicated_keys(self):
		'''
		harness sends a request with an invalid tracestate header with duplicated keys
		expects the tracestate to be discarded
		'''
		traceparent, tracestate = self.make_single_request_and_get_tracecontext([
			['traceparent', '00-12345678901234567890123456789012-1234567890123456-00'],
			['tracestate', 'foo=1,foo=1'],
		])
		self.assertEqual(traceparent.trace_id.hex(), '12345678901234567890123456789012')
		self.assertRaises(KeyError, lambda: tracestate['foo'])

		traceparent, tracestate = self.make_single_request_and_get_tracecontext([
			['traceparent', '00-12345678901234567890123456789012-1234567890123456-00'],
			['tracestate', 'foo=1,foo=2'],
		])
		self.assertEqual(traceparent.trace_id.hex(), '12345678901234567890123456789012')
		self.assertRaises(KeyError, lambda: tracestate['foo'])

		traceparent, tracestate = self.make_single_request_and_get_tracecontext([
			['traceparent', '00-12345678901234567890123456789012-1234567890123456-00'],
			['tracestate', 'foo=1'],
			['tracestate', 'foo=1'],
		])
		self.assertEqual(traceparent.trace_id.hex(), '12345678901234567890123456789012')
		self.assertRaises(KeyError, lambda: tracestate['foo'])

		traceparent, tracestate = self.make_single_request_and_get_tracecontext([
			['traceparent', '00-12345678901234567890123456789012-1234567890123456-00'],
			['tracestate', 'foo=1'],
			['tracestate', 'foo=2'],
		])
		self.assertEqual(traceparent.trace_id.hex(), '12345678901234567890123456789012')
		self.assertRaises(KeyError, lambda: tracestate['foo'])

	def test_tracestate_all_allowed_characters(self):
		'''
		harness sends a request with a valid tracestate header with all legal characters
		expects the tracestate to be inherited
		'''
		key_without_vendor = ''.join([
			''.join(map(chr, range(0x61, 0x7A + 1))), # lcalpha
			'0123456789', # DIGIT
			'_',
			'-',
			'*',
			'/',
		])
		key_with_vendor = key_without_vendor + '@a-z0-9_-*/'
		value = ''.join([
			''.join(map(chr, range(0x20, 0x2B + 1))),
			''.join(map(chr, range(0x2D, 0x3C + 1))),
			''.join(map(chr, range(0x3E, 0x7E + 1))),
		])

		traceparent, tracestate = self.make_single_request_and_get_tracecontext([
			['traceparent', '00-12345678901234567890123456789012-1234567890123456-00'],
			['tracestate', key_without_vendor + '=' + value],
		])
		self.assertEqual(tracestate[key_without_vendor], value)

		traceparent, tracestate = self.make_single_request_and_get_tracecontext([
			['traceparent', '00-12345678901234567890123456789012-1234567890123456-00'],
			['tracestate', key_with_vendor + '=' + value],
		])
		self.assertEqual(tracestate[key_with_vendor], value)

	def test_tracestate_ows_handling(self):
		'''
		harness sends a request with a valid tracestate header with OWS
		expects the tracestate to be inherited
		'''
		traceparent, tracestate = self.make_single_request_and_get_tracecontext([
			['traceparent', '00-12345678901234567890123456789012-1234567890123456-00'],
			['tracestate', 'foo=1 \t , \t bar=2, \t baz=3'],
		])
		self.assertEqual(tracestate['foo'], '1')
		self.assertEqual(tracestate['bar'], '2')
		self.assertEqual(tracestate['baz'], '3')

		traceparent, tracestate = self.make_single_request_and_get_tracecontext([
			['traceparent', '00-12345678901234567890123456789012-1234567890123456-00'],
			['tracestate', 'foo=1\t \t,\t \tbar=2,\t \tbaz=3'],
		])
		self.assertEqual(tracestate['foo'], '1')
		self.assertEqual(tracestate['bar'], '2')
		self.assertEqual(tracestate['baz'], '3')

		traceparent, tracestate = self.make_single_request_and_get_tracecontext([
			['traceparent', '00-12345678901234567890123456789012-1234567890123456-00'],
			['tracestate', ' foo=1'],
		])
		self.assertEqual(traceparent.trace_id.hex(), '12345678901234567890123456789012')
		self.assertEqual(tracestate['foo'], '1')

		traceparent, tracestate = self.make_single_request_and_get_tracecontext([
			['traceparent', '00-12345678901234567890123456789012-1234567890123456-00'],
			['tracestate', '\tfoo=1'],
		])
		self.assertEqual(traceparent.trace_id.hex(), '12345678901234567890123456789012')
		self.assertEqual(tracestate['foo'], '1')

		traceparent, tracestate = self.make_single_request_and_get_tracecontext([
			['traceparent', '00-12345678901234567890123456789012-1234567890123456-00'],
			['tracestate', 'foo=1 '],
		])
		self.assertEqual(traceparent.trace_id.hex(), '12345678901234567890123456789012')
		self.assertEqual(tracestate['foo'], '1')

		traceparent, tracestate = self.make_single_request_and_get_tracecontext([
			['traceparent', '00-12345678901234567890123456789012-1234567890123456-00'],
			['tracestate', 'foo=1\t'],
		])
		self.assertEqual(traceparent.trace_id.hex(), '12345678901234567890123456789012')
		self.assertEqual(tracestate['foo'], '1')

		traceparent, tracestate = self.make_single_request_and_get_tracecontext([
			['traceparent', '00-12345678901234567890123456789012-1234567890123456-00'],
			['tracestate', '\t foo=1 \t'],
		])
		self.assertEqual(traceparent.trace_id.hex(), '12345678901234567890123456789012')
		self.assertEqual(tracestate['foo'], '1')

	def test_tracestate_key_illegal_characters(self):
		'''
		harness sends a request with an invalid tracestate header with illegal key
		expects the tracestate to be discarded
		'''
		traceparent, tracestate = self.make_single_request_and_get_tracecontext([
			['traceparent', '00-12345678901234567890123456789012-1234567890123456-00'],
			['tracestate', 'foo =1'],
		])
		self.assertRaises(KeyError, lambda: tracestate['foo '])

		traceparent, tracestate = self.make_single_request_and_get_tracecontext([
			['traceparent', '00-12345678901234567890123456789012-1234567890123456-00'],
			['tracestate', 'FOO=1'],
		])
		self.assertRaises(KeyError, lambda: tracestate['FOO'])

		traceparent, tracestate = self.make_single_request_and_get_tracecontext([
			['traceparent', '00-12345678901234567890123456789012-1234567890123456-00'],
			['tracestate', 'foo.bar=1'],
		])
		self.assertRaises(KeyError, lambda: tracestate['foo.bar'])

	def test_tracestate_key_illegal_vendor_format(self):
		'''
		harness sends a request with an invalid tracestate header with illegal vendor format
		expects the tracestate to be discarded
		'''
		traceparent, tracestate = self.make_single_request_and_get_tracecontext([
			['traceparent', '00-12345678901234567890123456789012-1234567890123456-00'],
			['tracestate', 'foo@=1,bar=2'],
		])
		self.assertRaises(KeyError, lambda: tracestate['bar'])

		traceparent, tracestate = self.make_single_request_and_get_tracecontext([
			['traceparent', '00-12345678901234567890123456789012-1234567890123456-00'],
			['tracestate', '@foo=1,bar=2'],
		])
		self.assertRaises(KeyError, lambda: tracestate['bar'])

		traceparent, tracestate = self.make_single_request_and_get_tracecontext([
			['traceparent', '00-12345678901234567890123456789012-1234567890123456-00'],
			['tracestate', 'foo@@bar=1,bar=2'],
		])
		self.assertRaises(KeyError, lambda: tracestate['bar'])

		traceparent, tracestate = self.make_single_request_and_get_tracecontext([
			['traceparent', '00-12345678901234567890123456789012-1234567890123456-00'],
			['tracestate', 'foo@bar@baz=1,bar=2'],
		])
		self.assertRaises(KeyError, lambda: tracestate['bar'])

	@unittest.skipIf(STRICT_LEVEL < 2, "strict")
	def test_tracestate_member_count_limit(self):
		'''
		harness sends a request with a valid tracestate header with 32 list members
		expects the tracestate to be inherited

		harness sends a request with an invalid tracestate header with 33 list members
		expects the tracestate to be discarded
		'''
		traceparent, tracestate = self.make_single_request_and_get_tracecontext([
			['traceparent', '00-12345678901234567890123456789012-1234567890123456-00'],
			['tracestate', 'bar01=01,bar02=02,bar03=03,bar04=04,bar05=05,bar06=06,bar07=07,bar08=08,bar09=09,bar10=10'],
			['tracestate', 'bar11=11,bar12=12,bar13=13,bar14=14,bar15=15,bar16=16,bar17=17,bar18=18,bar19=19,bar20=20'],
			['tracestate', 'bar21=21,bar22=22,bar23=23,bar24=24,bar25=25,bar26=26,bar27=27,bar28=28,bar29=29,bar30=30'],
			['tracestate', 'bar31=31,bar32=32'],
		])
		self.assertEqual(tracestate['bar01'], '01')
		self.assertEqual(len(tracestate), 32)

		traceparent, tracestate = self.make_single_request_and_get_tracecontext([
			['traceparent', '00-12345678901234567890123456789012-1234567890123456-00'],
			['tracestate', 'bar01=01,bar02=02,bar03=03,bar04=04,bar05=05,bar06=06,bar07=07,bar08=08,bar09=09,bar10=10'],
			['tracestate', 'bar11=11,bar12=12,bar13=13,bar14=14,bar15=15,bar16=16,bar17=17,bar18=18,bar19=19,bar20=20'],
			['tracestate', 'bar21=21,bar22=22,bar23=23,bar24=24,bar25=25,bar26=26,bar27=27,bar28=28,bar29=29,bar30=30'],
			['tracestate', 'bar31=31,bar32=32,bar33=33'],
		])
		self.assertRaises(KeyError, lambda: tracestate['bar01'])

	def test_tracestate_key_length_limit(self):
		'''
		harness sends tracestate header with a key of 256 and 257 characters
		harness sends tracestate header with a key of 14 and 15 characters in the vendor section
		harness sends tracestate header with a key of 241 and 242 characters in the tenant section
		'''
		traceparent, tracestate = self.make_single_request_and_get_tracecontext([
			['traceparent', '00-12345678901234567890123456789012-1234567890123456-00'],
			['tracestate', 'foo=1'],
			['tracestate', 'z' * 256 + '=1'],
		])
		self.assertEqual(tracestate['foo'], '1')

		traceparent, tracestate = self.make_single_request_and_get_tracecontext([
			['traceparent', '00-12345678901234567890123456789012-1234567890123456-00'],
			['tracestate', 'foo=1'],
			['tracestate', 'z' * 257 + '=1'],
		])
		self.assertRaises(KeyError, lambda: tracestate['foo'])

		traceparent, tracestate = self.make_single_request_and_get_tracecontext([
			['traceparent', '00-12345678901234567890123456789012-1234567890123456-00'],
			['tracestate', 'foo=1'],
			['tracestate', 't' * 241 + '@' + 'v' * 14 + '=1'],
		])
		self.assertEqual(tracestate['foo'], '1')

		traceparent, tracestate = self.make_single_request_and_get_tracecontext([
			['traceparent', '00-12345678901234567890123456789012-1234567890123456-00'],
			['tracestate', 'foo=1'],
			['tracestate', 't' * 242 + '@v=1'],
		])
		self.assertRaises(KeyError, lambda: tracestate['foo'])

		traceparent, tracestate = self.make_single_request_and_get_tracecontext([
			['traceparent', '00-12345678901234567890123456789012-1234567890123456-00'],
			['tracestate', 'foo=1'],
			['tracestate', 't@' + 'v' * 15 + '=1'],
		])
		self.assertRaises(KeyError, lambda: tracestate['foo'])

class AdvancedTest(TestBase):
	def test_multiple_requests_with_valid_traceparent(self):
		'''
		harness sends a valid traceparent and asks vendor service to callback multiple times
		expects the trace_id to be inherited by all the callbacks
		'''
		trace_ids = set()
		parent_ids = set()
		for response in self.make_request([
			['traceparent', '00-12345678901234567890123456789012-1234567890123456-01'],
		], 3):
			traceparent = self.get_traceparent(response['headers'])
			trace_ids.add(traceparent.trace_id.hex())
			parent_ids.add(traceparent.parent_id.hex())
		self.assertEqual(len(trace_ids), 1)
		self.assertTrue('12345678901234567890123456789012' in trace_ids)
		self.assertEqual(len(parent_ids), 3)

	def test_multiple_requests_without_traceparent(self):
		'''
		harness asks vendor service to callback multiple times
		expects a different parent_id each time
		'''
		trace_ids = set()
		parent_ids = set()
		for response in self.make_request([], 3):
			traceparent = self.get_traceparent(response['headers'])
			trace_ids.add(traceparent.trace_id.hex())
			parent_ids.add(traceparent.parent_id.hex())
		self.assertEqual(len(parent_ids), 3)

	def test_multiple_requests_with_illegal_traceparent(self):
		'''
		harness sends an invalid traceparent and asks vendor service to callback multiple times
		expects new trace_id(s) generated
		'''
		trace_ids = set()
		parent_ids = set()
		for response in self.make_request([
			['traceparent', '00-00000000000000000000000000000000-1234567890123456-01'],
		], 3):
			traceparent = self.get_traceparent(response['headers'])
			trace_ids.add(traceparent.trace_id.hex())
			parent_ids.add(traceparent.parent_id.hex())
		self.assertFalse('00000000000000000000000000000000' in trace_ids)
		self.assertEqual(len(parent_ids), 3)

if __name__ == '__main__':
	if len(sys.argv) >= 2:
		os.environ['SERVICE_ENDPOINT'] = sys.argv[1]
	if not 'SERVICE_ENDPOINT' in os.environ:
		print('''
Usage: python {0} <service endpoint> [patterns]

Environment Variables:
	HARNESS_DEBUG      when set, debug mode will be enabled (default to disabled)
	HARNESS_HOST       the public host/address of the test harness (default 127.0.0.1)
	HARNESS_PORT       the public port of the test harness (default 7777)
	HARNESS_TIMEOUT    the timeout (in seconds) used for each test case (default 5)
	HARNESS_BIND_HOST  the host/address which the test harness binds to (default to HARNESS_HOST)
	HARNESS_BIND_PORT  the port which the test harness binds to (default to HARNESS_PORT)
	SERVICE_ENDPOINT   your test service endpoint (no default value)
	STRICT_LEVEL       the level of test strictness (default 2)

Example:
	python {0} http://127.0.0.1:5000/test
	python {0} http://127.0.0.1:5000/test TraceContextTest.test_both_traceparent_and_tracestate_missing
	python {0} http://127.0.0.1:5000/test AdvancedTest
	python {0} http://127.0.0.1:5000/test AdvancedTest TraceContextTest.test_both_traceparent_and_tracestate_missing
		'''.strip().format(sys.argv[0]), file = sys.stderr)
		exit(-1)

	host = environ('HARNESS_HOST', '127.0.0.1')
	port = environ('HARNESS_PORT', '7777')
	timeout = environ('HARNESS_TIMEOUT', '5')
	bind_host = environ('HARNESS_BIND_HOST', host)
	bind_port = environ('HARNESS_BIND_PORT', port)
	client = TestClient(host = host, port = int(port), timeout = int(timeout) + 1)
	server = TestServer(host = bind_host, port = int(bind_port), timeout = int(timeout))

	suite = unittest.TestSuite()
	loader = unittest.TestLoader()
	if len(sys.argv) > 2:
		for name in sys.argv[2:]:
			suite.addTests(loader.loadTestsFromName(name, module = sys.modules[__name__]))
	else:
		suite.addTests(loader.loadTestsFromModule(sys.modules[__name__]))
	result = unittest.TextTestRunner(verbosity = 2).run(suite)
	sys.exit(len(result.errors) + len(result.failures))
