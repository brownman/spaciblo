
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
	self.user_node = null;
	self.x_delta = 1;
	self.y_delta = 1;
	self.z_delta = 1;
	self.y_rot_delta = Math.PI / 24.0;
	self.getUserThing = function(){
		if(self.user_node == null){
			self.user_node = self.space_client.scene.getUserGroup(self.space_client.username);
		}
		return self.user_node;
	}
	
	self.relativeMove = function(x, y, z, userThing){
		userThing.position.x += x;
		userThing.position.y += y;
		userThing.position.z += z;
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
				self.relativeMove(-self.x_delta, 0, 0, userThing);
				break;
			case 38: //up arrow
			case 87: //w key
				self.relativeMove(0, 0, -self.z_delta, userThing);
				break;
			case 39: //right
			case 68: //d key
				self.relativeMove(self.x_delta, 0, 0, userThing);
				break;
			case 40: //down
			case 83: //s key
				self.relativeMove(0, 0, self.z_delta, userThing);
				break;
			case 82: //r key
				self.relativeMove(0, self.y_delta, 0, userThing);
				break;
			case 70: //f key
				self.relativeMove(0, -self.y_delta, 0, userThing);
				break;
			case 81: //q key
				userThing.orientation.rotateEuler(0, -1 * self.y_rot_delta, 0);
				break;
			case 69: //e key
				userThing.orientation.rotateEuler(0, self.y_rot_delta, 0);
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
