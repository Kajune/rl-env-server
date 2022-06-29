import asyncio, websockets
import argparse
from common import *

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--port', type=int, default=5000)
args = parser.parse_args()


env = None

async def init(ws):
	global env

	message = await ws.recv()
	env = decode(message)
	if env is not None:
		await ws.send('OK')
	else:
		await ws.send('NG')


async def observation_space(ws):
	if env is None:
		await ws.send('Must set env first via init.')
	else:
		await ws.send(encode(env.observation_space))


async def action_space(ws):
	if env is None:
		await ws.send('Must set env first via init.')
	else:
		await ws.send(encode(env.action_space))


async def reset(ws):
	if env is None:
		await ws.send('Must set env first via init.')
	else:
		await ws.send(encode(env.reset()))


async def step(ws):
	if env is None:
		await ws.send('Must set env first via init.')
	else:
		action = decode(await ws.recv())
		await ws.send(encode(env.step(action)))


async def render(ws):
	if env is None:
		await ws.send('Must set env first via init.')
	else:
		mode = await ws.recv()
		await ws.send(encode(env.render(mode)))


async def close(ws):
	if env is None:
		await ws.send('Must set env first via init.')
	else:
		env.close()


async def proc(ws, path):
	async for command in ws:
		if command == 'test':
			message = await ws.recv()
			await ws.send(message)
		elif command == 'init':
			await init(ws)
		elif command == 'observation_space':
			await observation_space(ws)
		elif command == 'action_space':
			await action_space(ws)
		elif command == 'reset':
			await reset(ws)
		elif command == 'step':
			await step(ws)
		elif command == 'render':
			await render(ws)
		elif command == 'close':
			await close(ws)
		else:
			await ws.send('Unkown command: ' + command)


async def main(host, port):
	async with websockets.serve(proc, host, port):
		await asyncio.Future()


if __name__ == '__main__':
	asyncio.run(main('0.0.0.0', args.port))

