SpacibloModels.{{ model.type }} = function({% for attr in model.HydrationMeta.attributes %}{{ attr }}{% if not forloop.last %}, {% endif %}{% endfor %}){
	var self = this;
	self.type = '{{ model.type }}';
	{% for attr in model.HydrationMeta.attributes %}self.{{ attr }} = {{ attr }};
	{% endfor %}
	{% for attr in model.HydrationMeta.nodes %}self.{{ attr }} = null;
	{% endfor %}
	
	self.toJSON = function(){ return Spaciblo.stringify(self); }
}