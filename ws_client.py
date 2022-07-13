import websocket, json
import gym, cv2, time
from common import *


class WebSocketEnv(gym.Env):
	def __init__(self, uri):
		self.ws = websocket.WebSocket(skip_utf8_validation=True)
		self.ws.connect(uri)


	def __del__(self):
		self.disconnect()


	def test(self, message):
		self.ws.send("test")
		self.ws.send(message)
		print(self.ws.recv())


	def init(self, env):
		self.ws.send("init")
		self.ws.send(encode(env))
		print(self.ws.recv())


	def call_func(self, func_name, **kwargs):
		self.ws.send("func")
		self.ws.send(json.dumps([func_name, {k: encode(v) for k, v in kwargs.items()}]))
		return decode(self.ws.recv())


	def call_property(self, property_name):
		self.ws.send("property")
		self.ws.send(property_name)
		return decode(self.ws.recv())


	def observation_space(self):
		return self.call_property("observation_space")


	def action_space(self):
		return self.call_property("action_space")


	def reset(self):
		return self.call_func("reset")


	def step(self, action):
		return self.call_func("step", action=action)


	def render(self, **kwargs):
		return self.call_func("render", **kwargs)


	def close(self):
		self.call_func("close")


	def disconnect(self):
		self.ws.close()



if __name__ == '__main__':
	env = WebSocketEnv("ws://localhost:5000")

	start = time.time()
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
			img = env.render(mode='rgb_array')

			cv2.imshow('', img[...,::-1])
			cv2.waitKey(1)
			if done:
				break

		env.close()

	env.disconnect()

	print('Finished in %f seconds.' % (time.time() - start))

