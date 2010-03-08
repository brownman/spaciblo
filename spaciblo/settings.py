import os 

PROJECT_ROOT = os.path.realpath(os.path.dirname(__file__))
BACKUP_ROOT = PROJECT_ROOT + '/backups/'
MEDIA_ROOT = PROJECT_ROOT + '/media/'
TEMPLATE_DIRS = ( PROJECT_ROOT + '/templates/', )

# the directories under the media root which include things like uploaded pics or other dynamic files
DYNAMIC_MEDIA_DIRS = ['asset','resized_image']

SOUTH_AUTO_FREEZE_APP = True

SITE_ID = 1

USE_I18N = True

# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/admin-media/'

TEMPLATE_CONTEXT_PROCESSORS = (
	'django.core.context_processors.request',
	'django.core.context_processors.auth',
	'django.core.context_processors.media',
    'context_processors.site',
)

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)


MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

ROOT_URLCONF = 'urls'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
	'django.contrib.admin',
	'south',
	'spaciblo.ground',
	'spaciblo.sim',
	'spaciblo.front',
)

from local_settings import *

# Copyright 2010 Trevor F. Smith (http://trevor.smith.name/) Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0 Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
