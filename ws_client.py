import websocket
import gym, cv2
from common import *


class WebSocketEnv(gym.Env):
	def __init__(self, uri):
		self.ws = websocket.WebSocket()
		self.ws.connect(uri)


	def test(self, message):
		self.ws.send("test")
		self.ws.send(message)
		print(self.ws.recv())


	def init(self, env):
		self.ws.send("init")
		self.ws.send(encode(env))
		print(self.ws.recv())


	def observation_space(self):
		self.ws.send("observation_space")
		return decode(self.ws.recv())


	def action_space(self):
		self.ws.send("action_space")
		return decode(self.ws.recv())


	def reset(self):
		self.ws.send("reset")
		return decode(self.ws.recv())


	def step(self, action):
		self.ws.send("step")
		self.ws.send(encode(action))
		return decode(self.ws.recv())


	def render(self, mode = 'rgb_array'):
		self.ws.send("render")
		self.ws.send(mode)
		return decode(self.ws.recv())


	def close(self):
		self.ws.send("close")
		self.ws.close()


if __name__ == '__main__':
	env = WebSocketEnv("ws://localhost:5000")

	for env_name in ['CartPole-v1', 'MountainCar-v0', 'Pendulum-v1']:
		env.init(gym.make(env_name))

		obs_space = env.observation_space()
		act_space = env.action_space()
		print(obs_space, act_space)

		obs = env.reset()
		while True:
			action = act_space.sample()
			obs, reward, done, info = env.step(action)
			print(obs, reward, done, info)
			img = env.render()

			cv2.imshow('', img[...,::-1])
			cv2.waitKey(1)
			if done:
				break

	env.close()

