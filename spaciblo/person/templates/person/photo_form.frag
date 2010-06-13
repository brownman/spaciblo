{% load imagetags %}
<h3>Current Photo:</h3>
{% if profile.photo.image %}
	<img src="{{ profile.photo.image.url|thumbnail:"150w" }}" />
{% else %}
	<img src="{{ MEDIA_URL }}BlankIcon150x150.jpg" width="150" height="150" />
{% endif %}

<h3 style="margin-top: 20px;">Upload a Photo:</h3>
<h4 style="font-weight: normal;">(smaller than 1MB, JPEG, GIF, or PNG)</h4>
<form id="photo-form" enctype="multipart/form-data" action="./#edit-photo" method="post">
{% for field in photo_form %}{{ field }}{% endfor %}
<input type="hidden" name="image_form" value="True" />
<input type="submit" value="save profile image" />
</form>
