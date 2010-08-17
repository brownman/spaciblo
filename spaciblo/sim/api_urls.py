"""The URLS for the API (not the user readable web UI)"""
import traceback

from django.conf.urls.defaults import *
from django.contrib.auth.models import User

from piston.resource import Resource

from models import *
from handler import *

class UserHandler(BaseHandler):
	"""The Piston handler for Django's user accounts"""
	model = User
	fields = ('username', 'first_name', 'last_name')
	allowed_methods = ('GET',)

class Thing(object):
	def __init__(self, name, rank):
		self.name = name
		self.rank = rank
		self.dink = []
		
t = Thing('foo', 'bar')
t.dink.append(Thing('dwong', 'dwink'))
t.dink.append([(u.username, u.first_name, u.last_name) for u in User.objects.all()])
t.dink.append({'moo':'cow'})

urlpatterns = patterns('',
	(r'^test/$', Resource(handler=PlainObjectHandler), {'obj':t }),
	(r'^template/$', Resource(handler=TemplateHandler)),
	(r'^template/(?P<id>[^/]+)/$', Resource(handler=TemplateHandler)),
	(r'^template/(?P<template_id>[\d]+)/asset/(?P<asset_key>[^/]+)$', 'sim.api_views.template_asset'),
	(r'^asset/$', Resource(handler=AssetHandler)),
	(r'^asset/(?P<id>[^/]+)/$', Resource(handler=AssetHandler)),
	(r'^space/$', Resource(handler=SpaceHandler)),
	(r'^space/(?P<id>[^/]+)/$', Resource(handler=SpaceHandler)),
	(r'^space/(?P<id>[^/]+)/scene/$', 'sim.api_views.scene_document'),
	
)
	
# Copyright 2010 Trevor F. Smith (http://trevor.smith.name/) Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0 Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
