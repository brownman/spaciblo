"""
Wrapper for loading templates from the template apps.
"""
import os

from django.conf import settings
from django.template import TemplateDoesNotExist
from django.utils._os import safe_join

def load_template_source(template_name, template_dirs=None):
	for app_dir in os.listdir(settings.TEMPLATE_APPS_DIR):
		app_path = os.path.join(settings.TEMPLATE_APPS_DIR, app_dir)
		template_dir_path = os.path.join(app_path, 'templates')
		if os.path.isdir(template_dir_path):
			template_path = os.path.join(template_dir_path, template_name)
			if os.path.isfile(template_path):
				return (open(template_path).read().decode(settings.FILE_CHARSET), template_path)
	raise TemplateDoesNotExist, "Did not find the template in the space template apps directory."
load_template_source.is_usable = True
