var camera, controls, scene, renderer;
var material, geometry, line, light;
var raycaster = new THREE.Raycaster();
var mouse = new THREE.Vector2();
var no = 1;
var filename = "badtops_8events";
 var materials = { photon : new THREE.LineBasicMaterial( { color: 0x0099aa, linewidth: 2. } ), 
			lepton : new THREE.LineBasicMaterial( { color: 0xddbb00, linewidth: 4. } ),
			nu : new THREE.LineBasicMaterial( { color: 0x333333, linewidth: 2. } ),
			hadron :  new THREE.LineBasicMaterial( { color: 0x338833, linewidth: 2. } ),
			detector : new THREE.MeshLambertMaterial( { color: 0x9999ff, transparent: true, opacity: 0.4, emissive: 10, reflectivity: 1 } ),
			beam :  new THREE.LineDashedMaterial( { color: 0x666666, linewidth: 5. } )
			};

function initVars(vars){
init(arguments[0], arguments[1]);
animate();
};
function onMouseMove(event){
mouse.x = ( event.clientX / window.innerWidth ) * 2 - 1;
mouse.y = - ( event.clientY / window.innerHeight ) * 2 + 1;
};

window.addEventListener('mousemove', onMouseMove, false);

var clickInfo = {
	x: 0,
	y: 0,
	userHasClicked: false
	};

function onMouseClick(event){
clickInfo.userHasClicked = true;
clickInfo.x = event.clientX;
clickInfo.y = event.clientY;
};

window.addEventListener('click', onMouseClick, false);

function init(view, particleData) {
  renderer = new THREE.WebGLRenderer();
  renderer.setSize( window.innerWidth, window.innerHeight );
  document.body.appendChild( renderer.domElement );

  camera = new THREE.PerspectiveCamera( 45, window.innerWidth / window.innerHeight, 0.01, 5000 );
  camera.position.set( 400, 150, 700 );
  camera.lookAt( new THREE.Vector3( 0, 0, 0 ) );

  controls = new THREE.OrbitControls( camera, renderer.domElement );
 

  scene = new THREE.Scene();

  

  light = new THREE.PointLight(0xffffff);
  light.position.set(200.0, 200.0, 500.0);
  scene.add( light );
  light = new THREE.AmbientLight(0x444444)
  scene.add( light );
 

  geometry = new THREE.Geometry();
  geometry.vertices.push(new THREE.Vector3( 0, 0, -10000 ) );
  geometry.vertices.push(new THREE.Vector3( 0, 0,  10000 ) );
  line = new THREE.Line( geometry, materials.beam );
  scene.add( line );

  var geometry = new THREE.CylinderGeometry( 115.0, 115.0, 700.0, 64 );
  var solenoid = new THREE.Mesh( geometry, materials.detector );
  solenoid.rotation.x += Math.PI / 2
  scene.add( solenoid );
  visualizeParticles(view, particleData, materials);
};

function clearScene (scene){
	while(scene.children.length > 0){
		if(scene.children[0].type === "Line"){
		scene.remove(scene.children[0]);
};
}

}


function visualizeParticles(view, particleData, materials){
if ( view  === 1) {
	for (var i = 0; i < particleData.length; i++) {
		var verts = [0, 0, 0, particleData[i].momentum.slice(0, 3)];
		var type = getParticleType(particleData[i]);
		geometry = new THREE.Geometry();
		geometry.vertices.push(new THREE.Vector3(verts[0], verts[1], verts[2]));
		geometry.vertices.push(new THREE.Vector3(verts[3][0], verts[3][1], verts[3][2]));
		var line = new THREE.Line(geometry, materials[type]);
		line.userData = {pType : type, 
				pid:particleData[i].pid,
				 momentum : particleData[i].momentum
				};
		scene.add(line);
	};
};
};
function getParticleType(particle){
	var particleType;
	switch (particle["pid"]){
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

function animate() {
    requestAnimationFrame( animate );
    render();
};

function render() {
    if (clickInfo.userHasClicked) {
    clickInfo.userHasClicked = false;
    raycaster.setFromCamera(mouse, camera);
    var intersects = raycaster.intersectObjects(scene.children);
    if (intersects.length && intersects[0].object.type === "Line"){
	console.log(intersects[0].object);
	var info = "Type:" + intersects[0].object.userData.pType + "\n" + "ID:" + String(intersects[0].object.userData.pid)
	document.getElementById("info").innerHTML = info
								}
    else if (intersects.length > 1 && intersects[1].object.type === "Line"){
	console.log(intersects[0].object, intersects[1].object);
	var info = "Type:" + intersects[1].object.userData.pType + "\n" + "ID:" + String(intersects[1].object.userData.pid)
	document.getElementById("info").innerHTML = info
									}
		}
renderer.render( scene, camera );
};


	$('*').keydown(function(event){
		console.log(event.keyCode);
		if(event.keyCode == 78){
			no = no + 1;
			}
		if(event.keyCode == 66){
			no = no - 1;
			}
			$.ajax({
			type: 'GET',
			url: 'http://127.0.0.1:5000/visualiser/get_event',
			data: {"no":no, "filename":filename},
			success: function(particles){clearScene(scene); visualizeParticles(1, particles, materials), console.log(particles)}
			});
		});
	


