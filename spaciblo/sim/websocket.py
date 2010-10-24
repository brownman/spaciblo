"""A library for the service of WebSockets (http://dev.w3.org/html5/websockets/) based connections"""
import socket
import threading
import sys
import time
import re
import traceback
import struct
import hashlib
import Queue
import ws_contrib

def parse_request_header(header):
	"""Breaks up the header lines of the WebSocket request into a dictionary"""
	lines = [token.strip() for token in header.split('\r')[1:]]
	result = {}
	for line in lines:
		if len(line) == 0: break
		key, value = line.split(' ', 1)
		result[key[:len(key) - 1]] = value
	return result

def receive_web_socket_message(socket):
		message = []
		data = socket.recv(4096)
		while len(data) > 0:
			message.append(data)
			if data.endswith('\xff'): break
			data = socket.recv(4096)
		if len(message) == 0: return None
		joined = ''.join(message)
		return joined[1:len(joined) - 1]

class EventHandler:
	"""A handy class for handling incoming events"""
	def __init__(self):
		self.events = Queue.Queue(-1)
	def handle_event(self, event):
		from spaciblo.sim.events import Heartbeat
		if not isinstance(event, Heartbeat):
			self.events.put(event)

class WebSocketClient:
	def __init__(self, host, port, origin, protocol='0.01'):
		self.host = host
		self.port = port
		self.origin = origin
		self.protocol = protocol
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.connect((self.host, self.port))
		self.socket.send(self.generate_request_headers())
		time.sleep(0.2) #TODO a total hack, fix when this is used outside of tests
		self.response_headers = parse_request_header(self.socket.recv(4096))

	def receive(self):
		return receive_web_socket_message(self.socket)

	def send(self, message):
		self.socket.send('\x00')
		self.socket.send(message)
		self.socket.send('\xff')

	def close(self):
		self.socket.close()

	def generate_request_headers(self):
		security = ws_contrib.generate_request_security()
		headers = [
			"GET / HTTP/1.1",
			"Host: %s:%s" % (self.host, self.port),
			"Connection: Upgrade",
			"Sec-WebSocket-Key1: %s" % security[0][1],
			"Sec-WebSocket-Key2: %s" % security[1][1],
			"Sec-WebSocket-Protocol: sample",
			"Upgrade: WebSocket",
			"Origin: %s" % self.origin
		]
		return '%s\r\n\r\n%s' % ('\r\n'.join(headers), security[2])

class WebSocketServer(threading.Thread):
	"""The server class which accepts incoming connections, parses the WebSockets request headers, sends the WebSockets response headers, and then passes control of the socket to a callback."""
	response_header_pattern = '''HTTP/1.1 101 Web Socket Protocol Handshake\r\nUpgrade: WebSocket\r\nConnection: Upgrade\r\nSec-WebSocket-Origin: %s\r\nSec-WebSocket-Location: %s\r\nSec-WebSocket-Protocol: %s\r\n'''

	def __init__(self, client_handler, port, protocol='0.01'):
		"""client_handler must be a callable which takes a single argument: a socket connected to the browser"""
		self.client_handler = client_handler
		self.port = port
		self.protocol = protocol
		self.finish = False
		self.sock = socket.socket()
		self.sock.settimeout(2)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.bind(('', self.port))
		self.sock.listen(1)
		threading.Thread.__init__(self)

	def parse_key(self, key_value):
		key_number = int(re.sub("\\D", "", key_value))
		spaces = re.subn(" ", "", key_value)[1]
		if key_number % spaces != 0: raise Error('key_number %d is not an integral multiple of spaces %d' % (key_number, spaces))
		part = key_number / spaces
		return part

	def read_challenge(self, secret, request_headers):
		challenge = struct.pack("!I", self.parse_key(request_headers['Sec-WebSocket-Key1']))  # network byteorder int
		challenge += struct.pack("!I", self.parse_key(request_headers['Sec-WebSocket-Key2']))  # network byteorder int
		challenge += secret
		return challenge
		
	def handle_socket(self, client_socket):
		"""Sends the response headers and then hands the socket to the client_handler"""
		raw_headers = client_socket.recv(4096)
		request_headers = parse_request_header(raw_headers)
		challenge = self.read_challenge(raw_headers[len(raw_headers) - 8:], request_headers)
		md5 = hashlib.md5()
		md5.update(challenge)
		challenge_md5 = md5.digest()
		location_host = 'ws://%s/' % request_headers['Host']
		origin_host = request_headers['Origin']
		response_header = self.response_header_pattern % (origin_host, location_host, self.port)
		client_socket.send( response_header + '\r\n')
		client_socket.send(challenge_md5)
		self.client_handler(client_socket)
		client_socket.close()

	def stop(self):
		self.finish = True
		self.sock.close()

	def run(self):
		"""Spawn a thread to handle each incoming web socket request"""
		#TODO don't spawn a thread to handle each incoming web socket request
		while not self.finish:
			try:
				client_socket,p = self.sock.accept()
				if self.finish:	return
				client_socket.setblocking(1)
				threading.Thread(target = self.handle_socket, args = (client_socket,)).start()
			except (socket.timeout):
				if self.finish: return
				
if __name__ == "__main__":
	def client_handler(client_socket):
		"""A little example which occasionally sends the time to the browser"""
		import time, datetime
		while True:
			message = 'time: %s' % datetime.datetime.now()
			client_socket.send('\x00')
			client_socket.send(message)
			client_socket.send('\xff')
			time.sleep(1)

	server = WebSocketServer(client_handler, 9876)
	server.start()
	try:
		while True: time.sleep(100000)
	except (KeyboardInterrupt, SystemExit):
		sys.exit()

# Copyright 2010 Trevor F. Smith (http://trevor.smith.name/) Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0 Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
