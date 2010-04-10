
SpacibloRenderer = {}

SpacibloRenderer.vsShaderSource = "\
attribute vec3 aVertexPosition;\
attribute vec4 aVertexColor;\
uniform mat4 uMVMatrix;\
uniform mat4 uPMatrix;\
varying vec4 vColor;\
void main(void) {\
 gl_Position = uPMatrix * uMVMatrix * vec4(aVertexPosition, 1.0);\
 vColor = aVertexColor;\
}\
";

SpacibloRenderer.fsShaderSource = "\
varying vec4 vColor;\
void main(void) {\
 gl_FragColor = vColor;\
}\
";

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

SpacibloRenderer.Renderable = function(geometry, canvas){
	var self = this;
	self.geometry = geometry;
	self.canvas = canvas
	self.gl = canvas.gl;

	self.thing = null; //this is only filled out for the Geometry which is the root of the Thing's geometry tree
	self.position = new SpacibloScene.Position("0,0,0");
	self.orientation = new SpacibloScene.Orientation("1,0,0,0");
	
	self.vertexPositionBuffer = self.gl.createBuffer();
	self.gl.bindBuffer(self.gl.ARRAY_BUFFER, self.vertexPositionBuffer);
	self.gl.bufferData(self.gl.ARRAY_BUFFER, new WebGLFloatArray(geometry.vertices), self.gl.STATIC_DRAW);
	self.vertexPositionBuffer.itemSize = 3;
	self.vertexPositionBuffer.numItems = geometry.vertices.length / 3;
	
	self.vertexColorBuffer = self.gl.createBuffer();
	self.gl.bindBuffer(self.gl.ARRAY_BUFFER, self.vertexColorBuffer);
	var colors = []
	for (var i=0; i < self.vertexPositionBuffer.numItems; i++) {
		if(self.geometry.material){
			colors = colors.concat([self.geometry.material.diffuse[0], self.geometry.material.diffuse[1], self.geometry.material.diffuse[2], 1.0]);
		} else {
			colors = colors.concat([0.5, 1, 0.5, 1.0]);
		}
	}

	self.gl.bufferData(self.gl.ARRAY_BUFFER, new WebGLFloatArray(colors), self.gl.STATIC_DRAW);
	self.vertexColorBuffer.itemSize = 4;
	self.vertexColorBuffer.numItems = self.vertexPositionBuffer.numItems;
	
	self.children = new Array();
	for(var index=0; index < self.geometry.children.length; index++){
		self.children[self.children.length] = new SpacibloRenderer.Renderable(self.geometry.children[index], self.canvas);
	}

	self.render = function(pMatrix, mvMatrix){
		self.gl.bindBuffer(self.gl.ARRAY_BUFFER, self.vertexPositionBuffer);
		self.gl.vertexAttribPointer(canvas.shaderProgram.vertexPositionAttribute, self.vertexPositionBuffer.itemSize, self.gl.FLOAT, false, 0, 0);
		self.gl.uniformMatrix4fv(canvas.shaderProgram.pMatrixUniform, false, new WebGLFloatArray(pMatrix.flatten()));

		var gMvMatrix = mvMatrix.dup();
		var transMatrix = Matrix.Translation($V([self.position.x, self.position.y, self.position.z])).ensure4x4();
		gMvMatrix = gMvMatrix.x(transMatrix);
		//var arad = 0 * Math.PI / 180.0;
		//var v = [0, 1, 0];
		//var rotMatrix = Matrix.Rotation(arad, $V([v[0], v[1], v[2]])).ensure4x4();
		//gMvMatrix = gMvMatrix.x(rotMatrix);
		self.gl.uniformMatrix4fv(canvas.shaderProgram.mvMatrixUniform, false, new WebGLFloatArray(gMvMatrix.flatten()));

		self.gl.drawArrays(self.gl.TRIANGLES, 0, self.vertexPositionBuffer.numItems);
		self.gl.bindBuffer(self.gl.ARRAY_BUFFER, self.vertexColorBuffer);
		self.gl.vertexAttribPointer(self.canvas.shaderProgram.vertexColorAttribute, self.vertexColorBuffer.itemSize, self.gl.FLOAT, false, 0, 0);

		for(var index=0; index < self.children.length; index++){
			self.children[index].render(pMatrix, mvMatrix);
		}
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

		self.fsShader = self.gl.createShader(self.gl.FRAGMENT_SHADER);
		self.gl.shaderSource(self.fsShader, SpacibloRenderer.fsShaderSource);
		self.gl.compileShader(self.fsShader);

		self.vsShader = self.gl.createShader(self.gl.VERTEX_SHADER);
		self.gl.shaderSource(self.vsShader, SpacibloRenderer.vsShaderSource);
		self.gl.compileShader(self.vsShader);

		self.shaderProgram = self.gl.createProgram();
		self.gl.attachShader(self.shaderProgram, self.vsShader);
		self.gl.attachShader(self.shaderProgram, self.fsShader);
		self.gl.linkProgram(self.shaderProgram);

		if (!self.gl.getProgramParameter(self.shaderProgram, self.gl.LINK_STATUS)) console.log("Could not initialise shaders");
		self.gl.useProgram(self.shaderProgram);

		self.shaderProgram.vertexPositionAttribute = self.gl.getAttribLocation(self.shaderProgram, "aVertexPosition");
		self.gl.enableVertexAttribArray(self.shaderProgram.vertexPositionAttribute);
		self.shaderProgram.vertexColorAttribute = self.gl.getAttribLocation(self.shaderProgram, "aVertexColor");
		self.gl.enableVertexAttribArray(self.shaderProgram.vertexColorAttribute);
		self.shaderProgram.pMatrixUniform = self.gl.getUniformLocation(self.shaderProgram, "uPMatrix");
		self.shaderProgram.mvMatrixUniform = self.gl.getUniformLocation(self.shaderProgram, "uMVMatrix");


		self.requestTemplates(self.scene.thing);

	    return true;
	}

	self.requestTemplates = function(thing){
		if(thing.template_id) thing.template = self.assetManager.getOrCreateTemplate(thing.template_id);
		for(var i=0; i < thing.children.length; i++){
			self.requestTemplates(thing.children[i]);
		}
	}

	self.render = function() {
		self.gl.clear(self.gl.COLOR_BUFFER_BIT | self.gl.DEPTH_BUFFER_BIT);
		var fovy = 45;
		var aspect = 1.0;
		var znear = 0.1;
		var zfar = 100.0;
		var pMatrix = makePerspective(fovy, aspect, znear, zfar)

		var userThing = self.scene.thing.getUserThing(self.username);
		var position = null;
		if(userThing){
			position = [userThing.position.x, userThing.position.y, userThing.position.z];
			theta = userThing.orientation.s;
			rotVector = [userThing.orientation.x, userThing.orientation.y, userThing.orientation.z];
		} else {
			theta = 1;
			rotVector = [0,1,0];
			position = [-1.5, 0.0, -7.0];
		}
		var mvMatrix = Matrix.I(4);
		var rotMatrix = Matrix.Rotation(theta, $V(rotVector)).ensure4x4();
		mvMatrix = mvMatrix.x(rotMatrix.inverse());
		var transMatrix = Matrix.Translation($V(position)).ensure4x4();
		mvMatrix = mvMatrix.x(transMatrix.inverse());

		for(var i=0; i < self.renderables.length; i++){
			self.renderables[i].render(pMatrix, mvMatrix);
		}
	}

	self.close = function(){
		if(self.canvas == null || self.gl == null) return;
		self.gl.clearColor(1.0, 1.0, 1.0, 1.0);
	}
	
	self.handleImageAsset = function(image, path){ }
	
	self.handleTemplateAsset = function(template){ }
	
	self.handleGeometryAsset = function(templateID, templateAssetID, geometry){
		var things = self.scene.thing.getThingsByTemplate(templateID);
		for(var i=0; i < things.length; i++){
			var renderable = new SpacibloRenderer.Renderable(geometry, self);
			renderable.thing = things[i];
			renderable.position = things[i].position;
			renderable.orientation = things[i].orientation;
			self.renderables[self.renderables.length] = renderable;
		}
	}

	self.assetManager = new SpacibloRenderer.AssetManager(self.handleImageAsset, self.handleTemplateAsset, self.handleGeometryAsset);
}
