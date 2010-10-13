
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
	
	self.getUserNode = function(){
		if(self.user_node == null){
			self.user_node = self.space_client.scene.getUserGroup(self.space_client.username);
		}
		return self.user_node;
	}
	
	self.relativeMove = function(x, y, z, userNode){
		userNode.setLoc(userNode.locX + x, userNode.locY + y, userNode.locZ + z);
		self.space_client.scene.camera.setLoc(userNode.locX + x, userNode.locY + y, userNode.locZ + z);
	}
	
	self.handle_keydown = function(event){
		var userNode = self.getUserNode();
		if(userNode == null){
			console.log('No user thing');
			return;
		}
		switch(event.keyCode){
			case 37: //left arrow
			case 65: //a key
				self.relativeMove(-self.x_delta, 0, 0, userNode);
				break;
			case 38: //up arrow
			case 87: //w key
				self.relativeMove(0, self.y_delta, 0, userNode);
				break;
			case 39: //right
			case 68: //d key
				self.relativeMove(self.x_delta, 0, 0, userNode);
				break;
			case 40: //down
			case 83: //s key
				self.relativeMove(0, -self.y_delta, 0, userNode);
				break;
			case 82: //r key
				self.relativeMove(0, 0, self.z_delta, userNode);
				break;
			case 70: //f key
				self.relativeMove(0, 0, -self.z_delta, userNode);
				break;
			case 81: //q key
				userNode.orientation.rotateEuler(0, -1 * self.y_rot_delta, 0);
				break;
			case 69: //e key
				userNode.orientation.rotateEuler(0, self.y_rot_delta, 0);
				break;
			default:
				return;
		}
		var event = new SpacibloEvents.UserMoveRequest(self.space_client.username, [userNode.locX, userNode.locY, userNode.locZ], self.space_client.space_id, [userNode.quatX, userNode.quatY, userNode.quatZ, userNode.quatW]);
		self.space_client.sendEvent(event);
	}
	
	self.handle_keyup = function(event){
		return false;
	}

	self.add_event_source = function(node){
		$(node).keydown(self.handle_keydown).keyup(self.handle_keyup);
	}
}
