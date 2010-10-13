
// If there is no console, ignore console logging
if(!window.console){
    var names = ["log", "debug", "info", "warn", "error", "assert", "dir", "dirxml", "group", "groupEnd", "time", "timeEnd", "count", "trace", "profile", "profileEnd"];
    window.console = {};
    for (var i = 0; i < names.length; ++i){ 
        window.console[names[i]] = function() {}
    }
}

String.prototype.endsWith = function(str){ return (this.match(str+"$")==str) }

{% include "sim/events.js" %}

{% include "sim/models.js" %}

{% include "sim/input.js" %}

{% include "sim/scene.js" %}

{% include "sim/renderer.js" %}

//
//
// Spaciblo
//
//

Spaciblo = {}

Spaciblo.stringify = function(hydrateObj){
	var data = { 'type': hydrateObj.type }
	for(var key in hydrateObj){
		if(key == 'type' || key == 'toJSON') continue;
		data[key] = hydrateObj[key];
	}
	return JSON.stringify(data);
}


Spaciblo.defaultRotation = [1.56, 0, 0];
Spaciblo.defaultPosition = [0.1, 0.1, 0.1];

Spaciblo.WebSocketClient = function(_ws_port, _ws_host, _message_handler_function){
	var self = this;
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

Spaciblo.SpaceClient = function(space_id, canvas) {
	var self = this;
	self.space_id = space_id;
	self.canvas = canvas;
	
	self.username = null;
	self.finished_auth = false;
	self.finished_join = false;
	self.sceneJson = null;
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
		spaciblo_event = SpacibloEvents.rehydrateEvent(JSON.parse(message));
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
					self.sceneJson = JSON.parse(spaciblo_event.scene_doc);
				}		
				self.finished_join = true;
				self.join_space_handler(spaciblo_event.joined);
				break;
			case 'NodeAdded':
				var nodeJson = JSON.parse(spaciblo_event.json_data);
				if(self.scene.getNode(nodeJson.uid)){
					console.log("Tried to add a duplicate node: " + nodeJson.uid);
					break;
				}
				var renderable = new SpacibloRenderer.Renderable(self, nodeJson.uid);
				renderable.init(nodeJson);
				if(nodeJson.username) renderable.username = nodeJson.username;
				self.scene.addChild(renderable);
				break;
			case 'PlaceableMoved':
				console.log('TODO placeable moved');
				console.log(spaciblo_event);
				var node = self.scene.getNode(spaciblo_event.uid);
				if(node){
					node.setLoc(spaciblo_event.position[0], spaciblo_event.position[1], spaciblo_event.position[2]);
					node.setQuat(spaciblo_event.orientation[0], spaciblo_event.orientation[1], spaciblo_event.orientation[2], spaciblo_event.orientation[3]);
					console.log(node);
				} else {
					console.log("Tried to move an unknown node: " + spaciblo_event.uid);
				}
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
	
	self.addUser = function(position, orientation) {
		if(self.scene.getUserGroup(self.username) != null) return;
		self.sendEvent(new SpacibloEvents.AddUserRequest(self.username, position, self.space_id, orientation));
	}
	
	self.sendUserMessage = function(message){
		self.sendEvent(new SpacibloEvents.UserMessage(self.username, self.space_id, message));
	}
	
	self.close = function() {
		self.ws_client.close();
	}
	
	self.__open = function(){
		//console.log('Space client opened');
		self.open_handler();
	}
	self.__close = function(){
		console.log('Space client closed');
		self.close_handler();
	}
	
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

