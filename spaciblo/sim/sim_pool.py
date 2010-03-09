import datetime
import threading
import Queue
from time import sleep

from models import *
from events import *
from scene import *
from spaciblo.hydration import *

DEFAULT_SIM_POOL = None

class Simulator:
	initializing, ready, running, terminating, stopped = range(5)
	possible_states = [ initializing, ready, running, terminating, stopped ]
	
	def __init__(self, pool, space):
		self.state = Simulator.initializing
		self.should_run = False

		self.pool = pool
		self.space = space
		self.scene = Scene(space)
		
		self.event_queue = Queue.Queue(-1)
		self.script_engine = None
		self.physics_engine = None
		
		self.state = Simulator.ready

	def __unicode__(self):
		return "Simulator for %s" % self.space

	def run(self):
		"""The simulation loop"""
		if not self.state == Simulator.ready:
			print "Tried to run a simulator in an unready state: %s" % self
			return
		self.state = Simulator.running
		self.should_run = True
		while self.should_run:
			try:
				event = self.event_queue.get(block=True, timeout=5)
			except Queue.Empty:
				self.pool.sim_server.send_space_event(self.space.id, Heartbeat())
				continue

			if event.event_name() == 'AddAvatarRequest':
				avatar = self.scene.thing.get_avatar(event.username)
				if avatar is None:
					thing = self.scene.add_avatar(User.objects.get(username=event.username), Position().hydrate(event.position), Orientation().hydrate(event.orientation))
					self.pool.sim_server.send_space_event(self.space.id, ThingAdded(self.space.id, event.username, thing.id, self.scene.thing.id, thing.position.__unicode__(), thing.orientation.__unicode__()))
				else:
					print "Already have an avatar."

			elif event.event_name() == 'UserExited':
				print 'user exited', event.username
				for thing in self.scene.thing.list_things():
					if thing.user is not None and thing.user.username == event.username:
						self.scene.thing.remove_thing(thing)
						self.pool.sim_server.send_space_event(self.space.id, ThingRemoved(self.space.id, thing.id))
			elif event.event_name() == 'UserMessage':
				if event.connection.user != None and event.username == event.connection.user.username:
					self.pool.sim_server.send_space_event(self.space.id, event)

			elif event.event_name() == 'AvatarMoveRequest':
				if event.connection.user != None and event.username == event.connection.user.username:
					avatar = self.scene.thing.get_avatar(event.username)
					if avatar == None:
						print "No such avatar: %s" % event.username
					else:
						avatar.position.hydrate(event.position)
						avatar.orientation.hydrate(event.orientation)
						response = ThingMoved(self.space.id, avatar.id, avatar.position, avatar.orientation)
						self.pool.sim_server.send_space_event(self.space.id, response)
			else:
				print "Unknown event: %s" % event.event_name()

		print "Exiting %s %s"  % (self, datetime.datetime.now())

class SimulationThread(threading.Thread):
	def __init__ (self, pool, space):
		self.pool = pool
		self.space = space
		threading.Thread.__init__ ( self )

	def run(self):
		self.sim = Simulator(self.pool, self.space)
		self.pool.add_simulator(self.sim)
		try:
			self.sim.run()
		finally:
			self.pool.remove_simulator(self.sim)

class SimulatorPool():
	initializing, running, terminating, stopped = range(4)
	possible_states = [initializing, running, terminating, stopped]

	def __init__(self, sim_server):
		self.state = SimulatorPool.initializing
		self.sim_server = sim_server
		self.simulators= [] #<time_since_populated>
		self.state = SimulatorPool.running
	
	def get_simulator(self, space_id):
		for sim in self.simulators:
			if sim.space.id == space_id: return sim
		return None
	
	def add_simulator(self, simulator):
		self.simulators.append(simulator)

	def remove_simulator(self, simulator):
		self.simulators.remove(simulator)

	def start_all_spaces(self):
		for space in Space.objects.all():
			sim_thread = SimulationThread(self, space)
			sim_thread.start()
		
	def __unicode__(self):
		return "Simulator Pool"

	def stateToString(self, state=None):
		if not state: state = self.state
		if state == 0: return 'initializing'
		if state == 1: return 'running'
		if state == 2: return 'terminating'
		if state == 3: return 'stopped'

# Copyright 2010 Trevor F. Smith (http://trevor.smith.name/) Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0 Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
