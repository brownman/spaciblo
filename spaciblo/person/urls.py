from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('',
	(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'person/login.html'}),
	(r'^logout/$', 'django.contrib.auth.views.logout_then_login', {'login_url': '/' }),

	(r'^register/$', 'person.views.register'),
	(r'^invite/$', 'person.views.invites'),
	(r'^invite/(?P<secret>[^/]+)/$', 'person.views.invite'),
	(r'^profile/$', 'person.views.profile_redirect'),
	(r'^find/$', 'person.views.find_people'),
	(r'^password-reset/$', 'person.views.password_reset'),
	(r'^email-validate/(?P<username>[^/]+)/(?P<secret>[^/]+)/$', 'person.views.email_validate'),
	(r'(?P<username>[^/]+)/$' , 'person.views.profile'),
)

# Copyright 2010 Trevor F. Smith (http://trevor.smith.name/) Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0 Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
