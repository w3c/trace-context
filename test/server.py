from aiohttp import ClientSession, ClientTimeout, ContentTypeError, web
from multidict import MultiDict

class AsyncTestServer(object):
	scopes = {}

	def __init__(self, host, port, timeout = 5):
		self.host = host
		self.port = port
		self.timeout = ClientTimeout(total = timeout)
		self.app = web.Application()
		self.app.add_routes([
			web.post('/{scope}', self.scope_handler),
		])

	async def start(self):
		self.runner = web.AppRunner(self.app)
		await self.runner.setup()
		self.site = web.TCPSite(self.runner, self.host, self.port)
		await self.site.start()
		print('harness listening on http://%s:%s'%(self.host, self.port))

	async def stop(self):
		await self.runner.cleanup()

	async def scope_handler(self, request):
		scope_id = request.match_info['scope'].split('.', maxsplit = 1)
		callback_id = None if len(scope_id) == 1 else scope_id[1]
		scope_id = scope_id[0]
		arguments = await request.json()
		scope = None
		if callback_id:
			scope = self.scopes[scope_id]
			scope[callback_id] = {
				'headers': list(request.headers.items()),
				'arguments': arguments,
			}
		else:
			scope = {
				'headers': list(request.headers.items()),
				'arguments': arguments,
				'results': [],
			}
			self.scopes[scope_id] = scope
		if not arguments:
			return web.json_response(None)
		if not isinstance(arguments, list):
			arguments = [arguments]
		for action in arguments:
			headers = [['Accept', 'application/json']]
			if 'headers' in action:
				headers += action['headers']
			async with ClientSession(headers = headers, timeout = self.timeout) as session:
				arguments = []
				if 'arguments' in action:
					arguments = action['arguments'] or []
				result = {}
				result['url'] = action['url']
				scope['results'].append(result)
				try:
					async with session.post(action['url'], json = arguments) as response:
						result['status'] = response.status
						result['headers'] = list(response.headers.items())
						result['body'] = await response.json(content_type = 'application/json')
				except ContentTypeError as err:
						result['body'] = await response.text()
				except Exception as err:
					result['exception'] = type(err).__name__
					result['msg'] = str(err)
		if not callback_id:
			del self.scopes[scope_id]
		return web.json_response(scope)

class TestServer(object):
	def __init__(self, host, port, timeout = 5):
		import asyncio
		from threading import Thread
		self.loop = asyncio.get_event_loop()
		self.server = AsyncTestServer(host, port, timeout)
		self.thread = Thread(target = self.monitor)
		self.run = True

	def monitor(self):
		import asyncio
		while self.run:
			self.loop.run_until_complete(asyncio.sleep(0.2))

	def start(self):
		self.loop.run_until_complete(self.server.start())
		self.thread.start()

	def stop(self):
		self.run = False
		self.thread.join()
		self.loop.run_until_complete(self.server.stop())

	def __enter__(self):
		self.start()
		return self

	def __exit__(self, type, value, traceback):
		self.stop()

if __name__ == '__main__':
	import sys
	host = '127.0.0.1'
	port = 7777
	if len(sys.argv) >= 2:
		host = sys.argv[1]
	if len(sys.argv) >= 3:
		port = int(sys.argv[2])
	with TestServer(host = host, port = port) as server:
		input('Press Enter to quit...')
