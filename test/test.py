#!/usr/bin/env python

import os
import sys
import unittest
from client import TestClient
from server import TestServer

client = None
server = None

def environ(name, default = None):
	if not name in os.environ:
		if default:
			os.environ[name] = default
		else:
			raise EnvironmentError('environment variable {} is not defined'.format(name))
	return os.environ[name]

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

	def get_traceparent(self, headers):
		retval = []
		for key, value in headers:
			if self.traceparent_name_re.match(key):
				retval.append((key, value))
		self.assertEqual(len(retval), 1, 'expect one traceparent header, got {} {!r}'.format('more' if retval else 'zero', retval))
		return retval[0]

	def get_traceparent_components(self, headers):
		traceparent = self.get_traceparent(headers)[1]
		match = self.traceparent_format_re.match(traceparent)
		self.assertTrue(match, 'failed to parse traceparent header, unknown format {!r}'.format(traceparent))
		return match.groups()

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

	def make_single_request_and_get_traceparent_components(self, headers):
		return self.get_traceparent_components(self.make_request(headers)[0]['headers'])

class TraceContextTest(TestBase):
	def test_both_traceparent_and_tracestate_missing(self):
		'''
		harness sends a request without traceparent or tracestate
		expects a valid traceparent from the output header
		'''
		version, trace_id, span_id, trace_flags = self.make_single_request_and_get_traceparent_components([])

	def test_traceparent_included_tracestate_missing(self):
		'''
		harness sends a request with traceparent but without tracestate
		expects a valid traceparent from the output header, with the same trace_id but different span_id
		'''
		version, trace_id, span_id, trace_flags = self.make_single_request_and_get_traceparent_components([
			['traceparent', '00-12345678901234567890123456789012-1234567890123456-01'],
		])
		self.assertEqual(trace_id, '12345678901234567890123456789012')
		self.assertNotEqual(span_id, '1234567890123456')

	def test_traceparent_duplicated(self):
		'''
		harness sends a request with two traceparent headers
		expects a valid traceparent from the output header, with a newly generated trace_id
		'''
		version, trace_id, span_id, trace_flags = self.make_single_request_and_get_traceparent_components([
			['traceparent', '00-12345678901234567890123456789011-1234567890123456-01'],
			['traceparent', '00-12345678901234567890123456789012-1234567890123456-01'],
		])
		self.assertNotEqual(trace_id, '12345678901234567890123456789011')
		self.assertNotEqual(trace_id, '12345678901234567890123456789012')

	def test_traceparent_header_name(self):
		'''
		harness sends an invalid traceparent using wrong names
		expects a valid traceparent from the output header, with a newly generated trace_id
		'''
		version, trace_id, span_id, trace_flags = self.make_single_request_and_get_traceparent_components([
			['trace-parent', '00-12345678901234567890123456789012-1234567890123456-01'],
		])
		self.assertNotEqual(trace_id, '12345678901234567890123456789012')

		version, trace_id, span_id, trace_flags = self.make_single_request_and_get_traceparent_components([
			['trace.parent', '00-12345678901234567890123456789012-1234567890123456-01'],
		])
		self.assertNotEqual(trace_id, '12345678901234567890123456789012')

	def test_traceparent_header_name_valid_casing(self):
		'''
		harness sends a valid traceparent using different combination of casing
		expects a valid traceparent from the output header
		'''
		version, trace_id, span_id, trace_flags = self.make_single_request_and_get_traceparent_components([
			['TraceParent', '00-12345678901234567890123456789012-1234567890123456-01'],
		])
		self.assertEqual(trace_id, '12345678901234567890123456789012')

		version, trace_id, span_id, trace_flags = self.make_single_request_and_get_traceparent_components([
			['TrAcEpArEnT', '00-12345678901234567890123456789012-1234567890123456-01'],
		])
		self.assertEqual(trace_id, '12345678901234567890123456789012')

		version, trace_id, span_id, trace_flags = self.make_single_request_and_get_traceparent_components([
			['TRACEPARENT', '00-12345678901234567890123456789012-1234567890123456-01'],
		])
		self.assertEqual(trace_id, '12345678901234567890123456789012')

	def test_traceparent_version_0x00(self):
		'''
		harness sends an invalid traceparent with extra trailing characters
		expects a valid traceparent from the output header, with a newly generated trace_id
		'''
		version, trace_id, span_id, trace_flags = self.make_single_request_and_get_traceparent_components([
			['traceparent', '00-12345678901234567890123456789012-1234567890123456-01.'],
		])
		self.assertNotEqual(trace_id, '12345678901234567890123456789012')

		version, trace_id, span_id, trace_flags = self.make_single_request_and_get_traceparent_components([
			['traceparent', '00-12345678901234567890123456789012-1234567890123456-01 '],
		])
		self.assertNotEqual(trace_id, '12345678901234567890123456789012')

		version, trace_id, span_id, trace_flags = self.make_single_request_and_get_traceparent_components([
			['traceparent', '00-12345678901234567890123456789012-1234567890123456-01-what-the-future-will-be-like'],
		])
		self.assertNotEqual(trace_id, '12345678901234567890123456789012')

	def test_traceparent_version_0xcc(self):
		'''
		harness sends an valid traceparent with future version 204 (0xcc)
		expects a valid traceparent from the output header with the same trace_id
		'''
		version, trace_id, span_id, trace_flags = self.make_single_request_and_get_traceparent_components([
			['traceparent', 'cc-12345678901234567890123456789012-1234567890123456-01'],
		])
		self.assertEqual(trace_id, '12345678901234567890123456789012')

		version, trace_id, span_id, trace_flags = self.make_single_request_and_get_traceparent_components([
			['traceparent', 'cc-12345678901234567890123456789012-1234567890123456-01-what-the-future-will-be-like'],
		])
		self.assertEqual(trace_id, '12345678901234567890123456789012')

		version, trace_id, span_id, trace_flags = self.make_single_request_and_get_traceparent_components([
			['traceparent', 'cc-12345678901234567890123456789012-1234567890123456-01.what-the-future-will-be-like'],
		])
		self.assertNotEqual(trace_id, '12345678901234567890123456789012')

	def test_traceparent_version_0xff(self):
		'''
		harness sends an invalid traceparent with version 255 (0xff)
		expects a valid traceparent from the output header, with a newly generated trace_id
		'''
		version, trace_id, span_id, trace_flags = self.make_single_request_and_get_traceparent_components([
			['traceparent', 'ff-12345678901234567890123456789012-1234567890123456-01'],
		])
		self.assertNotEqual(trace_id, '12345678901234567890123456789012')

	def test_traceparent_version_illegal_characters(self):
		'''
		harness sends an invalid traceparent with illegal characters in version
		expects a valid traceparent from the output header, with a newly generated trace_id
		'''
		version, trace_id, span_id, trace_flags = self.make_single_request_and_get_traceparent_components([
			['traceparent', '.0-12345678901234567890123456789012-1234567890123456-01'],
		])
		self.assertNotEqual(trace_id, '12345678901234567890123456789012')

		version, trace_id, span_id, trace_flags = self.make_single_request_and_get_traceparent_components([
			['traceparent', '0.-12345678901234567890123456789012-1234567890123456-01'],
		])
		self.assertNotEqual(trace_id, '12345678901234567890123456789012')

	def test_traceparent_version_too_long(self):
		'''
		harness sends an invalid traceparent with version more than 2 HEXDIG
		expects a valid traceparent from the output header, with a newly generated trace_id
		'''
		version, trace_id, span_id, trace_flags = self.make_single_request_and_get_traceparent_components([
			['traceparent', '000-12345678901234567890123456789012-1234567890123456-01'],
		])
		self.assertNotEqual(trace_id, '12345678901234567890123456789012')

	def test_traceparent_version_too_short(self):
		'''
		harness sends an invalid traceparent with version less than 2 HEXDIG
		expects a valid traceparent from the output header, with a newly generated trace_id
		'''
		version, trace_id, span_id, trace_flags = self.make_single_request_and_get_traceparent_components([
			['traceparent', '0-12345678901234567890123456789012-1234567890123456-01'],
		])
		self.assertNotEqual(trace_id, '12345678901234567890123456789012')

	def test_traceparent_trace_id_all_zero(self):
		'''
		harness sends an invalid traceparent with trace_id = 00000000000000000000000000000000
		expects a valid traceparent from the output header, with a newly generated trace_id
		'''
		version, trace_id, span_id, trace_flags = self.make_single_request_and_get_traceparent_components([
			['traceparent', '00-00000000000000000000000000000000-1234567890123456-01'],
		])
		self.assertNotEqual(trace_id, '00000000000000000000000000000000')

	def test_traceparent_trace_id_illegal_characters(self):
		'''
		harness sends an invalid traceparent with illegal characters in trace_id
		expects a valid traceparent from the output header, with a newly generated trace_id
		'''
		version, trace_id, span_id, trace_flags = self.make_single_request_and_get_traceparent_components([
			['traceparent', '00-.2345678901234567890123456789012-1234567890123456-01'],
		])
		self.assertNotEqual(trace_id, '.2345678901234567890123456789012')

		version, trace_id, span_id, trace_flags = self.make_single_request_and_get_traceparent_components([
			['traceparent', '00-1234567890123456789012345678901.-1234567890123456-01'],
		])
		self.assertNotEqual(trace_id, '1234567890123456789012345678901.')

	def test_traceparent_trace_id_too_long(self):
		'''
		harness sends an invalid traceparent with trace_id more than 32 HEXDIG
		expects a valid traceparent from the output header, with a newly generated trace_id
		'''
		version, trace_id, span_id, trace_flags = self.make_single_request_and_get_traceparent_components([
			['traceparent', '00-123456789012345678901234567890123-1234567890123456-01'],
		])
		self.assertNotEqual(trace_id, '123456789012345678901234567890123')
		self.assertNotEqual(trace_id, '12345678901234567890123456789012')
		self.assertNotEqual(trace_id, '23456789012345678901234567890123')

	def test_traceparent_trace_id_too_short(self):
		'''
		harness sends an invalid traceparent with trace_id less than 32 HEXDIG
		expects a valid traceparent from the output header, with a newly generated trace_id
		'''
		version, trace_id, span_id, trace_flags = self.make_single_request_and_get_traceparent_components([
			['traceparent', '00-1234567890123456789012345678901-1234567890123456-01'],
		])
		self.assertNotEqual(trace_id, '1234567890123456789012345678901')

	def test_traceparent_span_id_all_zero(self):
		'''
		harness sends an invalid traceparent with span_id = 0000000000000000
		expects a valid traceparent from the output header, with a newly generated trace_id
		'''
		version, trace_id, span_id, trace_flags = self.make_single_request_and_get_traceparent_components([
			['traceparent', '00-12345678901234567890123456789012-0000000000000000-01'],
		])
		self.assertNotEqual(trace_id, '12345678901234567890123456789012')

	def test_traceparent_span_id_illegal_characters(self):
		'''
		harness sends an invalid traceparent with illegal characters in span_id
		expects a valid traceparent from the output header, with a newly generated trace_id
		'''
		version, trace_id, span_id, trace_flags = self.make_single_request_and_get_traceparent_components([
			['traceparent', '00-12345678901234567890123456789012-.234567890123456-01'],
		])
		self.assertNotEqual(trace_id, '12345678901234567890123456789012')

		version, trace_id, span_id, trace_flags = self.make_single_request_and_get_traceparent_components([
			['traceparent', '00-12345678901234567890123456789012-123456789012345.-01'],
		])
		self.assertNotEqual(trace_id, '12345678901234567890123456789012')

	def test_traceparent_span_id_too_long(self):
		'''
		harness sends an invalid traceparent with span_id more than 16 HEXDIG
		expects a valid traceparent from the output header, with a newly generated trace_id
		'''
		version, trace_id, span_id, trace_flags = self.make_single_request_and_get_traceparent_components([
			['traceparent', '00-12345678901234567890123456789012-12345678901234567-01'],
		])
		self.assertNotEqual(trace_id, '12345678901234567890123456789012')

	def test_traceparent_span_id_too_short(self):
		'''
		harness sends an invalid traceparent with span_id less than 16 HEXDIG
		expects a valid traceparent from the output header, with a newly generated trace_id
		'''
		version, trace_id, span_id, trace_flags = self.make_single_request_and_get_traceparent_components([
			['traceparent', '00-12345678901234567890123456789012-123456789012345-01'],
		])
		self.assertNotEqual(trace_id, '12345678901234567890123456789012')

	def test_traceparent_trace_flags_illegal_characters(self):
		'''
		harness sends an invalid traceparent with illegal characters in trace_flags
		expects a valid traceparent from the output header, with a newly generated trace_id
		'''
		version, trace_id, span_id, trace_flags = self.make_single_request_and_get_traceparent_components([
			['traceparent', '00-12345678901234567890123456789012-1234567890123456-.0'],
		])
		self.assertNotEqual(trace_id, '12345678901234567890123456789012')

		version, trace_id, span_id, trace_flags = self.make_single_request_and_get_traceparent_components([
			['traceparent', '00-12345678901234567890123456789012-1234567890123456-0.'],
		])
		self.assertNotEqual(trace_id, '12345678901234567890123456789012')

	def test_traceparent_trace_flags_too_long(self):
		'''
		harness sends an invalid traceparent with trace_flags more than 2 HEXDIG
		expects a valid traceparent from the output header, with a newly generated trace_id
		'''
		version, trace_id, span_id, trace_flags = self.make_single_request_and_get_traceparent_components([
			['traceparent', '00-12345678901234567890123456789012-1234567890123456-001'],
		])
		self.assertNotEqual(trace_id, '12345678901234567890123456789012')

	def test_traceparent_trace_flags_too_short(self):
		'''
		harness sends an invalid traceparent with trace_flags less than 2 HEXDIG
		expects a valid traceparent from the output header, with a newly generated trace_id
		'''
		version, trace_id, span_id, trace_flags = self.make_single_request_and_get_traceparent_components([
			['traceparent', '00-12345678901234567890123456789012-1234567890123456-1'],
		])
		self.assertNotEqual(trace_id, '12345678901234567890123456789012')

class AdvancedTest(TestBase):
	def test_multiple_requests(self):
		'''
		harness asks vendor service to callback multiple times
		expects a different span_id each time
		'''
		span_ids = set()
		for response in self.make_request([
			['traceparent', '00-12345678901234567890123456789012-1234567890123456-01'],
		], 3):
			version, trace_id, span_id, trace_flags = self.get_traceparent_components(response['headers'])
			self.assertEqual(trace_id, '12345678901234567890123456789012')
			span_ids.add(span_id)
		self.assertEqual(len(span_ids), 3)


if __name__ == '__main__':
	if len(sys.argv) >= 2:
		os.environ['SERVICE_ENDPOINT'] = sys.argv[1]
	if not 'SERVICE_ENDPOINT' in os.environ:
		print('''
Usage: {0} <service endpoint>

Environment Variables:
	HARNESS_HOST       the public host/address of the test harness (default 127.0.0.1)
	HARNESS_PORT       the public port of the test harness (default 7777)
	HARNESS_TIMEOUT    the timeout (in seconds) used for each test case (default 5)
	HARNESS_BIND_HOST  the host/address which the test harness binds to (default to HARNESS_HOST)
	HARNESS_BIND_PORT  the port which the test harness binds to (default to HARNESS_PORT)
	SERVICE_ENDPOINT   your test service endpoint (no default value)

Example: {0} http://127.0.0.1:5000/test
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
	unittest.TextTestRunner(verbosity = 2).run(suite)
