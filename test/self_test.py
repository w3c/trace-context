import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from tracecontext import BaseTraceparent, Traceparent, Tracestate
from urllib.request import HTTPHandler, OpenerDirector, Request

test_data = []

class DemoServer(HTTPServer):
	def __init__(self, host = '127.0.0.1', port = None, timeout = 5):
		self.host = host
		self.port = port
		self.timeout = timeout
		self.worker_thread = Thread(target = self.loop)
		if not port:
			self.port = 5000
		while self.port < 65535:
			try:
				super().__init__((self.host, self.port), DemoServer.RequestHandler)
				break
			except OSError as err:
				if port:
					raise
				self.port += 1

	def __enter__(self):
		self.start()
		return self

	def __exit__(self, type, value, traceback):
		self.stop()

	def loop(self):
		self.serve_forever()

	def start(self):
		self.worker_thread.start()

	def stop(self):
		self.shutdown()
		self.worker_thread.join()

	class RequestHandler(BaseHTTPRequestHandler):
		opener_director = OpenerDirector()
		opener_director.add_handler(HTTPHandler())
		server_version = 'DemoServer/0.1'

		def do_POST(self):
			global test_data

			self.send_response(200)
			arguments = json.loads(str(self.rfile.read(int(self.headers['Content-Length'])), 'ascii'))

			traceparent = None
			tracestate = Tracestate()

			test_data.append({
				'headers': self.get_headers('traceparent') + self.get_headers('tracestate'),
			})

			try:
				temp_traceparent = BaseTraceparent.from_string(self.get_header('traceparent'))
				if temp_traceparent.version == 0:
					if temp_traceparent._residue:
						raise ValueError('illegal traceparent format')
				traceparent = Traceparent(0, temp_traceparent.trace_id, temp_traceparent.parent_id, temp_traceparent.trace_flags)
				test_data[-1]['is_traceparent_valid'] = True
			except ValueError:
				test_data[-1]['is_traceparent_valid'] = False

			try:
				header = self.get_header('tracestate', commaSeparated = True)
				if header:
					tracestate = Tracestate(header)
					if test_data[-1]['is_traceparent_valid']:
						test_data[-1]['is_tracestate_valid'] = True
			except ValueError:
				# if tracestate is malformed, reuse the traceparent instead of restart the trace
				# traceparent = Traceparent()
				test_data[-1]['is_tracestate_valid'] = False

			if traceparent is None:
				# if traceparent is malformed, discard tracestate
				traceparent = Traceparent()
				tracestate = Tracestate()

			for item in arguments:
				headers = {}
				headers['traceparent'] = str(Traceparent(0, traceparent.trace_id, None, traceparent.trace_flags))
				if tracestate.is_valid():
					headers['tracestate'] = str(tracestate)
				request = Request(method = 'POST', url = item['url'], headers = headers, data = bytes(json.dumps(item['arguments']), 'ascii'))
				with self.opener_director.open(request, timeout = self.timeout) as response:
					pass
			self.end_headers()

		def get_headers(self, name):
			name = name.lower()
			headers = filter(lambda kv: kv[0].lower() == name, self.headers.items())
			return tuple(headers)

		def get_header(self, name, commaSeparated = False):
			headers = self.get_headers(name)
			# https://tools.ietf.org/html/rfc7230#section-3.2
			# remove the leading whitespace and trailing whitespace
			headers = map(lambda kv: kv[1].strip(' \t'), headers)
			headers = tuple(headers)

			if not headers:
				return None
			if commaSeparated:
				return ','.join(headers)
			if len(headers) == 1:
				return headers[0]
			raise ValueError('multiple header {} not allowed'.format(name))

		def log_message(self, format, *args):
			pass

if __name__ == '__main__':
	import os
	import subprocess
	import sys
	with DemoServer() as server:
		os.environ['SERVICE_ENDPOINT'] = 'http://{}:{}/'.format(server.host, server.port)
		errno = subprocess.call(['python', '-m', 'unittest', '-v'] + sys.argv[1:])
		ofile = open("test_data.json", "w")
		ofile.write('[\n' + ',\n'.join(map(lambda x: '\t' + json.dumps(x), test_data)) + '\n' + ']' + '\n')
		ofile.close()
		sys.exit(errno)
