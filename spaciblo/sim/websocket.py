"""A library for the service of WebSockets (http://dev.w3.org/html5/websockets/) based connections"""
import socket
import threading
import sys
import time

class WebSocketServer(threading.Thread):
	"""The server class which accepts incoming connections, parses the WebSockets request headers, sends the WebSockets response headers, and then passes control of the socket to a callback."""
	response_header_pattern = '''HTTP/1.1 101 Web Socket Protocol Handshake\r\nUpgrade: WebSocket\r\nConnection: Upgrade\r\nWebSocket-Origin: %s\r\nWebSocket-Location: %s\r\nWebSocket-Protocol: %s'''

	def __init__(self, client_handler, port, protocol='0.01'):
		"""client_handler must be a callable which takes a single argument: a socket connected to the browser"""
		self.client_handler = client_handler
		self.port = port
		self.protocol = protocol
		self.sock = socket.socket()
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.bind(('', self.port));
		self.sock.listen(1);
		threading.Thread.__init__(self)
		
	def parse_request_header(self, header):
		"""Breaks up the header lines of the WebSocket request into a dictionary"""
		lines = [token.strip() for token in header.split('\r')[1:]]
		result = {}
		for line in lines:
			if len(line) == 0: break
			key, value = line.split(' ', 1)
			result[key[:len(key) - 1]] = value
		return result
		
	def handle_socket(self, client_socket):
		"""Sends the response headers and then hands the socket to the client_handler"""
		request_headers = self.parse_request_header(client_socket.recv(4096))
		location_host = 'ws://%s/' % request_headers['Host']
		origin_host = request_headers['Origin']
		response_header = self.response_header_pattern % (origin_host, location_host, self.port)
		client_socket.send( response_header + '\r\n\r\n')
		self.client_handler(client_socket)
		client_socket.close()

	def start(self):
		"""Spawn a thread to handle each incoming web socket request"""
		#TODO don't spawn a thread to handle each incoming web socket request
		while True:
			t,p = self.sock.accept();
			threading.Thread(target = self.handle_socket, args = (t,)).start()

if __name__ == "__main__":
	def client_handler(client_socket):
		"""A little example which occasionally sends the time to the browser"""
		import time, datetime
		while True:
			message = 'time: %s' % datetime.datetime.now()
			client_socket.send('\x00%s\xff' % message)
			time.sleep(1)

	server = WebSocketServer(client_handler, 9876)
	server.start()
	try:
		while True: time.sleep(100000)
	except (KeyboardInterrupt, SystemExit):
		sys.exit()

# Copyright 2010 Trevor F. Smith (http://trevor.smith.name/) Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0 Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
