
// Ignores Firebug (http://www.getfirebug.com/) console calls for browsers without firebug
if(!window.console){
    var names = ["log", "debug", "info", "warn", "error", "assert", "dir", "dirxml", "group", "groupEnd", "time", "timeEnd", "count", "trace", "profile", "profileEnd"];
    window.console = {};
    for (var i = 0; i < names.length; ++i){ 
        window.console[names[i]] = function() {}
    }
}

String.prototype.length_in_bytes = function() {
    return encodeURIComponent(this).replace(/%../g, 'x').length;
};

String.prototype.endsWith = function(str){ return (this.match(str+"$")==str) }

//
//
//  EVENTS
//
//
//

SpacibloEvents = {}

{% for event in events %}

SpacibloEvents.{{ event.event_name }} = function({% for attr in event.HydrationMeta.attributes %}_{{ attr }}{% if not forloop.last %}, {% endif %}{% endfor %}){
	var self = this;
	self.type = '{{ event.event_name }}';
	{% for attr in event.HydrationMeta.attributes %}self.{{ attr }} = _{{ attr }};
	{% endfor %}
	
	self.toJSON = function(){ return Spaciblo.stringify(self); }
}
{% endfor %}

/* these are the automatically generated Javascript objects for the spaciblo 3D scene */

//
//
//  SCENE
//
//
//

SpacibloScene = {}

{% for cls in scene_graph_classes %}
{% if cls.HydrationMeta %}
SpacibloScene.{{ cls.node_name }} = function({% for attr in cls.HydrationMeta.attributes %}_{{ attr }}{% if not forloop.last %}, {% endif %}{% endfor %}){
	var self = this;
	{% for attr in cls.HydrationMeta.attributes %}self.{{ attr }} = _{{ attr }};
	{% endfor %}
	{% for ref in cls.HydrationMeta.ref_attributes %}self.{{ ref }} = null;
	{% endfor %}
	{% for ref in cls.HydrationMeta.nodes %}self.{{ ref }} = null;
	{% endfor %}
	{% for ref in cls.HydrationMeta.raw_nodes %}self.{{ ref }} = null;
	{% endfor %}

	if(self.init){ self.init(); }
}
{% else %}
SpacibloScene.{{ cls.node_name }} = function(_data){
	var self = this;
	self.data = _data;
	if(self.init){ self.init(); }
	
	self.hydrate = function(_data){
		this.data = _data;
		if(this.init){ this.init(); }
	}
}
{% endif %}
{% endfor %}

SpacibloScene.User = function(_username){
	var self = this;
	self.username = _username;
}

SpacibloScene.Thing.prototype.getUserThing = function(username){
	if(this.user != null && this.user.username == username){
		return this;
	}
	for(var i=0; i < this.children.length; i++){
		var t = this.children[i].getUserThing(username);
		if(t != null) return t;
	}
	return null;
}

SpacibloScene.Thing.prototype.getUser = function(username){
	var ut = this.getUserThing(username);
	if(ut != null) return ut.user;
	return null;
}

SpacibloScene.Thing.prototype.getThing = function(thing_id){
	if(this.id == thing_id){
		return this;
	}
	for(var i=0; i < this.children.length; i++){
		var t = this.children[i].getThing(thing_id);
		if(t != null) return t;
	}
	return null;
}

SpacibloScene.Thing.prototype.listThings = function(results){
	if(!results) {
		results = new Array();
	}
	results[results.length] = this;
	for(var i=0; i < this.children.length; i++)
		this.children[i].listThings(results);
	return results
}

SpacibloScene.Scene.prototype.init = function(){
	this.assetManager = null; // to be assigned when the document is parsed
}

SpacibloScene.Thing.prototype.init = function(){
	this.children = [];
}

/* These are the manual initialization functions for scene nodes */
SpacibloScene.Color.prototype.init = function(){
	this.red = parseFloat(this.data.split(",")[0]);
	this.green = parseFloat(this.data.split(",")[1]);
	this.blue = parseFloat(this.data.split(",")[2]);
	this.alpha = parseFloat(this.data.split(",")[3]);
}
SpacibloScene.Position.prototype.init = function(){
	this.x = parseFloat(this.data.split(",")[0]);
	this.y = parseFloat(this.data.split(",")[1]);
	this.z = parseFloat(this.data.split(",")[2]);
}
SpacibloScene.Orientation.prototype.init = function(){
	this.set(parseFloat(this.data.split(",")[0]), parseFloat(this.data.split(",")[1]), parseFloat(this.data.split(",")[2]), parseFloat(this.data.split(",")[3]));
}

SpacibloScene.Position.prototype.toString = function(){
	return this.x + "," + this.y + "," + this.z;
}

SpacibloScene.Orientation.prototype.toString = function(){
	return this.s + "," + this.x + "," + this.y + "," + this.z;
}

SpacibloScene.parseSceneDocument = function(sceneDoc, assetManager){
	var sceneData = JSON.parse(sceneDoc);
	var scene = new SpacibloScene.Scene(new SpacibloScene.Color(sceneData['attributes']['background_color']));
	scene.thing = SpacibloScene.parseThingData(sceneData['thing'], null, this, assetManager);
	return scene;
}

SpacibloScene.parseThingData = function(thingData, parent, scene, assetManager){
	var thing = new SpacibloScene.Thing(thingData['attributes']['id'], new SpacibloScene.Position(thingData['attributes']['position']), new SpacibloScene.Orientation(thingData['attributes']['orientation']), parseFloat(thingData['attributes']['scale']));
	thing.parent = parent;
	if(thingData['attributes']['user']){
		if(scene.thing)
			thing.user = scene.thing.getUser(thingData['attributes']['user']);
		if(!thing.user)
			thing.user = new SpacibloScene.User(thingData['attributes']['user']);
	}
	if(thingData['attributes']['template']){
		thing.template = assetManager.getOrCreateTemplate(thingData['attributes']['template']);
	}
	if(thingData['children']){
		for(var i=0; i < thingData['children'].length; i++){
			thing.children[thing.children.length] = SpacibloScene.parseThingData(thingData['children'][i], thing, scene, assetManager);
		}
	}
	return thing;
}

SpacibloScene.Geometry.prototype.hydrate = function(geoData){
	this.name = geoData['attributes']['name'];
	this.position = new SpacibloScene.Position(geoData['attributes']['position']);
	this.orientation = new SpacibloScene.Orientation(geoData['attributes']['position']);
	this.vertices = geoData['vertices'];
	this.uvs = geoData['uvs'];
	this.normals = geoData['normals'];
	if(geoData['material']){
		this.material = new SpacibloScene.Material();
		for(var key in geoData['material']['attributes']){
			this.material[key] = geoData['material']['attributes'][key];
		}
		this.material.specular = geoData['material']['specular'];
		this.material.ambient = geoData['material']['ambient'];
		this.material.diffuse = geoData['material']['diffuse'];
	}
	this.children = new Array();
	for(var i=0; geoData['children'] && i < geoData['children'].length; i++){
		this.children[i] = new SpacibloScene.Geometry();
		this.children[i].hydrate(geoData['children'][i]);
	}
}

SpacibloScene.Orientation.prototype.set = function(sValue, xValue, yValue, zValue){
	this.s = sValue;
	this.x = xValue;
	this.y = yValue;
	this.z = zValue;
	this.normalize();
}

SpacibloScene.Orientation.prototype.normalize = function(){
	var norm = (this.x * this.x + this.y * this.y + this.z * this.z + this.s * this.s);

	 if (norm > 0.0) {
	   norm = 1.0 / Math.sqrt(norm);
	   this.x *= norm;
	   this.y *= norm;
	   this.z *= norm;
	   this.s *= norm;
	 } else {
	   this.x =  0.0;
	   this.y =  0.0;
	   this.z =  0.0;
	   this.s =  0.0;
	}
}

SpacibloScene.Orientation.prototype.add = function(q1){
	this.x += q1.x;
	this.y += q1.y;
	this.z += q1.z;
	this.s += q1.s;
	this.normalize();
}

SpacibloScene.Orientation.prototype.mul = function(q1){
	var ns = this.s * q1.s - this.x * q1.x - this.y * q1.y - this.z * q1.z;
	var nx = this.s * q1.x + q1.s * this.x + this.y * q1.z - this.z * q1.y;
	var ny = this.s * q1.y + q1.s * this.y - this.x * q1.z + this.z * q1.x;
	this.z = this.s * q1.z + q1.s * this.z + this.x * q1.y - this.y * q1.x;
	this.s = ns;
	this.x = nx;
	this.y = ny;
	this.normalize();
}

SpacibloScene.Orientation.prototype.rotateEuler = function(rotX, rotY, rotZ){
	var quat = new SpacibloScene.Orientation("1,0,0,0");
	quat.setEuler(rotX, rotY, rotZ);
	this.mul(quat);
}

SpacibloScene.Orientation.prototype.toString = function(){
	return this.s + ", " + this.x + ", " + this.y + ", " + this.z;
}

SpacibloScene.Orientation.prototype.setEuler = function(rotX, rotY, rotZ){
	var c1 = Math.cos(rotY / 2);
    var c2 = Math.cos(rotX / 2);
    var c3 = Math.cos(rotZ / 2);
    var s1 = Math.sin(rotY / 2);
    var s2 = Math.sin(rotX / 2);
    var s3 = Math.sin(rotZ / 2);
    
	this.s = (c1 * c2 * c3) - (s1 * s2 * s3);
	this.x = (s1 * s2 * c3) + (c1 * c2 * s3);
	this.y = (s1 * c2 * c3) + (c1 * s2 * s3);
	this.z = (c1 * s2 * c3) - (s1 * c2 * s3);
	this.normalize();
}

SpacibloScene.Orientation.prototype.getEuler = function(){
	var heading = 0;
	var attitude = 0;
	var bank = 0;
	if(this.x * this.y + this.z * this.s == 0.5){ //North Pole
		attitude = Math.PI / 2;
		bank = 0;
		heading = 2 * Math.atan2(this.x, this.s);
	} else if (this.x * this.y + this.z * this.s == -0.5) { // South Pole
		attitude = -Math.PI / 2;
		heading = -2 * Math.atan2(this.x, this.s)
		bank = 0;
	} else {
		heading = Math.atan2(2 * this.y * this.s - 2 * this.x * this.z, 1 - 2 * (this.y * this.y) - 2 * (this.z * this.z)) % (2 * Math.PI);
		attitude = Math.asin(2 * this.x * this.y + 2 * this.z * this.s) % (2 * Math.PI);
		bank = Math.atan2(2 * this.x * this.s - 2 * this.y * this.z , 1 - 2 * (this.x * this.x) - 2 * (this.z * this.z)) % (2 * Math.PI);
	}
	return new Array(this.cleanRotation(attitude), this.cleanRotation(heading), this.cleanRotation(bank));
}

SpacibloScene.Orientation.prototype.cleanRotation = function(rotation){ //in radians
	while(rotation < 0){
		rotation += 2 * Math.PI;
	}
	while(rotation >= 2 * Math.PI){
		rotation -= 2 * Math.PI;
	}
	if(rotation < 0.0001){
		return 0;
	}
	return rotation.toFixed(4);
}

//
//
// Models
//
//
SpacibloModels = {}
{% for model in models %}
{% include "sim/model_js.frag" %}
{% endfor %}

//
//
// Spaciblo
//
//

Spaciblo = {}

Spaciblo.stringify = function(hydrateObj){
	var attrs = {};
	for(var key in hydrateObj){
		if(key == 'type' || key == 'toJSON') continue;
		attrs[key] = hydrateObj[key];
	}
	var data = { 'type': hydrateObj.type, 'attributes':attrs };
	return JSON.stringify(data);
}

Spaciblo.rehydrateModel = function(jsonData, model){
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

Spaciblo.defaultOrientation = "1,0,0,0";
Spaciblo.defaultPosition = "20,20,0";

Spaciblo.WebSocketClient = function(_ws_port, _ws_host, _message_handler_function){
	var self = this;
	self.scene = null;
	self.socket = null;
	self.ws_port = _ws_port;
	self.ws_host = _ws_host;
	self.message_handler_function = _message_handler_function;
	
	self.onopen = function() { }
	self.onclose = function() { }
	self.onmessage = function(message) { 
		self.message_handler_function(message.data);
	}
	
	self.open = function(){
		try {
			self.socket = new WebSocket("ws://" + self.ws_host + ":" + self.ws_port + "/");
			self.socket.onopen = self.onopen;
			self.socket.onclose = self.onclose;
			self.socket.onmessage = self.onmessage;
		} catch (error) {
			console.log('Err ' + error)
		}
	}
	
	self.send = function(message){
		try {
			self.socket.send(message)
		} catch (error) {
			console.log('Err ' + error)
		}
	}
	
	self.close = function(){
		self.socket.close()
	}
}

Spaciblo.SpaceClient = function(space_id) {
	var self = this;
	self.space_id = space_id;
	self.username = null;
	self.finished_auth = false;
	self.finished_join = false;
	self.scene = null;

	// set these to receive callbacks on various events
	self.open_handler = function() {}
	self.close_handler = function(){}
	self.authentication_handler = function(successful) {}
	self.join_space_handler = function(successful) {}
	self.user_message_handler = function(username, message) {}
	self.suggest_render_handler = function(){}
	self.close_handler = function(){}
	self.handleIncomingImage = function(image, path){ }
	self.handleIncomingTemplate = function(template){ }
	self.handleIncomingGeometry = function(templateID, templateAssetID, geometry){ }

	self.assetManager = new Spaciblo.AssetManager(self.handleIncomingImage, self.handleIncomingTemplate, self.handleIncomingGeometry);
	
	self.handle_message = function(message) {
		spaciblo_event = Spaciblo.rehydrateEvent(JSON.parse(message));
		switch(spaciblo_event.type) {
			case 'Heartbeat':
				break;
			case 'UserMessage':
				self.user_message_handler(spaciblo_event.username, spaciblo_event.message);
				break;
			case 'AuthenticationResponse':
				if(spaciblo_event.authenticated){
					self.username = spaciblo_event.username;
				} else {
					self.username = null;
					console.log("failed to authenticate");
				}
				self.finished_auth = true;
				self.authentication_handler(self.username != null);
				break;
			case 'JoinSpaceResponse':
				if(spaciblo_event.joined == true){
					self.scene = SpacibloScene.parseSceneDocument(spaciblo_event.scene_doc, self.assetManager);
					self.scene.assetManager = self.assetManager;
				}		
				self.finished_join = true;
				self.join_space_handler(spaciblo_event.joined);
				break;
			case 'ThingAdded':
				if(self.scene.thing.getThing(spaciblo_event.thing_id) != null) {
					console.log("Tried to add a duplicate thing id: " + spaciblo_event.thing_id);
					break;
				}
				var thing = new SpacibloScene.Thing(spaciblo_event.thing_id, new SpacibloScene.Position(spaciblo_event.position), new SpacibloScene.Orientation(spaciblo_event.orientation), parseFloat(spaciblo_event.scale));
				thing.parent = self.scene.thing.getThing(spaciblo_event.parent_id);
				thing.parent.children[thing.parent.children.length] = thing;
				if(spaciblo_event.username){
					var user = self.scene.thing.getUser(spaciblo_event.username);
					if(user == null){
						user = new SpacibloScene.User(spaciblo_event.username);
					}
					thing.user = user;
				}
				self.suggest_render_handler();
				break;
			case 'ThingMoved':
				var thing = self.scene.thing.getThing(spaciblo_event.thing_id);
				thing.position.hydrate(spaciblo_event.position);
				thing.orientation.hydrate(spaciblo_event.orientation);
				self.suggest_render_handler();
				break;
			default:
				console.log("Received an unknown event: " + message);
		}
	}

	self.ws_client = new Spaciblo.WebSocketClient(9876, document.location.hostname, self.handle_message);

	self.open = function() {
		self.ws_client.onopen = self.__open;
		self.ws_client.onclose = self.__close;
		self.ws_client.open();
	}

	self.sendEvent = function(event){
		self.ws_client.send(event.toJSON());
	}

	self.authenticate = function() {
		var cookie = Spaciblo.getSessionCookie();
		if(cookie == null || cookie == '') return false;
		self.sendEvent(new SpacibloEvents.AuthenticationRequest(cookie));
		return true;
	}
	
	self.joinSpace = function() {
		self.sendEvent(new SpacibloEvents.JoinSpaceRequest(self.space_id));
	}
	
	self.addUserThing = function(position, orientation) {
		var userThing = self.scene.thing.getUserThing(self.username)
		if(userThing == null){
			self.sendEvent(new SpacibloEvents.AddUserThingRequest(self.space_id, self.username, position, orientation));
		}
	}
	
	self.sendUserMessage = function(message){
		self.sendEvent(new SpacibloEvents.UserMessage(self.space_id, self.username, message));
	}
	
	self.close = function() {
		self.ws_client.close();
	}
	
	self.__open = function(){
		console.log('Space client opened');
		self.open_handler();
	}
	self.__close = function(){
		console.log('Space client closed');
		self.close_handler();
	}
	
}

//
//
// AssetManager
//
//
//

Spaciblo.AssetManager = function(imageCallback, templateCallback, geometryCallback){
	// This handles loading and unloading asset resources like images and geometry
	var self = this;
	self.imageCallback = imageCallback;
	self.templateCallback = templateCallback;
	self.geometryCallback = geometryCallback;
	self.images = {};
	self.templates = {};
	self.geometries = {};
	
	self.getOrCreateTemplate = function(template_id){
		var template = self.getTemplate(template_id);
		if(template) return template;
		self.templates[template_id] = new SpacibloModels.Template(template_id);
		$.ajax({ 
			type: "GET",
			url: "/api/sim/template/" + template_id,
			dataType: "json",
			success: self.templateLoaded
		});
		return self.templates[template_id];
	}

	self.getTemplate = function(template_id){
		var template = self.templates[template_id];
		if(!template) return null;
		return template;
	}
	
	self.templateLoaded = function(jsonData){
		var template = self.getTemplate(jsonData['attributes']['id']);
		if(!template){
			console.log("Received template data for an unloaded template: " + jsonData['attributes']['id']);
			return;
		}
		Spaciblo.rehydrateModel(jsonData, template);
		template.templateAssets = []
		if(jsonData['templateassets']){
			for(var i=0; i < jsonData['templateassets'].length; i++){
				var templateAsset = new SpacibloModels.TemplateAsset();
				Spaciblo.rehydrateModel(jsonData['templateassets'][i], templateAsset);
				templateAsset.asset = new SpacibloModels.Asset();
				Spaciblo.rehydrateModel(jsonData['templateassets'][i].asset, templateAsset.asset);
				if(templateAsset.asset.type == 'texture'){
					//TODO stop consing these URIs from scratch
					self.loadImage('/api/sim/template/' + template.id + '/asset/' + templateAsset.key);
				} else if (templateAsset.asset.type == 'geometry' && templateAsset.key.endsWith('.obj')){
					self.loadGeometry(template.id, templateAsset.id, '/api/sim/template/' + template.id + '/asset/' + templateAsset.key);
				}
				template.templateAssets[i] = templateAsset;
			}
		}
		if (self.templateCallback) self.templateCallback(template);
	}

	self.loadGeometry = function(templateID, templateAssetID, path){
		if(self.geometries[templateAssetID]) return;
		self.geometries[templateAssetID] = new SpacibloScene.Geometry();
		$.ajax({ 
			type: "GET",
			url: path,
			dataType: "json",
			success: self.geometryLoaded,
			error:self.geometryErrored,
			beforeSend: function(request){ request.templateAssetID = templateAssetID; request.templateID = templateID}
		});
	}

	self.geometryErrored = function(request, status, error){
		if (self.geometryCallback) self.geometryCallback(request.templateID, request.templateAssetID, null);
	}

	self.geometryLoaded = function(jsonData, status, request){
		self.geometries[request.templateAssetID].hydrate(jsonData);
		if (self.geometryCallback) self.geometryCallback(request.templateID, request.templateAssetID, self.geometries[request.templateAssetID]);
	}

	self.imageLoaded = function(image, path){
		self.images[path] = {'path':path, 'image':image};
		if(self.imageCallback) self.imageCallback(image, path);
	}

	self.imageErrored = function(path){
		self.images[path] = {'path':path, 'image':null};
		if(self.imageCallback) self.imageCallback(null, path);
	}
	
	self.getImage = function(path){
		var image_info = self.images[path];
		if(image_info) return image_info['image'];
		return null;
	}
	
	self.loadImage = function(path){
		var image = self.getImage(path);
		if(image) return image;
		image = new Image();
		image.onerror = function() { self.imageErrored(path); };
		image.onload = function() {	self.imageLoaded(image, path); };
		image.src = path;
		return null;
	}
}

Spaciblo.rehydrateEvent = function(jsonData){
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
	var attributes = jsonData['attributes'];
	for(var key in attributes){
		spaciblo_event[key] = attributes[key];
	}
	return spaciblo_event;
}

Spaciblo.escapeHTML = function(xml){
	if(xml == null || xml.length == 0){
		return xml;
	}
    return xml.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&apos;");
}

Spaciblo.unescapeHTML = function(xml){
    return xml.replace(/&apos;/g,"'").replace(/&quot;/g,"\"").replace(/&gt;/g,">").replace(/&lt;/g,"<").replace(/&amp;/g,"&");
}

Spaciblo.getSessionCookie = function(){
 return Spaciblo.getCookie('sessionid');
}

Spaciblo.getCookie = function(name) {
    var dc = document.cookie;
    var prefix = name + "=";
    var begin = dc.indexOf("; " + prefix);
    if (begin == -1) {
        begin = dc.indexOf(prefix);
        if (begin != 0) return null;
    } else {
        begin += 2;
    }
    var end = document.cookie.indexOf(";", begin);
    if (end == -1) {
        end = dc.length;
    }
    return Spaciblo.unescapeHTML(dc.substring(begin + prefix.length, end));
}

// sets up all the url parameters in a dictionary
Spaciblo.parseLocationParameters = function(){
    	var paramPhrases = location.search.substring(1, location.search.length).split("&");
    	var paramDict = new Object();
    	for(var i=0; i < paramPhrases.length; i++){
    		paramDict[paramPhrases[i].split("=")[0]] = paramPhrases[i].split("=")[1];
	}
	return paramDict;
}

Spaciblo.locationParameters = Spaciblo.parseLocationParameters();

//
//
// SpacibloInput
//
//
//

SpacibloInput = {}

SpacibloInput.InputManager = function(_space_client){
	var self = this;
	self.space_client = _space_client;
	self.user_thing = null;
	self.x_delta = 1;
	self.y_delta = 1;
	self.z_delta = 1;
	self.y_rot_delta = Math.PI / 8.0;
	self.getUserThing = function(){
		if(self.user_thing == null){
			self.user_thing = self.space_client.scene.thing.getUserThing(self.space_client.username);
		}
		return self.user_thing;
	}
	
	self.handle_keydown = function(event){
		var userThing = self.getUserThing();
		if(userThing == null){
			console.log('No user thing');
			return;
		}
		switch(event.keyCode){
			case 37: //left arrow
			case 65: //a key
				userThing.position.x -= self.x_delta;
				break;
			case 38: //up arrow
			case 87: //w key
				userThing.position.z -= self.z_delta;
				break;
			case 39: //right
			case 68: //d key
				userThing.position.x += self.x_delta;
				break;
			case 40: //down
			case 83: //s key
				userThing.position.z += self.z_delta;
				break;
			case 81: //q key
				userThing.orientation.rotateEuler(0, self.y_rot_delta, 0);
				break;
			case 69: //e key
				userThing.orientation.rotateEuler(0, -1 * self.y_rot_delta, 0);
				break;
			default:
				return;
		}
		var event = new SpacibloEvents.UserThingMoveRequest(self.space_client.space_id, self.space_client.username, userThing.position.toString(), userThing.orientation.toString());
		self.space_client.sendEvent(event);
	}
	
	self.handle_keyup = function(event){
		return false;
	}

	self.add_event_source = function(node){
		$(node).keydown(self.handle_keydown).keyup(self.handle_keyup);
	}
}

//
//
// SPACIBLO RENDERER
//
//

SpacibloRenderer = {}

SpacibloRenderer.Renderable = function(_canvas, _thing){
	var VERTEX = "vertex";
	var COLOR  = "color";
	var NORMAL = "normal";
	var TEX_COORD = "texCoord";

	var self = this;
	self.canvas = _canvas;
	self.thing = _thing;
	self.children = [];
	
	self.glObj = new $W.Object($W.GL.TRIANGLES);
	self.glObj.setShaderProgram('textured');
	self.glObj.setTexture('check', 'sampler');
	var cubeData = $W.constants.unitCube;
	self.glObj.fillArray(VERTEX, cubeData.vertices);
	self.glObj.fillArray(NORMAL, cubeData.normals);
	self.glObj.fillArray(TEX_COORD, cubeData.texCoords);
	self.glObj.setElements(cubeData.indices);
	self.glObj.setPosition(self.thing.position.x, self.thing.position.y, self.thing.position.z);
	for(var index=0; index < self.thing.children.length; index++){
		var childRenderable = new SpacibloRenderer.Renderable(self.canvas, self.thing.children[index]);
		self.glObj.addChild(childRenderable.glObj);
		self.children[self.children.length] = childRenderable;
	}
}

SpacibloRenderer.Canvas = function(_canvas_id, _scene, _username){
	var self = this;
	self.canvas_id = _canvas_id;
	self.scene = _scene;
	self.username = _username;
	self.canvas = document.getElementById(self.canvas_id);

	self.initializeCanvas = function() {
		// This is just junk, placeholder code
		if (!$W.initialize(self.canvas)) return false;
		$W.newProgram('textured');
		$W.programs['textured'].attachShader('texVS', $W.paths.shaders + 'texture.vert');
		$W.programs['textured'].attachShader('texFS', $W.paths.shaders + 'texture.frag');
		$W.GL.clearColor(self.scene.background_color.red, self.scene.background_color.green, self.scene.background_color.blue, 1.0);
		$W.camera.yfov = 20;

		new $W.texture.Image('check', '/media/webglu/examples/keyframe/check.png');
		new $W.texture.Image('tiger', '/media/webglu/examples/texture/tiger.png');

	    return true;
	}

	self.render = function() {
		var userThing = self.scene.thing.getUserThing(self.username);
		//TODO this is wrong
		if(userThing != null){
			$W.camera.setPosition(userThing.position.x, userThing.position.y, userThing.position.z);
			$W.camera.setRotation([userThing.orientation.getEuler()[0], userThing.orientation.getEuler()[1], userThing.orientation.getEuler()[2]]);
		} else {
			//console.log('no user thing');
		}
		
		$W.update();
		$W.draw();	
	}

	self.close = function(){
		// TODO make some indication that the connection has closed
	}

	self.initializeCanvas();
	self.renderables = [new SpacibloRenderer.Renderable(self, self.scene.thing)];

    $G.initialize();
}