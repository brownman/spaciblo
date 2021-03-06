
//
//
//  EVENTS
//
//
//

SpacibloEvents = {}

{% for event in events %}

SpacibloEvents.{{ event.event_name }} = function({% for attr in event.dict %}_{{ attr }}{% if not forloop.last %}, {% endif %}{% endfor %}){
	var self = this;
	self.type = '{{ event.event_name }}';
	{% for attr in event.dict %}self.{{ attr }} = _{{ attr }};
	{% endfor %}
	self.toJSON = function(){ return Spaciblo.stringify(self); }
}
{% endfor %}

SpacibloEvents.rehydrateEvent = function(jsonData){
	event_func = null;
	for(var key in SpacibloEvents){
		if(key == jsonData['type']){
			event_func = SpacibloEvents[key];
			break;
		}
	}
	if(event_func == null){
		console.log('Tried to rehydrate an unknown event: ' + JSON.stringify(jsonData));
		return null;
	}
	var spaciblo_event = new event_func(); // we'll just let all the parameters be undefined for the moment
	for(var key in jsonData){
		spaciblo_event[key] = jsonData[key];
	}
	return spaciblo_event;
}