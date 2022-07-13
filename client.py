import grpc
import rl_env_server_pb2
import rl_env_server_pb2_grpc
import gym, cv2, time
from common import *


class RLEnvClient(gym.Env):
	def __init__(self, uri):
		self.channel = grpc.insecure_channel(uri)
		self.stub = rl_env_server_pb2_grpc.RLEnvServerStub(self.channel)
		self.stub.on_connected(rl_env_server_pb2.ConnectionRequest(id=str(id(self))))


	def __del__(self):
		self.stub.on_disconnected(rl_env_server_pb2.ConnectionRequest(id=str(id(self))))
		self.channel.close()


	def echo(self, message):
		response = self.stub.echo(rl_env_server_pb2.EchoRequest(message=message))
		return response.message


	def init(self, env):
		response = self.stub.init(rl_env_server_pb2.InitRequest(env=encode(env)))
		return response.status


	def numConnection(self):
		response = self.stub.numConnection(rl_env_server_pb2.Void())
		return response.numConnection


	def func(self, funcName, **kwargs):
		response = self.stub.func(rl_env_server_pb2.FuncRequest(funcName=funcName, args=encode(kwargs)))
		ret = decode(response.ret)
		if ret is None:
			print(response.message)
		else:
			return ret


	def property(self, propertyName):
		response = self.stub.property(rl_env_server_pb2.PropertyRequest(propertyName=propertyName))
		ret = decode(response.ret)
		if ret is None:
			print(response.message)
		else:
			return ret


	def observation_space(self):
		return self.property("observation_space")


	def action_space(self):
		return self.property("action_space")


	def reset(self):
		return self.func("reset")


	def step(self, action):
		return self.func("step", action=action)


	def render(self, **kwargs):
		return self.func("render", **kwargs)


	def close(self):
		self.func("close")



if __name__ == '__main__':
	env = RLEnvClient("localhost:5000")

	start = time.time()
	for env_name in ['CartPole-v1', 'MountainCar-v0', 'Pendulum-v1']:
		print(env.init(gym.make(env_name)))

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

	print('Finished in %s seconds.' % (time.time() - start))
