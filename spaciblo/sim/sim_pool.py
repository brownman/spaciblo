"""Simulations and a simple pool."""
import datetime
import threading
import Queue
from time import sleep

from models import *
from events import *
from scene import *

DEFAULT_SIM_POOL = None

class Simulator:
	"""The class responsible for managing various aspects of Space simulation such as the event queue, run loop, and scene."""
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

	def stop(self):
		if self.state != Simulator.running:
			print 'Tried to stop a simulator which is not running: ' % self.state
			return
		self.state = Simulator.terminating
		self.should_run = False
		self.state = Simulator.stopped

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
			
			if not self.should_run: return
			
			if event.event_name() == 'AddUserThingRequest':
				user_thing = self.scene.thing.get_user_thing(event.username)
				if user_thing is None:
					thing = self.scene.add_user_thing(User.objects.get(username=event.username), Position().hydrate(event.position), Orientation().hydrate(event.orientation))
					self.pool.sim_server.send_space_event(self.space.id, ThingAdded(self.space.id, event.username, thing.id, self.space.default_body.id, self.scene.thing.id, thing.position.__unicode__(), thing.orientation.__unicode__()))
				else:
					print "Already have a user thing with id", user_thing.id

			elif event.event_name() == 'UserExited':
				print 'User exited', event.username
				for thing in self.scene.thing.list_things():
					if thing.user is not None and thing.user.username == event.username:
						self.scene.thing.remove_thing(thing)
						self.pool.sim_server.send_space_event(self.space.id, ThingRemoved(self.space.id, thing.id))

			elif event.event_name() == 'UserMessage':
				if event.connection.user != None and event.username == event.connection.user.username:
					self.pool.sim_server.send_space_event(self.space.id, event)

			elif event.event_name() == 'UserThingMoveRequest':
				if event.connection.user != None and event.username == event.connection.user.username:
					user_thing = self.scene.thing.get_user_thing(event.username)
					if user_thing == None:
						print "No such user thing: %s" % event.username
					else:
						user_thing.position.hydrate(event.position)
						user_thing.orientation.hydrate(event.orientation)
						response = ThingMoved(self.space.id, user_thing.id, user_thing.position, user_thing.orientation)
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

class SimulatorPool:
	"""A simple manager for space simulators."""
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

	def stop_all_spaces(self):
		self.state = SimulatorPool.terminating
		for sim in self.simulators:
			sim.stop()
		self.state = SimulatorPool.stopped

	def __unicode__(self):
		return "Simulator Pool"

	def stateToString(self, state=None):
		if not state: state = self.state
		if state == 0: return 'initializing'
		if state == 1: return 'running'
		if state == 2: return 'terminating'
		if state == 3: return 'stopped'

# Copyright 2010 Trevor F. Smith (http://trevor.smith.name/) Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0 Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
