{% load imagetags %}
<div class="person-info">
		{% if profile.photo %}
		<img class="person-photo" src="{{ profile.photo.image.url|thumbnail:"150w" }}" width="150" title="{{profile.full_name}}" alt="{{ profile.full_name}}" />
		{% else %}
		<img class="person-photo" src="{{ MEDIA_URL }}BlankIcon150x150.jpg" width="150" height="150" />		
		{% endif %}
	<h2 class="vcard"><span class="fn">{{ profile.full_name }}</span></h2>
	<table>
		{% if profile.location %}
			<tr><th>Location:</th><td>{{ profile.location }}</td></tr>
		{% endif %}
		{% if profile.url %}
			<tr><th>URL:</th><td>{{ profile.url|urlize }}<td></tr>
		{% endif %}
		{% if profile.bio %}
			<tr><td colspan="2">{{ profile.bio }}</td></tr>
		{% endif %}
	</table>
	<br clear="all" />
</div>
