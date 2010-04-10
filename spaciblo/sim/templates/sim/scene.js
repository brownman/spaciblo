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

SpacibloScene.Thing.prototype.getThingsByTemplate = function(templateID, results){
	if(!results) {
		results = new Array();
	}
	if(this.template_id == templateID) results[results.length] = this;
	for(var i=0; i < this.children.length; i++)
		this.children[i].getThingsByTemplate(templateID, results);
	return results
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
}

SpacibloScene.Thing.prototype.init = function(){
	this.children = [];
	this.renderable = null;
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

SpacibloScene.parseSceneDocument = function(sceneDoc){
   console.log(sceneDoc);
	var sceneData = JSON.parse(sceneDoc);
	var scene = new SpacibloScene.Scene(new SpacibloScene.Color(sceneData['attributes']['background_color']));
	scene.thing = SpacibloScene.parseThingData(sceneData['thing'], null, this);
	return scene;
}

SpacibloScene.parseThingData = function(thingData, parent, scene){
	var thing = new SpacibloScene.Thing(thingData['attributes']['id'], new SpacibloScene.Position(thingData['attributes']['position']), new SpacibloScene.Orientation(thingData['attributes']['orientation']), parseFloat(thingData['attributes']['scale']));
	thing.parent = parent;
	thing.template_id = thingData['attributes']['template'];
	if(thingData['attributes']['user']){
		if(scene.thing)
			thing.user = scene.thing.getUser(thingData['attributes']['user']);
		if(!thing.user)
			thing.user = new SpacibloScene.User(thingData['attributes']['user']);
	}
	if(thingData['children']){
		for(var i=0; i < thingData['children'].length; i++){
			thing.children[thing.children.length] = SpacibloScene.parseThingData(thingData['children'][i], thing, scene);
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
