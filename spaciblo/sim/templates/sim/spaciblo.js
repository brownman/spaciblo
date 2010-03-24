
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

{% include "sim/scene.js" %}

{% include "sim/models.js" %}

{% include "sim/input.js" %}

{% include "sim/renderer.js" %}

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


Spaciblo.defaultOrientation = "1,0,0,0";
Spaciblo.defaultPosition = "0,0,10";

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

Spaciblo.SpaceClient = function(space_id, canvas) {
	var self = this;
	self.space_id = space_id;
	self.canvas = canvas;
	
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
					self.scene = SpacibloScene.parseSceneDocument(spaciblo_event.scene_doc);
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

