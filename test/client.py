#!/usr/bin/env python

import json
import uuid
from urllib.error import HTTPError
from urllib.request import HTTPHandler, OpenerDirector, Request

__all__ = ['TestClient']

class TestClient(object):
	def __init__(self, host, port, timeout = 5):
		self.host = host
		self.port = port
		self.timeout = timeout

	opener_director = OpenerDirector()
	opener_director.add_handler(HTTPHandler())

	def send_request(self, url, headers = {}, arguments = None):
		if not isinstance(arguments, bytes):
			arguments = bytes(json.dumps(arguments), 'ascii')
		request = Request(method = 'POST', url = url, headers = headers, data = arguments)
		with self.opener_director.open(request, timeout = self.timeout) as response:
			if response.status != 200:
				raise HTTPError(url, response.status, response.msg, response.headers, None)
			return json.loads(str(response.read(), 'ascii'))

	class Scope(object):
		def __init__(self, harness):
			self.harness = harness
			self.id = uuid.uuid4().hex

		def __enter__(self):
			return self

		def __exit__(self, type, value, traceback):
			pass

		def __repr__(self):
			return '{}({})'.format(type(self).__name__, repr(self.id))

		def send_request(self, arguments = None):
			return self.harness.send_request(
				url = 'http://{}:{}/{}'.format(self.harness.host, self.harness.port, self.id),
				headers = {'Accept': 'application/json', 'Content-Type': 'application/json'},
				arguments = arguments)

		def url(self, path = ''):
			return 'http://{}:{}/{}.{}'.format(self.harness.host, self.harness.port, self.id, path)

	def scope(self):
		return TestClient.Scope(self)

if __name__ == '__main__':
	client = TestClient(host = '127.0.0.1', port = 7777, timeout = 5)
	with client.scope() as scope:
		response = scope.send_request()
