//Three.JS global variables to handle all the rendering.
var camera, controls, scene, renderer; 
var material, geometry, line, light;
//Racyaster and mouse ray global objects to enable interactivity with the particle lines.
var raycaster = new THREE.Raycaster();
var mouse = new THREE.Vector2();
//Material object that contains all the materials used by particle lines.
var materials = {
	photon: new THREE.LineBasicMaterial({
		color: 0x0099aa,
		linewidth: 2.
	}),
	lepton: new THREE.LineBasicMaterial({
		color: 0xddbb00,
		linewidth: 4.
	}),
	nu: new THREE.LineBasicMaterial({
		color: 0x333333,
		linewidth: 2.
	}),
	hadron: new THREE.LineBasicMaterial({
		color: 0x338833,
		linewidth: 2.
	}),
	detector: new THREE.MeshLambertMaterial({
		color: 0x9999ff,
		transparent: true,
		opacity: 0.4,
		emissive: 10,
		reflectivity: 1
	}),
	beam: new THREE.LineDashedMaterial({
		color: 0x666666,
		linewidth: 5.
	})
};
//Filename for the file being visualized.
var file;
//The number of the event being visualized.
var no;
//Whether the event is being visualized in momentum space (=1) or spacetime (=2).
var viewMode;

var maxno = 8; //placeholder; find way to add max number of events in file

//Object for registering mouse position on-click.
var clickInfo = {
	x: 0,
	y: 0,
	userHasClicked: false
};
//Normalize window coordinates.
function onMouseMove(event) {
	mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
	mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
};
//Callback to register mouse position on-click.
function onMouseClick(event) {
	clickInfo.userHasClicked = true;
	clickInfo.x = event.clientX;
	clickInfo.y = event.clientY;
};
//Callback to clear the visualizer when switching events or view modes.
function clearScene() {
	removableItems = []
	scene.children.forEach(function (obj) {
		if (obj.type === "Line" && obj.material != materials.beam) {
			removableItems.push(obj);
		}



	});
	while (removableItems.length > 0) {
		scene.remove(removableItems[0]);
		removableItems.shift();
	}

};

//Callback to switch events or view modes on appropriate keyboard presses.
$('*').off().keydown(function (event) {
	//This method call stops the events from triggering more than once per click.
	event.stopImmediatePropagation();
	var switchEvent = false;
	//Key = N, switches to next event.
	if (event.keyCode == 78 && no < maxno) {
		no = no + 1;
		switchEvent = true;
	//Key = B, switches to previous event.
	} else if (event.keyCode == 66 && no > 1) {
		no = no - 1;
		switchEvent = true;
	//Key = 1, switches to momentum space view.
	} else if (event.keyCode == 49 && viewMode == 2) {
		viewMode = 1;
		switchEvent = true;
	//Key = 2, switches to spacetime view.
	} else if (event.keyCode == 50 && viewMode == 1) {
		viewMode = 2;
		switchEvent = true;
	}
	//Performs the AJAX call to retrieve appropriate event. On success, clear scene and visualize the new event.
	if (switchEvent == true) {
		$.ajax({
			type: 'GET',
			url: 'http://127.0.0.1:5000/visualiser/get_event',
			data: {
				"no": no,
				"filename": file
			},
			success: function (data) {
				clearScene();
				visualizeParticles(JSON.parse(data.particles), JSON.parse(data.vertices));
			}
		});
	}
});
//Register event listeners.
window.addEventListener('mousemove', onMouseMove, false);
window.addEventListener('click', onMouseClick, false);
//Initialize the Python variables processed by the template.
function initVars(vars) {
	init(arguments[0], arguments[1], arguments[2]);
	animate();
};
//Set up the scene and load first event.
function init(particleData, vertexData, filename) {
	no = 1;
	file = filename;
	viewMode = 1;
	renderer = new THREE.WebGLRenderer();
	renderer.setSize(window.innerWidth, window.innerHeight);
	document.body.appendChild(renderer.domElement);

	camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.01, 5000);
	camera.position.set(400, 150, 700);
	camera.lookAt(new THREE.Vector3(0, 0, 0));

	controls = new THREE.OrbitControls(camera, renderer.domElement);


	scene = new THREE.Scene();



	light = new THREE.PointLight(0xffffff);
	light.position.set(200.0, 200.0, 500.0);
	scene.add(light);
	light = new THREE.AmbientLight(0x444444)
	scene.add(light);


	geometry = new THREE.Geometry();
	geometry.vertices.push(new THREE.Vector3(0, 0, -10000));
	geometry.vertices.push(new THREE.Vector3(0, 0, 10000));
	line = new THREE.Line(geometry, materials.beam);
	scene.add(line);

	var geometry = new THREE.CylinderGeometry(115.0, 115.0, 700.0, 64);
	var solenoid = new THREE.Mesh(geometry, materials.detector);
	solenoid.rotation.x += Math.PI / 2
	scene.add(solenoid);
	visualizeParticles(particleData, vertexData);
};

//Helper function to get particle type to select material.
function getParticleType(particle) {
	var particleType;
	switch (particle["pid"]) {
		case 22:
			particleType = "photon";
			break;
		case 11:
		case -11:
		case 13:
		case -13:
		case 15:
		case -15:
			particleType = "lepton";
			break;
		case 12:
		case -12:
		case 14:
		case -14:
		case 16:
		case -16:
			particleType = "nu";
			break;
		default:
			particleType = "hadron";
	}
	return particleType;
};

//Function to visualize particle data.
function visualizeParticles(particleData, vertexData) {
	//Momentum view.
	if (viewMode === 1) {
		for (var i = 0; i < particleData.length; i++) {
			//Get momentum and type.
			var verts = [0, 0, 0, particleData[i].momentum.slice(0, 3)];
			var type = getParticleType(particleData[i]);
			//Point line to momentum coordinates.
			geometry = new THREE.Geometry();
			geometry.vertices.push(new THREE.Vector3(verts[0], verts[1], verts[2]));
			geometry.vertices.push(new THREE.Vector3(verts[3][0], verts[3][1], verts[3][2]));
			var line = new THREE.Line(geometry, materials[type]);
			//Add data for display on-click.
			line.userData = {
				pType: type,
				pid: particleData[i].pid,
				momentum: particleData[i].momentum
			};
			scene.add(line);
		};
	//Soacetime view.
	} else if (viewMode === 2) {
		//Timestep.
		var DT = 5 * 10 ** (-10);
		//Number of steps.
		var NSTEP = 16;
		for (var i = 0; i < particleData.length; i++) {
			var verts = [];
			var E = particleData[i].momentum[3];
			var mass = 0.0;
			//Get mass if particle is not massles.
			if (particleData[i].momentum[0] ** 2 + particleData[i].momentum[1] ** 2 + particleData[i].momentum[2] ** 2 < E) {
				mass = Math.sqrt(E ** 2 - particleData[i].momentum[0] ** 2 - particleData[i].momentum[1] ** 2 - particleData[i].momentum[2] ** 2);
				};
				//Find vstart vertex position.
				var pos3 = vertexData.find(function (vertex) {
					return vertex.barcode === particleData[i].start_vertex;
				}).position.slice(0, 3);
				//Get momentum and charge.
				var mom3 = particleData[i].momentum.slice(0, 3);
				var charge = particleData[i].charge;
				verts.push(pos3);
				//Model particle movement over time.
				for (var j = 0; j < NSTEP; j++) {

					var vel3 = mom3.map(mom => mom / E * 3 * 10 ** 8);
					//Model electric force if particle is charged.
					if (particleData[i].charge != 0) {
						pos3 = vel3.map(vel => vel + vel*DT)
						var force = math.cross(vel3, [0, 0, 4]).map(f => f*particleData[i].charge);
						mom3 = mom3.map(mom => mom + DT ^ force / 500);
						verts.push(pos3);
					//If particle is not charged, just use momentum.
					} else {
						pos3 = pos3.map(vel => vel + vel * DT);
						verts.push(pos3);
					}
				};
				
				if (verts.length === 2){
					gemoetry = new THREE.Geometry();
					verts.forEach(function(vert){
					geometry.vertices.push(new THREE.Vector3(vert[0], verts[1], verts[2]));
				});
				}
				else {
					var points = verts.map(vert => new THREE.Vector3(vert[0], vert[1], vert[2]));
					var curve = new THREE.CatmullRomCurve3(points);
					geometry = new THREE.BufferGeometry().setFromPoints(curve.getPoints(100));
				}
				//Analogous to momentum view.
				type = getParticleType(particleData[i]);
				var line = new THREE.Line(geometry, materials[type]);
				line.userData = {
					pType: type,
					pid: particleData[i].pid,
					momentum: particleData[i].momentum
				};
				scene.add(line);
			};

		};

	};

	//Start render loop.
	function animate() {
		requestAnimationFrame(animate);
		render();
	};
	//Render loop.
	function render() {
		//Checks if user has clicked.
		if (clickInfo.userHasClicked) {
			//Resets the click check.
			clickInfo.userHasClicked = false;
			raycaster.setFromCamera(mouse, camera);
			//Gets all objects intersecting mouse ray. Displays info for first particle line encountered.
			var intersects = raycaster.intersectObjects(scene.children);
			for (var i = 0; i < intersects.length; i++) {
				if (intersects[i].object.type == "Line") {
					var info = "Type:" + intersects[i].object.userData.pType + "\n" + "ID:" + String(intersects[i].object.userData.pid) + "\n" + "Momentum" + String(intersects[i].object.userData.momentum)
					$("[id=info]").text(info)
					break;
				}
			}
		}
		renderer.render(scene, camera);
	};