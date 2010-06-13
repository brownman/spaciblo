from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from django.core import mail
from django.core.urlresolvers import reverse

class BasicViewsTest(TestCase):
	fixtures = ["auth.json", "person.json", "sites.json", "space.json", "front.json", "tagging.json"]
	
	def setUp(self):
		self.client = Client()

	def tearDown(self):
		pass

	def test_email_validation(self):
		user = User.objects.get(username='trevor_smith')
		profile = user.get_profile()
		self.assertTrue(profile.email_validated)
		url = reverse('person.views.email_validate', kwargs={ 'username':user.username, 'secret':profile.validation_secret() })
		self.failUnlessEqual(self.client.get(url).status_code, 200)
		user = User.objects.get(username='trevor_smith')
		self.assertTrue(user.get_profile().email_validated)
		profile = user.get_profile()
		profile.email_validated = False
		profile.save()
		self.failUnlessEqual(self.client.get(url).status_code, 200)
		user = User.objects.get(username='trevor_smith')
		self.assertTrue(user.get_profile().email_validated)
		

	def test_registration(self):
		url = '/person/register/'

		self.failIf(self.client.login(username="gronkle_stiltskin", password="98562"))

		self.client = Client()
		self.failUnlessEqual(self.client.get(url).status_code, 200)
		response = self.client.post(url, { 'username':'gronkle_stiltskin', 'password1':'98562', 'password2':'98562', 'email':'schlub@inkbbl.com', 'full_name':'Schlub', 'tos':'true' })
		self.failUnlessEqual(response.status_code, 302) # redirected to profile upon successful registration
		self.failUnlessEqual(self.client.get('/timeline/').status_code, 200) # will redirect to login unless client is authed

		self.assertEquals(len(mail.outbox), 1)
		self.assertTrue(mail.outbox[0].subject.endswith(' email validation'))
		
		self.client = Client()
		self.failUnless(self.client.login(username="gronkle_stiltskin", password="98562"))
		
		self.client = Client()
		response = self.client.post(url, { 'username':'gronkle_stiltskin', 'password1':'98562', 'password2':'98562', 'email':'schlub2@inkbbl.com', 'full_name':'Schlub', 'tos':'true' })
		self.failUnlessEqual(response.status_code, 200) # should not redirect because the username is a duplicate
		response = self.client.post(url, { 'username':'gronkle_stiltskin2', 'password1':'98562', 'password2':'98562', 'email':'schlub@inkbbl.com', 'full_name':'Schlub', 'tos':'true' })
		self.failUnlessEqual(response.status_code, 200) # should not redirect because the email is a duplicate
		response = self.client.post(url, { 'username':'gronkle_stiltskin2', 'password1':'98562', 'password2':'98562', 'email':'schlub2@inkbbl.com', 'full_name':'Schlub' })
		self.failUnlessEqual(response.status_code, 200) # should not redirect because the tos is not accepted
		
	def test_basic_views(self):
		public_urls = ['/person/trevor_smith/', '/person/register/']
		private_urls = []
		for url in public_urls:
			self.failUnlessEqual(self.client.get(url).status_code, 200, 'failed on url %s' % url)
		for url in private_urls:
			self.failUnlessEqual(self.client.get(url).status_code, 302, 'failed on url %s' % url)
		self.failUnless(self.client.login(username="trevor_smith", password="1234"))
		for url in private_urls:
			self.failUnlessEqual(self.client.get(url).status_code, 200, 'failed on url %s' % url)
		
# Copyright 2010 Trevor F. Smith (http://trevor.smith.name/) Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0 Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

