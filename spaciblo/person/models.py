import os
import os.path
import Image
import urllib
import datetime, calendar
import random
import time
import re
import unicodedata
import traceback
import logging
import pprint

from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.db import models
from django.db.models import signals
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.dispatch import dispatcher
from django.core.mail import send_mail
from django.utils.encoding import force_unicode
from django.db.models import Q

import front.templatetags.imagetags as imagetags

PASSWORD_RESET_SECRET_PARAMETER = "secret"
PASSWORD_RESET_ID_PARAMETER = "id"

class ThumbnailedModel(models.Model):
	"""An abstract base class for models with an ImageField named "image" """
	def thumb(self):
		try:
			if hasattr(self, 'image') and self.image:
				image = self.image
			elif hasattr(self, 'photo') and self.photo:
				image = self.photo.image
			else:
				return ""
			file = settings.MEDIA_URL + image.path[len(settings.MEDIA_ROOT):]
			filename, miniature_filename, miniature_dir, miniature_url = imagetags.determine_resized_image_paths(file, "admin_thumb")
			if not os.path.exists(miniature_dir): os.makedirs(miniature_dir)
			if not os.path.exists(miniature_filename): imagetags.fit_crop(filename, 200, 100, miniature_filename)
			return """<img src="%s" />""" % miniature_url
		except:
			traceback.print_exc()
			return None
	thumb.allow_tags = True
	class Meta:
		abstract = True
		
class Photo(ThumbnailedModel):
	image = models.ImageField(upload_to='person_photo', blank=False)
	created = models.DateTimeField(auto_now_add=True)
	class Meta:
		ordering = ['-created']
	def __unicode__(self):
		return str(self.image)

def create_secret(): return User.objects.make_random_password(length=20)

class InviteManager(models.Manager):
	def distribute_invites(self, num_per_user):
		for profile in UserProfile.objects.filter(user__is_active=True):
			num_to_distribute = num_per_user - Invite.objects.filter(inviter=profile, sent_to=None).count()
			if num_to_distribute < 1: continue
			for i in range(0, num_per_user):
				profile.invites.add(Invite.objects.create())
			print 'Gave %s %s invites' % (profile.full_name, num_to_distribute)

class Invite(models.Model):
	secret = models.CharField(max_length=1024, blank=False, null=False, default=create_secret)
	sent_to = models.EmailField(default=None, blank=True, null=True)
	used_by = models.ForeignKey(User, blank=True, null=True, related_name='origin_invites')
	created = models.DateTimeField(auto_now_add=True)
	objects = InviteManager()
	def __unicode__(self): return 'Invite %s' % self.id
	@models.permalink
	def get_absolute_url(self):
		return ('person.views.invite', (), { 'secret':self.secret })

class InviteRequest(models.Model):
	email = models.EmailField(blank=False, null=False)
	created = models.DateTimeField(auto_now_add=True)
	def __unicode__(self): return 'InviteRequest: %s' % self.email
	
class UserProfileManager(models.Manager):
	def search(self, search_string):
		"""return user profiles which match ALL terms in one or more of full name, username, location, email, or bio"""
		terms = search_string.split()
		if len(terms) == 0: return None;

		name_query = Q(full_name__icontains=terms[0]) 
		for term in terms[1:]: name_query = name_query & Q(full_name__icontains=term)

		username_query = Q(user__username__icontains=terms[0]) 
		for term in terms[1:]: username_query = username_query & Q(user__username__icontains=term)

		location_query = Q(location__icontains=terms[0]) 
		for term in terms[1:]: location_query = location_query & Q(location__icontains=term)

		bio_query = Q(bio__icontains=terms[0]) 
		for term in terms[1:]: bio_query = bio_query & Q(bio__icontains=term)

		email_query = Q(user__email=terms[0]) 
		for term in terms[1:]: email_query = email_query & Q(user__email=term)

		return UserProfile.objects.filter(name_query | username_query | location_query | bio_query | email_query).order_by('full_name')

class UserProfile(ThumbnailedModel):
	"""Extends the django.contrib.auth User model"""
	user = models.ForeignKey(User, unique=True)
	photo = models.ForeignKey(Photo, blank=True, null=True)
	full_name = models.CharField(max_length=1024, blank=False, null=False)
	location = models.CharField(max_length=1024, blank=True, null=True, help_text="Where you are, for example 'Seattle' or 'Home'")
	bio = models.TextField(null=True, blank=True)
	url = models.URLField(verify_exists=False, null=True, blank=True, max_length=300)
	invites = models.ManyToManyField(Invite, blank=True, null=True, related_name='inviter')
	email_validated = models.BooleanField(default=False, blank=False, null=False)
	objects = UserProfileManager()
	def save(self, *args, **kwargs):
		if not self.full_name or len(self.full_name.strip()) == 0:
			self.full_name = self.user.username
		super(UserProfile, self).save(*args, **kwargs)
	def invitees(self):
		return UserProfile.objects.filter(user__origin_invites__inviter=self.user)
	def used_invites(self):
		return Invite.objects.filter(inviter=self).exclude(used_by=None)
	def available_invites(self):
		return Invite.objects.filter(inviter=self, sent_to=None)
	def send_email_validation(self):
		site = Site.objects.get_current()
		message = render_to_string('person/email/email_validation.txt', { 'site':site, 'user':self.user })
		subject = '%s email validation' % site.name
		send_mail(subject, message, None, [self.user.email], fail_silently=True)
	def validation_secret(self):
		import md5
		return md5.new('%s-%s-%s' % (self.user.username, self.user.email, self.user.id)).hexdigest()
	@models.permalink
	def get_absolute_url(self):
		return ('person.views.profile', (), { 'username':urllib.quote(self.user.username) })
	def __unicode__(self):
		return self.user.username
	class Meta:
		ordering = ['user__username']

User.get_profile = lambda self: UserProfile.objects.get_or_create(user=self)[0]

# Copyright 2010 Trevor F. Smith (http://trevor.smith.name/) Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0 Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
