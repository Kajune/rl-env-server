import asyncio, websockets, json
import argparse
from common import *

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--port', type=int, default=5000)
args = parser.parse_args()


env = None
num_connection = 0


async def init(ws):
	global env

	message = await ws.recv()
	env = decode(message)
	if env is not None:
		await ws.send('OK')
	else:
		await ws.send('NG')


async def call_property(ws):
	if env is None:
		await ws.send('Must set env first via init.')
	else:
		name = await ws.recv()
		if hasattr(env, name):
			await ws.send(encode(getattr(env, name)))
		else:
			await ws.send('env does not have property: ', name)


async def call_func(ws):
	if env is None:
		await ws.send('Must set env first via init.')
	else:
		name, args = json.loads(await ws.recv())
		args = {k: decode(v) for k, v in args.items()}
		if hasattr(env, name):
			await ws.send(encode(getattr(env, name)(**args)))
		else:
			await ws.send('env does not have function: ', name)


async def proc(ws, path):
	global num_connection
	num_connection += 1

	try:
		async for command in ws:
			if command == 'test':
				message = await ws.recv()
				await ws.send(message)
			elif command == 'init':
				await init(ws)
			elif command == 'property':
				await call_property(ws)
			elif command == 'func':
				await call_func(ws)
			else:
				await ws.send('Unkown command: ' + command)
	except websockets.exceptions.ConnectionClosedError:
		if env is not None:
			env.close()

	num_connection -= 1


async def main(host, port):
	async with websockets.serve(proc, host, port):
		await asyncio.Future()


if __name__ == '__main__':
	asyncio.run(main('0.0.0.0', args.port))

