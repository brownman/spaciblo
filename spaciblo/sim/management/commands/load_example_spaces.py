import os
import csv
import ConfigParser

from django.template.defaultfilters import slugify
from django.core.management.base import NoArgsCommand, CommandError
from django.core.files import File
from sim.management import *
from ground.hydration import Hydration

class Command(NoArgsCommand):
	"""Loads the example templates and spaces."""
	help = "Loads the example templates and spaces."

	requires_model_validation = True

	def handle_noargs(self, **options):
		from django.contrib.auth.models import User
		
		if len(User.objects.filter(is_staff=True)) == 0:
			print 'There must be at least one staff user before we can load templates.'
			return
		
		admin_user = User.objects.filter(is_staff=True).order_by('id')[0]
		
		for template_dir in os.listdir(TEMPLATE_DIR_PATH):
			abs_dir = os.path.join(TEMPLATE_DIR_PATH, template_dir)
			if not os.path.isdir(abs_dir): continue
			template = self.load_template_from_dir(abs_dir, admin_user)
			print 'loaded template: ', template
		
		for space_dir in os.listdir(SPACE_DIR_PATH):
			abs_dir = os.path.join(SPACE_DIR_PATH, space_dir)
			if not os.path.isdir(abs_dir): continue
			space = self.load_space_from_dir(abs_dir, admin_user)
			print 'loaded space: ', space

	def load_space_from_dir(self, space_dir_path, owner):
		from sim.models import Space, Template
		from sim.scene import Thing, Scene, Position, Orientation
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
		root_thing = Thing(0)
		thing_id = 1
		for thing_row in things_reader:
			template_name = thing_row[0]
			if Template.objects.filter(name=template_name).count() != 1:
				print 'things.csv references an unknown template: %s' % template_name
				continue
			template = Template.objects.get(name=template_name)
			position = Position(float(thing_row[1]), float(thing_row[2]), float(thing_row[3])) 
			orientation = Orientation(float(thing_row[4]), float(thing_row[5]), float(thing_row[6]), float(thing_row[7]))
			root_thing.add_thing(Thing(thing_id, template, position, orientation))
			thing_id += 1
		scene = Scene(space)
		scene.thing = root_thing
		space.scene_document = Hydration.dehydrate(scene)
		space.save()
		return space

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
		elif filename.endswith('.obj') or filename.endswith('.mtl'):
			return 'geometry'
		else:
			return None

	def load_template_from_dir(self, template_dir_path, owner):
		from sim.models import Template, Asset, TemplateAsset
		template_name = os.path.basename(template_dir_path)
		seat_position = '0,0,0'
		seat_orientation = '1,0,0,0'

		properties_path = os.path.join(template_dir_path, TEMPLATE_PROPERTIES_FILE_NAME)
		if os.path.isfile(properties_path):
			config = ConfigParser.ConfigParser()
			config.readfp(open(properties_path))
			if config.has_option(TEMPLATE_INFO_SECTION, TEMPLATE_NAME_OPTION):
				template_name = config.get(TEMPLATE_INFO_SECTION, TEMPLATE_NAME_OPTION)
			if config.has_option(SEATING_SECTION, POSITION_OPTION):
				seat_position = config.get(SEATING_SECTION, POSITION_OPTION)
			if config.has_option(SEATING_SECTION, ORIENTATION_OPTION):
				seat_orientation = config.get(SEATING_SECTION, ORIENTATION_OPTION)
				
		else:
			print 'no properties at ', properties_path
		
		template, created = Template.objects.get_or_create(name=template_name, owner=owner)
		template.seat_position = seat_position
		template.seat_orientation = seat_orientation
		template.save()
		
		asset_files = [os.path.join(template_dir_path, filename) for filename in os.listdir(template_dir_path)]
		for asset_path in asset_files:
			if not os.path.isfile(asset_path): continue
			asset_name = os.path.basename(asset_path)
			file_type = self.asset_type(asset_name)
			if asset_name == TEMPLATE_PROPERTIES_FILE_NAME:
				continue
			if file_type == None:
				print 'Ignoring %s asset: %s' % (template_name, asset_name)
				continue
			asset_file = file(asset_path, 'r')
			asset = template.get_asset(key=asset_name)
			if asset == None:
				asset = Asset(type=file_type)
			asset.file.save(asset_name, File(asset_file), save=False)
			asset.save()
			asset_file.close()
			template_asset, created = TemplateAsset.objects.get_or_create(template=template, asset=asset, key=asset_name)
		template.prep_assets()
		
		return template

# Copyright 2010 Trevor F. Smith (http://trevor.smith.name/) Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0 Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
