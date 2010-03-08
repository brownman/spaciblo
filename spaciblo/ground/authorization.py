AUTHORIZATION_META_NAME = 'AuthorizationMeta'

# This is not used yet.

class Authorization:
	def __init__(self, create=False, read_all=False, read_own=False, update_all=False, update_own=False, delete_all=False, delete_own=False):
		self.create = create
		self.read_all = read_all
		self.read_own = read_own
		self.update_all = update_all
		self.update_own = update_own
		self.delete_all = delete_all
		self.delete_own = delete_own
		
# Copyright 2010 Trevor F. Smith (http://trevor.smith.name/) Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0 Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
