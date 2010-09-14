//
//
// Models
//
//
SpacibloModels = {}
{% for model in models %}
SpacibloModels.{{ model.type }} = function({% for attr in model.dict %}{{ attr }}{% if not forloop.last %}, {% endif %}{% endfor %}){
	var self = this;
	self.type = '{{ model.type }}';
	{% for attr in model.dict %}self.{{ attr }} = {{ attr }};
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
	
	for(var key in jsonData) model[key] = jsonData[key];
	return model;
}
