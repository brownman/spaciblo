import traceback
import os
from django.db import models
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.exceptions import *
from django.core.files.storage import default_storage
from django.core.files import File

from scene import Scene
from sim.loaders.obj import ObjLoader, MtlLibLoader
from ground.hydration import Hydration

class HydrateModel(models.Model):
	
	@classmethod
	def type(cls):
		return cls.__name__
	
	class Meta:
		abstract = True

class SpaceManager(models.Manager):
	def get_membership(self, space, user):
		"""Returns a tuple of the form (allow_entry, SpaceMember) where allow_entry is True or False and SpaceMember will be None if there's no SpaceMember record for this user and space"""
		try:
			space_member = SpaceMember.objects.get(space=space, member=user)
		except:
			space_member = None
		if space.state == 'closed': return (False, space_member)
		if space.state == 'admin_only' and (space_member == None or not space_member.is_admin): return (False, space_member)
		if space.max_guests > 0: return (True, space_member) #TODO respect the guest limits
		return (space_member != None, space_member)
			
class Space(HydrateModel):
	"""An n-dimensional cartesian space"""
	name = models.CharField(max_length=1000)
	slug = models.SlugField(max_length=1000)
	STATE_CHOICES = (('open', 'open'), ('admin_only', 'admin_only'), ('closed', 'closed'))
	state = models.CharField(max_length=20, choices=STATE_CHOICES, default='admin_only', blank=False, null=False)
	max_guests = models.IntegerField(blank=False, null=False, default=0)
	scene_document = models.TextField(blank=False, null=False, default='{"type":"Scene", "thing":{"type":"Thing", "attributes": { "id":"0" } } }')
	default_body = models.ForeignKey("Template", blank=False, null=False)
	
	objects = SpaceManager()

	class HydrationMeta:
		attributes = ['id', 'name', 'slug', 'state', 'max_guests']
		nodes = ['scene_document']

	def add_member(self, user, is_admin=False, is_editor=False):
		membership, created = SpaceMember.objects.get_or_create(space=self, member=user)
		membership.is_admin = is_admin
		membership.is_editor = is_editor
		membership.save()

	@models.permalink
	def get_absolute_url(self): 
		return ('sim.views.space', (), { 'id':self.id })

	def __unicode__(self):
		return "Space #%s: %s" % (self.id, self.name)

class SpaceMember(HydrateModel):
	"""A member of a space which can have admin or editor rights."""
	space = models.ForeignKey(Space, blank=False, null=False)
	member = models.ForeignKey(User, blank=False, null=False)
	is_admin = models.BooleanField(blank=False, default=False)
	is_editor = models.BooleanField(blank=False, default=False)
	class HydrationMeta:
		attributes = ['id', 'member', 'is_admin', 'is_editor']

class Asset(HydrateModel):
	"""A chunk of typed data used by a template to instantiate a Thing in a Space."""
	TYPE_CHOICES = (('geometry', 'geometry'), ('animation', 'animation'), ('script', 'script'), ('texture', 'texture'), ('text', 'text'))
	type = models.CharField(max_length=20, choices=TYPE_CHOICES, blank=False, null=False, default='text')
	file = models.FileField(upload_to='asset/%Y/%m/%d', null=False, blank=False)
	prepped_file = models.FileField(upload_to='prepped/%Y/%m/%d', null=True, blank=True) # a version of this asset which is optimized for use, e.g. a JSON representation of a geometry
	
	def save(self, force_insert=False, force_update=False):
		"""Deletes old files if they exist for this asset"""
		try:
			if Asset.objects.filter(pk=self.pk).count() > 0:
				old_obj = Asset.objects.get(pk=self.pk)
				if self.file and old_obj.file and old_obj.file.path != self.file.path:
					default_storage.delete(old_obj.file.path)
				if self.prepped_file and old_obj.prepped_file and old_obj.prepped_file.path != self.prepped_file.path:
					default_storage.delete(old_obj.prepped_file.path)
		except:
			traceback.print_exc()
		super(Asset, self).save(force_insert, force_update)
	
	def __unicode__(self):
		return self.file.name
	class HydrationMeta:
		attributes = ['id', 'type', 'file', 'prepped_file']

class TemplateAsset(HydrateModel):
	"""A mediation record linking an asset with a template"""
	template = models.ForeignKey('Template', blank=False, null=False, related_name="templateassets")
	asset = models.ForeignKey(Asset, blank=False, null=False)
	key = models.CharField(max_length=1000, blank=False, null=False)
	def __unicode__(self):
		return "TemplateAsset: %s" % self.asset
	class HydrationMeta:
		attributes = ['id', 'key']
		nodes = ['asset']

class TemplateSetting(HydrateModel):
	"""A key/value tuple used to initialize a Thing's state"""
	key = models.CharField(max_length=1000, blank=False, null=False)
	value = models.TextField(blank=False, null=False)
	class HydrationMeta:
		attributes = ['id', 'key']
		text_node = 'value'
	def __unicode__(self):
		return "<%s|%s>" % (self.key, self.value)

class TemplateChild(HydrateModel):
	"""A record of where a child template should be in relation to its parent."""
	template = models.ForeignKey('Template', blank=False, null=False)
	#TODO make position and orientation custom tuple fields
	position = models.CharField(max_length=1000, blank=False, null=False, default="0,0,0") # px, py, pz
	orientation = models.CharField(max_length=1000, blank=False, null=False, default="1,0,0,0") # qs,qx,qy,qz
	settings = models.ManyToManyField(TemplateSetting, blank=True, null=True) # overrides the child's setting defaults
	def __unicode__(self):
		return "TemplateChild: %s" % self.template
	class Meta:
		verbose_name_plural = 'template children'
	class HydrationMeta:
		attributes = ['id', 'position', 'orientation']
		ref_attributes = ['template']
		nodes = ['settings']
	
class Template(HydrateModel):
	"""A set of information used to instantiate a Thing in a Space."""
	name = models.CharField(max_length=1000, blank=False, null=False, default="A Template")
	owner = models.ForeignKey(User, blank=False, null=False)
	last_updated = models.DateTimeField(auto_now=True, blank=False, null=False)
	assets = models.ManyToManyField('Asset', blank=True, null=True, through='TemplateAsset')
	settings = models.ManyToManyField(TemplateSetting, blank=True, null=True) # used as defaults when creating a new Thing
	children = models.ManyToManyField(TemplateChild, blank=True, null=True, related_name="parents")
	#TODO make position and orientation custom tuple fields
	seat_position = models.CharField(max_length=1000, blank=True, null=True, default="0,0,0") # px, py, pz
	seat_orientation = models.CharField(max_length=1000, blank=True, null=True, default="1,0,0,0") # qs,qx,qy,qz

	def prep_assets(self):
		obj_assets = []
		mtl_assets = {}
		for template_asset in TemplateAsset.objects.filter(template=self):
			if template_asset.asset.type == 'geometry' and template_asset.asset.file.name.endswith('.mtl'):
				mtl_assets[template_asset.key] = template_asset.asset
			if template_asset.asset.type == 'geometry' and template_asset.asset.file.name.endswith('.obj'):
				obj_assets.append(template_asset.asset)
		print mtl_assets
		for obj_asset in obj_assets: # try to save a prepped geometry JSON
			try:
				loader = ObjLoader()
				obj = loader.parse(open(obj_asset.file.path).read())
				if obj.mtllib and mtl_assets.has_key(obj.mtllib):
					mtllib_loader = MtlLibLoader()
					mtllib = mtllib_loader.parse(open(mtl_assets[obj.mtllib].file.path).read())
				elif obj.mtllib:
					print 'Obj asset %s requires an unknown mtllib: %s' % (obj_asset.file, obj.mtllib)
					mtllib = None
				else:
					print 'Obj has no mtllib'
					mtllib = None
				geometry = obj.toGeometry(mtllib)
				path = '/tmp/prepped_geo-%s' % self.id
				json_file = file(path, 'wb')
				json_file.write(Hydration.dehydrate(geometry))
				json_file.close()
				json_file = file(path, 'r')
				obj_asset.prepped_file.save(json_file.name, File(json_file), save=False)
				obj_asset.save()
				json_file.close()
				os.unlink(path)
			except:
				traceback.print_exc()

	def get_asset(self, key):
		try:
			return TemplateAsset.objects.get(template=self, key=key).asset
		except ObjectDoesNotExist:
			return None

	def __unicode__(self):
		return self.name
	class HydrationMeta:
		attributes = ['id', 'owner', 'name']
		nodes = ['templateassets', 'settings', 'children']

class SimulatorPoolRegistration(models.Model):
	"""A simulator pool address in this cluster"""
	ip = models.IPAddressField()
	port = models.IntegerField()
	class HydrationMeta:
		attributes = ['id', 'ip', 'port']

HYDRATE_MODELS = [Template, TemplateChild, TemplateSetting, TemplateAsset, Asset, SpaceMember, Space]

# Copyright 2010 Trevor F. Smith (http://trevor.smith.name/) Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0 Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
