from django.conf.urls.defaults import *

from django_restapi.model_resource import Collection
from django_restapi.responder import XMLResponder

from models import *

urlpatterns = patterns('',
	(r'^spaciblo.js$', 'sim.views.spaciblo_js'),
	(r'^space/(?P<id>[\d]+)/$', 'sim.views.space'),
	(r'^space/(?P<id>[\d]+)/debug/$', 'sim.views.space_debug'),
    (r'^$', 'sim.views.index'),
	(r'^scratch/', 'sim.views.scratch'),
)

# Copyright 2010 Trevor F. Smith (http://trevor.smith.name/) Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0 Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
