"""
A system for specifying and implementing how ground allows or refuses resource access.

In this example, the ExampleModel class is marked to allow the owner (in this case the User object specified in the 'user' field) to update and delete their ExampleModels.
It is also marked to allow any request (even anonymous, unauthed requests) to read the ExampleModel resources via Ground.

from forms import ExampleForm

class ExampleModel(Model):
	user = models.ForeignKey(User)
	name = models.CharField(max_length=20)
	image = models.FileField(upload_to='example_image')
	
	class AuthorizationMeta:
		owner = 'user'
		form = ExampleForm
		read_all = True
		update_own = True
		delete_own = True
"""

AUTHORIZATION_META_NAME = 'AuthorizationMeta'
OWNER = 'owner'
FORM = 'form'
CREATE = 'create'
READ_ALL = 'read_all'
READ_OWN = 'read_own'
UPDATE_ALL = 'update_all'
UPDATE_OWN = 'update_own'
DELETE_ALL = 'delete_all'
DELETE_OWN = 'delete_own'

META_NAMES = [OWNER, FORM, CREATE, READ_ALL, READ_OWN, UPDATE_ALL, UPDATE_OWN, DELETE_ALL, DELETE_OWN]

class Authorization:
	"""A representation of the fields in an AuthorizationMeta class on the source."""
	def __init__(self, source=None):
		self.owner = None
		self.form = None
		self.create = False
		self.read_all = False
		self.read_own = True
		self.update_all = False
		self.update_own = True
		self.delete_all = False
		self.delete_own = True

		if source and hasattr(source, AUTHORIZATION_META_NAME):
			auth_meta = getattr(source, AUTHORIZATION_META_NAME)
			for meta_name in META_NAMES:
				if hasattr(target, meta_name): setattr(self, meta_name, getattr(target, meta_name))

		if self.create and not self.form: raise Exception("Can not allow creation without a form")
		if self.update_all or self.update_own: 
			if not self.form: raise Exception("Can not allow updates without a form")
		
		
# Copyright 2010 Trevor F. Smith (http://trevor.smith.name/) Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0 Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
