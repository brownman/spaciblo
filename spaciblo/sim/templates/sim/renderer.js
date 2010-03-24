
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
		var template = self.getTemplate(jsonData['attributes']['id']);
		if(!template){
			console.log("Received template data for an unloaded template: " + jsonData['attributes']['id']);
			return;
		}
		SpacibloModels.rehydrateModel(jsonData, template);
		template.templateAssets = []
		if(jsonData['templateassets']){
			for(var i=0; i < jsonData['templateassets'].length; i++){
				var templateAsset = new SpacibloModels.TemplateAsset();
				SpacibloModels.rehydrateModel(jsonData['templateassets'][i], templateAsset);
				templateAsset.asset = new SpacibloModels.Asset();
				SpacibloModels.rehydrateModel(jsonData['templateassets'][i].asset, templateAsset.asset);
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

// 
//
//
// RENDERABLE
//
//

SpacibloRenderer.Renderable = function(thing){
	var self = this;
	self.thing = thing;
	self.thing.renderable = self;
	
	self.children = new Array();
	//self.glObj.setPosition(self.thing.position.x, self.thing.position.y, self.thing.position.z);
	for(var index=0; index < self.thing.children.length; index++){
		self.children[self.children.length] = new SpacibloRenderer.Renderable(self.thing.children[index]);
	}
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
	self.scene = null;
	self.username = null;
	self.canvas = null;
	self.gl = null;
	self.renderables = [];
	
	self.initialize = function(scene, username) {
		self.scene = scene;
		self.username = username;
		
		self.canvas = document.getElementById(self.canvas_id);		
		if(self.canvas == null) return false;
		try {
			self.gl = canvas.getContext("experimental-webgl");
			self.gl.viewport(0, 0, self.canvas.width, self.canvas.height);
		} catch(e) {
			console.log("Error initializing WebGL");
			console.log(e);
			return false;
		}
		self.gl.clearColor(scene.background_color.red, scene.background_color.green, scene.background_color.blue, scene.background_color.alpha);
		self.gl.clearDepth(1.0);
		self.gl.enable(self.gl.DEPTH_TEST);
		self.gl.depthFunc(self.gl.LEQUAL);

		var rootRenderable = new SpacibloRenderer.Renderable(self.scene.thing);
		self.renderables[self.renderables.length] = rootRenderable;
		self.initializeRenderable(rootRenderable);
	    return true;
	}

	self.initializeRenderable = function(renderable){
		if(renderable.thing.template_id) self.assetManager.getOrCreateTemplate(renderable.thing.template_id);
		for(var i=0; i < renderable.children.length; i++){
			self.initializeRenderable(renderable.children[i]);
		}
	}

	self.render = function() {
		self.gl.clear(self.gl.COLOR_BUFFER_BIT | self.gl.DEPTH_BUFFER_BIT);

		//var userThing = self.scene.thing.getUserThing(self.username);
	}

	self.close = function(){
		if(self.canvas == null || self.gl == null) return;
		self.gl.clearColor(1.0, 1.0, 1.0, 1.0);
	}
	
	self.handleImageAsset = function(image, path){ }
	
	self.handleTemplateAsset = function(template){ }
	
	self.handleGeometryAsset = function(templateID, templateAssetID, geometry){ }

	self.assetManager = new SpacibloRenderer.AssetManager(self.handleImageAsset, self.handleTemplateAsset, self.handleGeometryAsset);
}
