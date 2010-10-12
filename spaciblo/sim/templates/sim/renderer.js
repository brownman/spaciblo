
SpacibloRenderer = {}

//
//
// AssetManager
//
//
//

SpacibloRenderer.AssetManager = function(imageCallback, templateCallback, geometryCallback){
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
		var template = self.getTemplate(jsonData['id']);
		if(!template){
			console.log("Received template data for an unloaded template: " + jsonData['id']);
			return;
		}
		SpacibloModels.rehydrateModel(jsonData, template);
		template.templateAssets = []
		if(jsonData['assets']){
			for(var i=0; i < jsonData['assets'].length; i++){
				var templateAsset = new SpacibloModels.TemplateAsset();
				SpacibloModels.rehydrateModel(jsonData['assets'][i], templateAsset);
				templateAsset.asset = new SpacibloModels.Asset();
				SpacibloModels.rehydrateModel(jsonData['assets'][i].asset, templateAsset.asset);
				template.templateAssets[i] = templateAsset;
			}
		}
		if (self.templateCallback) self.templateCallback(template);

		// Now that we have notified listeners about the template, load the assets.
		for(var i=0; i < template.templateAssets.length; i++){
			if(template.templateAssets[i].asset.type == 'texture'){
				self.loadImage('/api/sim/template/' + template.id + '/asset/' + template.templateAssets[i].key);
			} else if (template.templateAssets[i].asset.type == 'geometry' && template.templateAssets[i].key.endsWith('.obj')){
				self.loadGeometry(template.id, template.templateAssets[i].id, '/api/sim/template/' + template.id + '/asset/' + template.templateAssets[i].key);
			}
		}
	}

	self.loadGeometry = function(templateID, templateAssetID, path){
		if(self.geometries[templateAssetID]) return;
		self.geometries[templateAssetID] = {};
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
		self.geometries[request.templateAssetID] = jsonData;
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

SpacibloRenderer.DefaultMaterial = new GLGE.Material(GLGE.Assets.createUUID());
SpacibloRenderer.DefaultMaterial.setColor("chocolate");
SpacibloRenderer.DefaultMaterial.setSpecular(1);
SpacibloRenderer.DefaultMaterial.setShininess(20);

// 
//
//
// RENDERABLE
//
//

SpacibloRenderer.Renderable = function(canvas, uid){
	GLGE.Assets.registerAsset(this,uid);
	this.canvas = canvas;
	this.children = [];
}	
GLGE.augment(GLGE.Group,SpacibloRenderer.Renderable);

SpacibloRenderer.Renderable.prototype.init = function(nodeJson){

	this.setLoc(nodeJson.locX, nodeJson.locY, nodeJson.locZ);
	this.setScale(nodeJson.scaleX, nodeJson.scaleY, nodeJson.scaleZ);

	if(nodeJson.mesh != null){
		var obj = new GLGE.Object(GLGE.Assets.createUUID());
		if(nodeJson.material){
			var material = new GLGE.Material(GLGE.Assets.createUUID());
			material.setColor({r:nodeJson.material.specColor[0], g:nodeJson.material.specColor[1], b:nodeJson.material.specColor[2]});
			material.setSpecular(nodeJson.material.specular);
			material.setShininess(nodeJson.material.shine);
			material.setAlpha(nodeJson.material.alpha);
			obj.setMaterial(material);
		} else {
			obj.setMaterial(SpacibloRenderer.DefaultMaterial);
		}

		var mesh = new GLGE.Mesh(GLGE.Assets.createUUID());
		mesh.setPositions(nodeJson.mesh.positions);
		mesh.setFaces(nodeJson.mesh.faces);
		if(nodeJson.mesh.normals && nodeJson.mesh.normals.length > 0) mesh.setNormals(nodeJson.mesh.normals);
		if(nodeJson.mesh.UV && nodeJson.mesh.UV.length > 0) mesh.setUV(nodeJson.mesh.UV);
		obj.setMesh(mesh);

		this.addChild(obj);
	} else {
		console.log("No mesh");
	}

	if(typeof nodeJson.children == "undefined") return;
	for(var i=0; i < nodeJson.children.length; i++){
		var childRenderable = new SpacibloRenderer.Renderable(self.canvas, GLGE.Assets.createUUID());
		childRenderable.init(nodeJson.children[i]);
		this.addChild(childRenderable);
	}
}

SpacibloRenderer.parseArray = function(data){
	var result = [];
	currentArray = data.split(",");
	for(i = 0; i < currentArray.length; i++) result.push(currentArray[i]);
	return result;
}

// 
//
//
// CANVAS
//
//

SpacibloRenderer.Canvas = function(_canvas_id){
	var self = this;
	self.canvas_id = _canvas_id;
	self.username = null;
	self.canvas = null;
	self.gameRenderer = null;
	self.scene = null;

	self.initialize = function(sceneJson, username) {
		self.username = username;
		self.canvas = document.getElementById(self.canvas_id);		
		if(self.canvas == null) return false;

		self.gameRenderer = new GLGE.Renderer(self.canvas);

		var light1 = new GLGE.Light(GLGE.Assets.createUUID());
		light1.setLocX(-3);
		light1.setLocY(15)
		light1.setLocZ(-7);
		light1.setAttenuationQuadratic(0.00001);
		light1.setAttenuationLinear(0.00000001);
		light1.setAttenuationConstant(1);
		light1.setType(GLGE.L_POINT);

		var light2 = new GLGE.Light(GLGE.Assets.createUUID());
		light2.setLocX(3);
		light2.setLocY(15)
		light2.setLocZ(-7);
		light2.setAttenuationQuadratic(0.00001);
		light2.setAttenuationLinear(0.00000001);
		light2.setAttenuationConstant(1.5);
		light2.setType(GLGE.L_POINT);

		var userGroup = new GLGE.Group(GLGE.Assets.createUUID());
		userGroup.username = self.username;
      
		self.scene = new GLGE.Scene();
		self.scene.obj_name = "I am the scene";
		self.scene.setAmbientColor("#555");
		self.scene.setBackgroundColor("#55F");
		self.scene.addLight(light1);
		self.scene.addChild(userGroup);
		for(var i=0; i < sceneJson.children.length; i++){
			var renderable = new SpacibloRenderer.Renderable(self, GLGE.Assets.createUUID());
			renderable.init(sceneJson.children[i]);
			self.scene.addChild(renderable);
		}

		self.gameRenderer.setScene(self.scene);
		self.scene.camera.setRot(Spaciblo.defaultRotation[0], Spaciblo.defaultRotation[1], Spaciblo.defaultRotation[2]);
		self.scene.camera.setLoc(Spaciblo.defaultPosition[0], Spaciblo.defaultPosition[1], Spaciblo.defaultPosition[2]);

		//self.requestTemplates(self.scene.thing);

	    return true;
	}

	self.requestTemplates = function(thing){
		if(thing.template_id) thing.template = self.assetManager.getOrCreateTemplate(thing.template_id);
		for(var i=0; i < thing.children.length; i++){
			self.requestTemplates(thing.children[i]);
		}
	}

	self.render = function() {
		/*
		var userThing = self.scene.thing.getUserThing(self.username);
		if(userThing){
			self.scene.camera.setLoc(userThing.position.x, userThing.position.y, userThing.position.z);
			self.scene.camera.setQuat(userThing.orientation.x, userThing.orientation.y, userThing.orientation.z, userThing.orientation.s);
		}
		*/
		self.gameRenderer.render();
	}

	self.close = function(){
		if(self.canvas == null || self.gl == null) return;
		//self.gl.clearColor(1.0, 1.0, 1.0, 1.0);
	}
	
	self.handleImageAsset = function(image, path){ }
	
	self.handleTemplateAsset = function(template){ }
	
	self.handleGeometryAsset = function(templateID, templateAssetID, geometry){
		console.log('should load geo asset');
		/*
		var things = self.scene.thing.getThingsByTemplate(templateID);
		for(var i=0; i < things.length; i++){
			try {
				var renderable = new SpacibloRenderer.Renderable(geometry, self, GLGE.Assets.createUUID());
				renderable.thing = things[i];
				renderable.init();
				renderable.setLoc(renderable.thing.position.x, renderable.thing.position.y, renderable.thing.position.z);
				renderable.setQuat(renderable.thing.orientation.x, renderable.thing.orientation.y, renderable.thing.orientation.z, renderable.thing.orientation.s);
				self.scene.addChild(renderable);
			} catch (err){
				console.log(err);
			} 
		}
		*/
	}

	self.assetManager = new SpacibloRenderer.AssetManager(self.handleImageAsset, self.handleTemplateAsset, self.handleGeometryAsset);
}
