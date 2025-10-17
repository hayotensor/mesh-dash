// Three.js scene setup
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(
  60,
  window.innerWidth / window.innerHeight,
  0.1,
  1000
);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

// Orbit controls for rotating / zooming
const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.05;

// Light
const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
scene.add(ambientLight);

const directionalLight = new THREE.DirectionalLight(0xffffff, 10.0);
directionalLight.position.set(110, 110, 110);
scene.add(directionalLight);

// Load GLTF Earth model
const loader = new THREE.GLTFLoader();
loader.load(
  '/static/3d/Earth.glb', // path to your GLB file
  function (gltf) {
    const earth = gltf.scene;
    earth.scale.set(0.005, 0.005, 0.005); // scale globe if needed
    scene.add(earth);

    animate();
  },
  undefined,
  function (error) {
    console.error('Error loading GLTF:', error);
  }
);

// Camera position
camera.position.set(0, 0, 10);

// Optional: add example nodes
function addNode(lat, lon, radius = 2.05) {
  // Convert lat/lon to Cartesian coordinates
  const phi = (90 - lat) * (Math.PI / 180);
  const theta = (lon + 180) * (Math.PI / 180);

  const x = -radius * Math.sin(phi) * Math.cos(theta);
  const y = radius * Math.cos(phi);
  const z = radius * Math.sin(phi) * Math.sin(theta);

  const geometry = new THREE.SphereGeometry(0.05, 16, 16);
  const material = new THREE.MeshPhongMaterial({ color: 0xff0000 });
  const sphere = new THREE.Mesh(geometry, material);
  sphere.position.set(x, y, z);
  scene.add(sphere);
}

// Example: 3 nodes
addNode(37.7749, -122.4194); // San Francisco
addNode(51.5074, -0.1278);   // London
addNode(-33.8688, 151.2093); // Sydney

// Animate loop
function animate() {
  requestAnimationFrame(animate);
  controls.update();
  renderer.render(scene, camera);
}

// Handle window resize
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
