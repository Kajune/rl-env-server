from concurrent import futures
import grpc
import rl_env_server_pb2
import rl_env_server_pb2_grpc
import argparse
from common import *


parser = argparse.ArgumentParser()
parser.add_argument('-p', '--port', type=int, default=5000)
args = parser.parse_args()


class RLEnvServer(rl_env_server_pb2_grpc.RLEnvServerServicer):
	def __init__(self):
		super().__init__()
		self.env = None
		self.client_ids = []


	def on_connected(self, request, context):
		self.client_ids.append(request.id)
		return rl_env_server_pb2.Void()


	def on_disconnected(self, request, context):
		self.client_ids.remove(request.id)
		return rl_env_server_pb2.Void()


	def echo(self, request, context):
		return rl_env_server_pb2.EchoResponse(message=request.message)


	def init(self, request, context):
		self.env = decode(request.env)
		if self.env is not None:
			return rl_env_server_pb2.InitResponse(status="OK")
		else:
			return rl_env_server_pb2.InitResponse(status="NG")


	def numConnection(self, request, context):
		return rl_env_server_pb2.NumConnectionResponse(numConnection=len(self.client_ids))


	def func(self, request, context):
		if self.env is None:
			return rl_env_server_pb2.FuncResponse(
				message="Must set env first",
				ret=encode(None),
			)

		if hasattr(self.env, request.funcName):
			args = decode(request.args)
			ret = getattr(self.env, request.funcName)(**args)
			return rl_env_server_pb2.FuncResponse(
				message="",
				ret=encode(ret),
			)
		else:
			return rl_env_server_pb2.FuncResponse(
				message="Env has no function: " + request.funcName,
				ret=encode(None),
			)


	def property(self, request, context):
		if self.env is None:
			return rl_env_server_pb2.FuncResponse(
				message="Must set env first",
				ret=encode(None),
			)

		if hasattr(self.env, request.propertyName):
			ret = getattr(self.env, request.propertyName)
			return rl_env_server_pb2.PropertyResponse(
				message="",
				ret=encode(ret),
			)
		else:
			return rl_env_server_pb2.PropertyResponse(
				message="Env has no property: " + request.propertyName,
				ret=encode(None),
			)



def serve():
	server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
	rl_env_server_pb2_grpc.add_RLEnvServerServicer_to_server(RLEnvServer(), server)
	server.add_insecure_port('[::]:' + str(args.port))
	server.start()
	server.wait_for_termination()


if __name__ == '__main__':
	serve()

