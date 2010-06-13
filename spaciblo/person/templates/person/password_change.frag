{% load imagetags %}
<table>
<form id="password-change-form" action="./#change-password" method="post">
{{ password_change_form }}
<tr>
	<td colspan="2" style="text-align: right;">
		<input type="hidden" name="password_change_form" value="True" />
		<input type="submit" value="change your password" />
	</td>
</tr>
</form>
</table>
