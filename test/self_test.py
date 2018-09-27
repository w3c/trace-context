import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from tracecontext import BaseTraceparent, Traceparent, Tracestate
from urllib.request import HTTPHandler, OpenerDirector, Request

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
			self.send_response(200)
			arguments = json.loads(str(self.rfile.read(int(self.headers['Content-Length'])), 'ascii'))

			traceparent = None
			tracestate = Tracestate()

			try:
				temp_traceparent = BaseTraceparent.from_string(self.get_header('traceparent'))
				if temp_traceparent.version == 0:
					if temp_traceparent._residue:
						raise ValueError('illegal traceparent format')
				traceparent = Traceparent(0, temp_traceparent.trace_id, temp_traceparent.span_id, temp_traceparent.trace_flags)
			except ValueError:
				pass

			if traceparent is None:
				traceparent = Traceparent()
			else:
				try:
					header = self.get_header('tracestate', commaSeparated = True)
					if header is not None:
						tracestate = Tracestate(header)
				except ValueError:
					# if tracestate is malformed, reuse the traceparent instead of restart the trace
					# traceparent = Traceparent()
					pass

			for item in arguments:
				headers = {}
				headers['traceparent'] = str(Traceparent(0, traceparent.trace_id, None, traceparent.trace_flags))
				if tracestate.is_valid():
					headers['tracestate'] = str(tracestate)
				request = Request(method = 'POST', url = item['url'], headers = headers, data = bytes(json.dumps(item['arguments']), 'ascii'))
				with self.opener_director.open(request, timeout = self.timeout) as response:
					pass
			self.end_headers()

		def get_header(self, name, commaSeparated = False):
			name = name.lower()
			headers = filter(lambda kv: kv[0].lower() == name, self.headers.items())
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
		sys.exit(subprocess.call(['python', '-m', 'unittest', '-v'] + sys.argv[1:]))
