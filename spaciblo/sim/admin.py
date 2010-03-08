from django.contrib import admin
from django import forms
from django.forms.util import ErrorList

from spaciblo.sim.models import *

class BaseMedia:
		css = { "all": ('sim/css/admin.css', )}

class SpaceMemberInline(admin.TabularInline):
    model = SpaceMember

class SpaceAdmin(admin.ModelAdmin):
	inlines = [ SpaceMemberInline ]
	class Media(BaseMedia):
		pass
admin.site.register(Space, SpaceAdmin)

class AssetAdmin(admin.ModelAdmin):
	class Media(BaseMedia):
		pass
admin.site.register(Asset, AssetAdmin)

class TemplateAssetAdmin(admin.ModelAdmin):
	class Media(BaseMedia):
		pass
admin.site.register(TemplateAsset, TemplateAssetAdmin)

class TemplateSettingAdmin(admin.ModelAdmin):
	class Media(BaseMedia):
		pass
admin.site.register(TemplateSetting, TemplateSettingAdmin)

class TemplateChildAdmin(admin.ModelAdmin):
	class Media(BaseMedia):
		pass
admin.site.register(TemplateChild, TemplateChildAdmin)

class TemplateAssetInline(admin.TabularInline):
	model = TemplateAsset
	
class TemplateAdmin(admin.ModelAdmin):
	inlines = [TemplateAssetInline]
	class Media(BaseMedia):
		pass
admin.site.register(Template, TemplateAdmin)

# Copyright 2010 Trevor F. Smith (http://trevor.smith.name/) Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0 Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
