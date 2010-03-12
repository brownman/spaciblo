"""The URLS for the API (not the user readable web UI)"""
from django.conf.urls.defaults import *

from models import *

urlpatterns = patterns('',
	(r'^space/$', 'ground.views.model_list', { 'model':Space }),
	(r'^space/(?P<id>[\d]+)/$', 'ground.views.model', { 'model':Space }),
	(r'^space/(?P<id>[\d]+)/scene/$', 'ground.views.model_attribute', { 'model':Space, 'attr_name':'scene_document', 'mimetype':'application/json' }),
	(r'^template/$', 'ground.views.model_list', { 'model':Template }),
	(r'^template/(?P<id>[\d]+)/$', 'ground.views.model', { 'model':Template }),
	(r'^template/(?P<template_id>[\d]+)/asset/(?P<asset_key>[^/]+)$', 'sim.api_views.template_asset'),
)
	
# Copyright 2010 Trevor F. Smith (http://trevor.smith.name/) Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0 Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
