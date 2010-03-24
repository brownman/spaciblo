//
//
// Models
//
//
SpacibloModels = {}
{% for model in models %}
SpacibloModels.{{ model.type }} = function({% for attr in model.HydrationMeta.attributes %}{{ attr }}{% if not forloop.last %}, {% endif %}{% endfor %}){
	var self = this;
	self.type = '{{ model.type }}';
	{% for attr in model.HydrationMeta.attributes %}self.{{ attr }} = {{ attr }};
	{% endfor %}
	{% for attr in model.HydrationMeta.nodes %}self.{{ attr }} = null;
	{% endfor %}
	
	self.toJSON = function(){ return Spaciblo.stringify(self); }
}
{% endfor %}

SpacibloModels.rehydrateModel = function(jsonData, model){
	if(!model){
		model_func = null;
		for(var key in SpacibloModels){
			if(key == jsonData['type']){
				model_func = SpacibloModels[key];
				break;
			}
		}
		if(model_func == null){
			console.log('Tried to rehydrate an unknown model: ' + JSON.stringify(jsonData));
			return null;
		}
		model = new model_func();
	}
	
	var attributes = jsonData['attributes'];
	if(!attributes) return model;
	for(var key in attributes) model[key] = attributes[key];
	return model;
}
