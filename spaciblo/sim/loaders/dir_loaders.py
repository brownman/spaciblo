import os
import csv
import ConfigParser
import tarfile
import tempfile
import simplejson

from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.core.files import File
from django.contrib.auth import login, authenticate
from django.http import HttpRequest
from django.contrib.sessions.models import Session

from django.conf import settings
from django.utils.importlib import import_module

from spaciblo.sim.handler import to_json
from spaciblo.sim.events import TemplateUpdated
from spaciblo.sim.models import Space, Template, Asset, TemplateAsset
from spaciblo.sim.glge import Object, Scene, Group, GroupTemplate

TEMPLATE_PROPERTIES_FILE_NAME = "template.properties"
TEMPLATE_INFO_SECTION = "Template Info"
TEMPLATE_NAME_OPTION = "template-name"

SEATING_SECTION = "Seating"
POSITION_OPTION = 'position'
ORIENTATION_OPTION = 'orientation'
APPLICATION_DIR = 'application-dir'

SPACE_TEMPLATE_FILE_NAME = 'things.csv'
SPACE_PROPERTIES_FILE_NAME = "space.properties"
SPACE_INFO_SECTION = "Space Info"
DEFAULT_BODY_OPTION = "default-body"

class SpaceDirLoader():
	def load(self, space_dir_path, owner):
		space_name = os.path.basename(space_dir_path)
		things_path = os.path.join(space_dir_path, SPACE_TEMPLATE_FILE_NAME)
		if not os.path.isfile(things_path):
			print 'No things.csv in space %s, ignoring' % space_name
			return None
		properties_path = os.path.join(space_dir_path, SPACE_PROPERTIES_FILE_NAME)
		if not os.path.isfile(properties_path):
			print 'No %s in space %s, ignoring' % (SPACE_PROPERTIES_FILE_NAME, space_name)
			return None
		config = ConfigParser.ConfigParser()
		config.readfp(open(properties_path))
		if config.has_option(SPACE_INFO_SECTION, DEFAULT_BODY_OPTION):
			body_name = config.get(SPACE_INFO_SECTION, DEFAULT_BODY_OPTION)
		else:
			print 'No %s option in %s.  Cannot create the space.' % (DEFAULT_BODY_OPTION, SPACE_PROPERTIES_FILE_NAME)
			return None
		if Template.objects.filter(name=body_name).count() != 1:
			print 'An unknown template is specified for default-body: %s' % body_name
			return None
		body_template = Template.objects.get(name=body_name)
		space, created = Space.objects.get_or_create(name=space_name, default_body=body_template, slug=slugify(space_name))
		space.add_member(owner, is_admin=True, is_editor=True)
		
		things_reader = csv.reader(open(things_path))
		scene = Scene()
		for thing_row in things_reader:
			template_name = thing_row[0]
			if Template.objects.filter(name=template_name).count() != 1:
				print 'things.csv references an unknown template: %s' % template_name
				continue
			template = Template.objects.get(name=template_name)
			node = Group()
			node.group_template = GroupTemplate(template_id=template.id, name=template.name)
			node.set_loc([float(thing_row[1]), float(thing_row[2]), float(thing_row[3])])
			node.set_quat([float(thing_row[4]), float(thing_row[5]), float(thing_row[6]), float(thing_row[7])])
			node.set_scale([float(thing_row[8]), float(thing_row[9]), float(thing_row[10])]) 
			#TODO hook the template data and ID
			scene.children.append(node)
		space.scene_document = to_json(scene)
		space.save()
		return space

class TemplateDirLoader():
	"""Loads templates using files in a directory."""

	def load(self, template_dir_path, owner):
		template_name = os.path.basename(template_dir_path)
		seat_position = '0,0,0'
		seat_orientation = '1,0,0,0'
		application_dir = None
		
		properties_path = os.path.join(template_dir_path, TEMPLATE_PROPERTIES_FILE_NAME)
		if os.path.isfile(properties_path):
			config = ConfigParser.ConfigParser()
			config.readfp(open(properties_path))
			if config.has_option(TEMPLATE_INFO_SECTION, TEMPLATE_NAME_OPTION):
				template_name = config.get(TEMPLATE_INFO_SECTION, TEMPLATE_NAME_OPTION)
			if config.has_option(TEMPLATE_INFO_SECTION, APPLICATION_DIR):
				application_dir = config.get(TEMPLATE_INFO_SECTION, APPLICATION_DIR)
			if config.has_option(SEATING_SECTION, POSITION_OPTION):
				seat_position = config.get(SEATING_SECTION, POSITION_OPTION)
			if config.has_option(SEATING_SECTION, ORIENTATION_OPTION):
				seat_orientation = config.get(SEATING_SECTION, ORIENTATION_OPTION)
		else:
			print 'no properties at ', properties_path
		
		template, template_created = Template.objects.get_or_create(name=template_name, owner=owner)
		template.seat_position = seat_position
		template.seat_orientation = seat_orientation
		template.save()
		
		asset_files = [os.path.join(template_dir_path, filename) for filename in os.listdir(template_dir_path)]
		for asset_path in asset_files:
			if not os.path.isfile(asset_path): continue
			asset_name = os.path.basename(asset_path)
			file_type = self.asset_type(asset_name)
			if asset_name == TEMPLATE_PROPERTIES_FILE_NAME: continue
			if file_type == None: continue
			asset_file = file(asset_path, 'r')
			asset = template.get_asset(key=asset_name)
			if asset == None: asset = Asset(type=file_type)
			asset.file.save(asset_name, File(asset_file), save=False)
			asset.save()
			asset_file.close()
			template_asset, created = TemplateAsset.objects.get_or_create(template=template, asset=asset, key=asset_name)

		if application_dir != None:
			app_dir_path = os.path.join(template_dir_path, application_dir)
			if not os.path.exists(app_dir_path):
				print 'Application directory "%s" does not exist' % app_dir_path
			elif not os.path.isdir(app_dir_path):
				print 'Application directory "%s" is not a directory' % app_dir_path
			else:
				#print 'Creating app archive %s' % app_dir_path
				app_archive = self.create_app_archive(template_dir_path, application_dir)
				asset = template.get_asset(key=Asset.APPLICATION_KEY)
				if asset == None: asset = Asset(type='application')
				asset.file.save(Asset.APPLICATION_KEY, File(app_archive), save=False)
				asset.save()
				app_archive.close()
				template_asset, created = TemplateAsset.objects.get_or_create(template=template, asset=asset, key=Asset.APPLICATION_KEY)

		template.prep_assets()
		return template

	def asset_type(self, filename):
		filename = filename.lower()
		if filename.endswith('.bvh'):
			return 'animation'
		elif filename.endswith('.js'):
			return 'script'
		elif filename.endswith('.jpg') or filename.endswith('.gif') or filename.endswith('.png'):
			return 'texture'
		elif filename.endswith('.txt'):
			return 'text'
		elif filename.endswith('.obj') or filename.endswith('.mtl') or filename.endswith('.json'):
			return 'geometry'
		else:
			return None

	def create_app_archive(self, template_dir_path, application_dir):
		full_app_path = os.path.join(template_dir_path, application_dir)
		working_dir = tempfile.mkdtemp('template-app')
		tar_path = os.path.join(working_dir, 'template-app.tgz')
		tar = tarfile.open(tar_path, "w:gz")
		for target_file in os.listdir(full_app_path):
			full_target_path = os.path.join(full_app_path, target_file)
			tar.add(full_target_path, arcname=target_file)
		tar.close()
		return open(tar_path)

# Copyright 2010 Trevor F. Smith (http://trevor.smith.name/) Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0 Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
