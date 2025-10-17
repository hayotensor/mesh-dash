// Basic Three.js setup
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(
  75,
  window.innerWidth / window.innerHeight,
  0.1,
  1000
);
const renderer = new THREE.WebGLRenderer();
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

// Orbit controls
const controls = new THREE.OrbitControls(camera, renderer.domElement);

// Add light
const light = new THREE.PointLight(0xffffff, 1);
light.position.set(10, 10, 10);
scene.add(light);

// Fetch nodes from API
fetch("/api/nodes")
  .then(res => res.json())
  .then(data => {
    data.nodes.forEach(n => {
      const geometry = new THREE.SphereGeometry(0.3, 16, 16);
      const material = new THREE.MeshPhongMaterial({ color: 0x00ff00 });
      const sphere = new THREE.Mesh(geometry, material);
      sphere.position.set(n.x, n.y, n.z);
      scene.add(sphere);
    });
    animate();
  });

// Camera
camera.position.z = 10;

// Animate loop
function animate() {
  requestAnimationFrame(animate);
  controls.update();
  renderer.render(scene, camera);
}

// Handle window resize
window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
