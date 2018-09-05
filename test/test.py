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
		self.assertEqual(len(retval), 1, 'expect one traceparent header, got more {!r}'.format(retval))
		return retval[0]

	def get_traceparent_components(self, headers):
		traceparent = self.get_traceparent(headers)[1]
		match = self.traceparent_format_re.match(traceparent)
		self.assertTrue(match, 'failed to parse traceparent header, unknown format {!r}'.format(traceparent))
		return match.groups()

	def make_single_request(self, headers):
		with client.scope() as scope:
			response = scope.send_request(arguments = {
				'url': environ('SERVICE_ENDPOINT'),
				'headers': headers,
				'arguments': [
					{'url': scope.url('0'), 'arguments': []},
				],
			})
			return response['0']

	def make_single_request_and_get_traceparent_components(self, headers):
		return self.get_traceparent_components(self.make_single_request(headers)['headers'])

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

	def test_traceparent_trace_flags_illegal_characters(self):
		'''
		harness sends an invalid traceparent with illegal characters in trace_flags
		expects a valid traceparent from the output header, with a newly generated trace_id
		'''
		version, trace_id, span_id, trace_flags = self.make_single_request_and_get_traceparent_components([
			['traceparent', '00-12345678901234567890123456789012-1234567890123456-xy'],
		])
		self.assertNotEqual(trace_id, '12345678901234567890123456789012')

class AdvancedTest(TestBase):
	def test_multiple_requests(self):
		'''
		harness asks vendor service to callback multiple times
		expects a different span_id each time
		'''
		with client.scope() as scope:
			response = scope.send_request(arguments = {
				'url': environ('SERVICE_ENDPOINT'),
				'headers': [
					['traceparent', '00-12345678901234567890123456789012-1234567890123456-01'],
				],
				'arguments': [
					{'url': scope.url('1'), 'arguments': []},
					{'url': scope.url('2'), 'arguments': []},
					{'url': scope.url('3'), 'arguments': []},
				],
			})
			span_ids = set()
			span_ids.add(self.get_traceparent_components(response['1']['headers'])[2])
			span_ids.add(self.get_traceparent_components(response['2']['headers'])[2])
			span_ids.add(self.get_traceparent_components(response['3']['headers'])[2])
			self.assertEqual(len(span_ids), 3)


if __name__ == '__main__':
	if len(sys.argv) == 2:
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
	client = TestClient(host = host, port = int(port), timeout = int(timeout))
	server = TestServer(host = bind_host, port = int(bind_port), timeout = int(timeout))

	suite = unittest.TestSuite()
	loader = unittest.TestLoader()
	suite.addTests(loader.loadTestsFromTestCase(AdvancedTest))
	suite.addTests(loader.loadTestsFromTestCase(TraceContextTest))
	unittest.TextTestRunner().run(suite)
