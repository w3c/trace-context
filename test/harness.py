import os
import uuid
from aiohttp import ClientSession, web
from multidict import MultiDict

class Harness(object):
	scopes = {}
	dirname = os.path.dirname(os.path.realpath(__file__))

	def __init__(self, host = '0.0.0.0', port = 7777):
		self.host = host
		self.port = port
		self.app = web.Application()
		self.app.add_routes([
			web.get('/', self.index_html_handler),
			web.get('/{name}.js', self.test_js_handler),
			web.post('/callback/{id}', self.callback_handler),
			web.post('/test/{scope_id}', self.test_handler),
		])

	async def start(self):
		self.runner = web.AppRunner(self.app)
		await self.runner.setup()
		self.site = web.TCPSite(self.runner, self.host, self.port)
		await self.site.start()
		print('harness listening on http://%s:%s'%(self.host, self.port))

	async def stop(self):
		await self.runner.cleanup()

	async def index_html_handler(self, request):
		with open(os.path.join(self.dirname, 'index.html'), mode = 'rb') as file:
			return web.Response(body = file.read(), headers = {'Content-Type': 'text/html'})

	async def test_js_handler(self, request):
		with open(os.path.join(self.dirname, '{}.js'.format(request.match_info['name'])), mode = 'rb') as file:
			return web.Response(body = file.read(), headers = {'Content-Type': 'application/javascript; charset=utf-8'})

	async def callback_handler(self, request):
		scope_id, callback_id = request.match_info['id'].split('.')
		arguments = await request.json()
		scope = self.scopes[scope_id]
		scope[scope_id + '.' + callback_id] = {
			'headers': list(request.headers.items()),
			'arguments': arguments,
		}
		if not arguments:
			return web.json_response(None)
		for action in arguments:
			async with ClientSession() as session:
				arguments = []
				if 'arguments' in action:
					arguments = action['arguments'] or []
				async with session.post(action['url'], json = arguments) as response:
					pass
		return web.json_response(None)

	async def test_handler(self, request):
		scope_id = request.match_info['scope_id']
		arguments = await request.json()
		scope = {
			scope_id: {
				'arguments': arguments,
				'headers': list(request.headers.items()),
			}
		}
		self.scopes[scope_id] = scope
		for action in arguments:
			args = {'headers': [['Accept', 'application/json']]}
			if 'headers' in action:
				args['headers'] += action['headers']
			async with ClientSession(**args) as session:
				arguments = []
				if 'arguments' in action:
					arguments = action['arguments'] or []
				async with session.post(action['url'], json = arguments) as response:
					pass
		del self.scopes[scope_id]
		return web.json_response(scope)

if __name__ == '__main__':
	import asyncio
	import sys
	from contextlib import suppress
	host = '127.0.0.1'
	port = 7777
	if len(sys.argv) >= 2:
		host = sys.argv[1]
	if len(sys.argv) >= 3:
		port = int(sys.argv[2])
	harness = Harness(host = host, port = port)
	loop = asyncio.get_event_loop()
	loop.run_until_complete(harness.start())
	with suppress(KeyboardInterrupt):
		loop.run_forever()
	loop.run_until_complete(harness.stop())
