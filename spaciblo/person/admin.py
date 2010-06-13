from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

from models import *

 
class StyledAdmin(admin.ModelAdmin):
	save_on_top=True
	class Media:
		css = { "all": ('admin.css', )}

class PhotoAdmin(StyledAdmin):
	list_display = ('image', 'thumb')
admin.site.register(Photo, PhotoAdmin)

class InviteRequestAdmin(StyledAdmin):
	list_display = ('email', 'created')
admin.site.register(InviteRequest, InviteRequestAdmin)

class UserProfileAdmin(StyledAdmin):
	list_display = ('user', 'full_name', 'thumb')
	raw_id_fields = ('user', 'photo', 'invites')
#admin.site.register(UserProfile, UserProfileAdmin)
# commented out because we use the UserAndProfileAdmin instead

class UserProfileInline(admin.StackedInline):
	raw_id_fields = ('user', 'photo', 'invites')
	model = UserProfile

class UserAndProfileAdmin(UserAdmin):
	inlines = [UserProfileInline] 
admin.site.unregister(User)
admin.site.register(User, UserAndProfileAdmin)

class InviteAdmin(StyledAdmin):
	list_display = ('id', 'sent_to', 'used_by', 'created')
admin.site.register(Invite, InviteAdmin)

# Copyright 2010 Trevor F. Smith (http://trevor.smith.name/) Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0 Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
