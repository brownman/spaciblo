
String.prototype.length_in_bytes = function() {
    return encodeURIComponent(this).replace(/%../g, 'x').length;
};

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
	self.tagName = '{{ event.tag_name }}';
	{% for attr in event.HydrationMeta.attributes %}self.{{ attr }} = _{{ attr }};
	{% endfor %}
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

SpacibloScene.parseSceneDocument = function(xmlDoc){
	var sceneElement = xmlDoc.documentElement;
	var scene = new SpacibloScene.Scene(new SpacibloScene.Color(sceneElement.attributes['background_color'].value));
	for(var i=0; i < sceneElement.childNodes.length; i++){
		if(sceneElement.childNodes[i].tagName == 'thing'){
			scene.thing = SpacibloScene.parseThingElement(sceneElement.childNodes[i], this);
		}
	}
	return scene;
}

SpacibloScene.parseThingElement = function(thingElement, scene){
	var attrs = thingElement.attributes;
	var thing = new SpacibloScene.Thing(attrs['id'].value, new SpacibloScene.Position(attrs['position'].value), new SpacibloScene.Orientation(attrs['orientation'].value), parseFloat(attrs['scale'].value));
	if(attrs['user']){
		var u = null;
		if(scene.thing)
			u = scene.thing.getUser(attrs['user'].value);
		if(u == null)
			u = new SpacibloScene.User(attrs['user'].value);
		thing.user = u;
		console.log('thing.user: ' + thing.user);
	}
	for(var i=0; i < thingElement.childNodes.length; i++){
		if(thingElement.childNodes[i].tagName == 'children'){
			childrenElement = thingElement.childNodes[i];
			for(var j=0; j < childrenElement.childNodes.length; j++){
				if(childrenElement.childNodes[j].tagName == 'thing'){
					thing.children[thing.children.length] = SpacibloScene.parseThingElement(childrenElement.childNodes[j], scene);
				}
			}
		}
	}
	return thing;
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
// Spaciblo CometClient
//
//

Spaciblo = {}

Spaciblo.defaultOrientation = "1,0,0,0";
Spaciblo.defaultPosition = "20,20,0";

Spaciblo.WebSocketClient = function(_ws_port, _ws_host, _message_handler_function){
	var self = this;
	self.scene = null;
	self.socket = null;
	self.ws_port = _ws_port;
	self.ws_host = _ws_host;
	self.message_handler_function = _message_handler_function;
	
	self.onopen = function() { console.log('open'); }
	self.onclose = function() { console.log('close'); }
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
	
	self.handle_message = function(message) {
		event_xml = Spaciblo.parseXML(message);
		spaciblo_event = Spaciblo.rehydrateEvent(event_xml)
		switch(spaciblo_event.tagName) {
			case 'heartbeat':
				break;
			case 'usermessage':
				self.user_message_handler(spaciblo_event.username, spaciblo_event.message);
				break;
			case 'authenticationresponse':
				if(spaciblo_event.authenticated){
					self.username = spaciblo_event.username;
				} else {
					self.username = null;
					console.log("failed to authenticate");
				}
				self.finished_auth = true;
				self.authentication_handler(self.username != null);
				break;
			case 'joinspaceresponse':
				if(spaciblo_event.joined == true){
					self.scene = SpacibloScene.parseSceneDocument(Spaciblo.parseXML(spaciblo_event.scene_doc));
				}		
				self.finished_join = true;
				self.join_space_handler(spaciblo_event.joined);
				break;
			case 'thingadded':
				if(self.scene.thing.getThing(parseInt(spaciblo_event.thing_id)) != null) { break; }
				var thing = new SpacibloScene.Thing(spaciblo_event.thing_id, new SpacibloScene.Position(spaciblo_event.position), new SpacibloScene.Orientation(spaciblo_event.orientation), parseFloat(spaciblo_event.scale));
				thing.parent = self.scene.thing.getThing(parseInt(spaciblo_event.parent_id));
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
			case 'thingmoved':
				var thing = self.scene.thing.getThing(parseInt(spaciblo_event.thing_id));
				thing.position.hydrate(spaciblo_event.position);
				thing.orientation.hydrate(spaciblo_event.orientation);
				self.suggest_render_handler();
				break;
			default:
				console.log("Received an unknown event: " + Spaciblo.serializeXML(event_xml.documentElement));
		}
	}

	self.ws_client = new Spaciblo.WebSocketClient(9876, '127.0.0.1', self.handle_message);

	self.open = function() {
		self.ws_client.onopen = self.__open;
		self.ws_client.onclose = self.__close;
		self.ws_client.open();
	}

	self.sendEvent = function(event){
		self.ws_client.send(Spaciblo.quickXMLString(event));
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
	
	self.addAvatar = function(position, orientation) {
		var avatarThing = self.scene.thing.getUserThing(self.username)
		if(avatarThing == null){
			self.sendEvent(new SpacibloEvents.AddAvatarRequest(self.space_id, self.username, position, orientation));
		}
	}
	
	self.sendUserMessage = function(message){
		self.sendEvent(new SpacibloEvents.UserMessage(self.space_id, self.username, message));
	}
	
	self.close = function() {
		self.ws_client.close();
	}
	
	self.__open = function(){
		console.log('open');
		self.open_handler();
	}
	self.__close = function(){
		console.log('close');
		self.close_handler();
	}
	
}

Spaciblo.rehydrateEvent = function(xmlDoc){
	event_func = null;
	for(key in SpacibloEvents){
		if(key.toLowerCase() == xmlDoc.documentElement.tagName){
			event_func = SpacibloEvents[key];
			break;
		}
	}
	if(event_func == null){
		console.log('Tried to rehydrate an unknown event: ' + xmlDoc.documentElement.tagName);
		return null;
	}
	var spaciblo_event = new event_func(); // we'll just let all the parameters be undefined for the moment
	var attributes = xmlDoc.documentElement.attributes;
	for (var i = 0; i < attributes.length; i++){
		if(attributes.item(i).value == "True"){
			spaciblo_event[attributes.item(i).name] = true;
		} else if (attributes.item(i).value == "False"){
			spaciblo_event[attributes.item(i).name] = false;
		} else {
			spaciblo_event[attributes.item(i).name] = attributes.item(i).value;
		}
	}
	return spaciblo_event;
}

Spaciblo.quickXMLString = function(dictionary){
	return Spaciblo.serializeXML(Spaciblo.quickXML(dictionary).documentElement);
}

Spaciblo.quickXML = function(dictionary){
	xml = Spaciblo.parseXML('<' + dictionary['tagName'] + '/>');
	for(var i in dictionary){
		if(i == 'tagName') continue;
		xml.documentElement.setAttribute(i, dictionary[i])
	}
	return xml
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


Spaciblo.parseXML = function(xml) {
	if (window.ActiveXObject) {
		xmlDoc=new ActiveXObject("Microsoft.XMLDOM");
		xmlDoc.async="false";
		xmlDoc.loadXML(xml);
		return xmlDoc;
	} else if (document.implementation && document.implementation.createDocument) {
		parser=new DOMParser();
		xmlDoc=parser.parseFromString(xml, "text/xml");
		return xmlDoc;
	}
}

Spaciblo.serializeXML = function(xml){
	var result = "<" + xml.tagName.toLowerCase();

	var attributes = xml.attributes;
	for (var i = 0; i < attributes.length; i++){
		if(attributes.item(i).value == null || attributes.item(i).value == "null"){
			continue;
		}
	   result += " " + attributes.item(i).name.toLowerCase() + "='" + Spaciblo.escapeHTML(attributes.item(i).value) + "'";
	}
	var hasText = (typeof xml.text != "undefined") && xml.text.length != 0;
	
	if(!hasText && xml.childNodes.length == 0){
		result += " />";
		
		return result;
	} else {
		result += ">";
	}

	if(hasText){
		result += xml.text;
	}
	
	for(var i = 0; i < xml.childNodes.length; i++){
		if(xml.childNodes[i].nodeType == 3){
			if(!hasText){
				result += Spaciblo.escapeHTML(xml.childNodes[i].nodeValue)
			}
			continue;
		}
		result += Spaciblo.serializeXML(xml.childNodes[i]);
	}
	result += "</" + xml.tagName.toLowerCase() + ">";
	return result;
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

SpacibloInput = {}

SpacibloInput.InputManager = function(_space_client){
	var self = this;
	self.space_client = _space_client;
	self.avatar_thing = null;
	self.x_delta = 1;
	self.y_delta = 1;
	self.z_delta = 1;
	self.y_rot_delta = Math.PI / 8.0;
	self.getAvatarThing = function(){
		if(self.avatar_thing == null){
			self.avatar_thing = self.space_client.scene.thing.getUserThing(self.space_client.username);
		}
		return self.avatar_thing;
	}
	
	self.handle_keydown = function(event){
		var avatarThing = self.getAvatarThing();
		switch(event.keyCode){
			case 37: //left arrow
			case 65: //a key
				avatarThing.position.x -= self.x_delta;
				break;
			case 38: //up arrow
			case 87: //w key
				avatarThing.position.z -= self.z_delta;
				break;
			case 39: //right
			case 68: //d key
				avatarThing.position.x += self.x_delta;
				break;
			case 40: //down
			case 83: //s key
				avatarThing.position.z += self.z_delta;
				break;
			case 81: //q key
				avatarThing.orientation.rotateEuler(0, self.y_rot_delta, 0);
				break;
			case 69: //e key
				avatarThing.orientation.rotateEuler(0, -1 * self.y_rot_delta, 0);
				break;
			default:
				return;
		}
		var event = new SpacibloEvents.AvatarMoveRequest(self.space_client.space_id, self.space_client.username, avatarThing.position.toString(), avatarThing.orientation.toString());
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
		//--Initialize WebGLU, shaders
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
		var avatarThing = self.scene.thing.getUserThing(self.username);
		//TODO this is wrong
		if(avatarThing != null){
			$W.camera.setPosition(avatarThing.position.x, avatarThing.position.y, avatarThing.position.z);
			$W.camera.setRotation([avatarThing.orientation.getEuler()[0], avatarThing.orientation.getEuler()[1], avatarThing.orientation.getEuler()[2]]);
		} else {
			//console.log('no avatar thing');
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