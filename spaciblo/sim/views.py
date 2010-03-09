import datetime
import calendar
import pprint
import traceback

from django.conf import settings
from django.db.models import Q
from django.template import Context, loader
from django.http import HttpResponse, Http404, HttpResponseServerError, HttpResponseRedirect, HttpResponsePermanentRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.comments.models import Comment
from django.contrib.sites.models import Site
from django.utils.html import strip_tags
import django.contrib.contenttypes.models as content_type_models
from django.template import RequestContext
from django.core.cache import cache
from django.core.mail import send_mail
from django.contrib.admin.views.decorators import staff_member_required
from django.template.loader import render_to_string

import sim_pool as sim_pool
import comet as comet
import events as events
import scene as scene
from spaciblo.hydration import *
from spaciblo.sim.models import *

def scratch(request):
	return render_to_response('sim/scratch.html', {'sim_pool': sim_pool.DEFAULT_SIM_POOL }, context_instance=RequestContext(request))

def index(request):
	return render_to_response('sim/index.html', {'sim_pool': sim_pool.DEFAULT_SIM_POOL }, context_instance=RequestContext(request))

def space(request, id):
	space = get_object_or_404(Space, pk=id)
	return render_to_response('sim/space.html', { 'space':space }, context_instance=RequestContext(request))

@staff_member_required
def space_debug(request, id):
	space = get_object_or_404(Space, pk=id)
	return render_to_response('sim/space_debug.html', { 'space':space }, context_instance=RequestContext(request))

def spaciblo_js(request):
	return render_to_response('sim/spaciblo.js', {'events': events.SIM_EVENTS, 'scene_graph_classes': scene.SCENE_GRAPH_CLASSES }, context_instance=RequestContext(request), mimetype='application/javascript')

# Copyright 2010 Trevor F. Smith (http://trevor.smith.name/) Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0 Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
