# Developing with Three.js

This note summarizes discussions and guidance on working with the Three.js library for 3D web development.

## Key Areas of Knowledge

-   **Foundations:** Solid skills in vanilla JavaScript, HTML, CSS, and DOM manipulation.
-   **Three.js Basics:** Setting up a scene (scene, camera, renderer), adding geometries, materials, and textures.
-   **WebGL Knowledge:** Understanding WebGL basics as Three.js abstracts it.
-   **3D Concepts:** Grasp of 3D modeling, animation, lighting, and shading.
-   **Mathematical Skills:** Linear algebra and calculus for transformations and rotations.
-   **Development Environment:** Using npm with build tools (e.g., Vite) or CDN.
-   **Additional Libraries:** Exploring extensions and libraries for enhanced functionality.
-   **Game Development:** Implementing loaders, collision detection, HUDs, and interfaces.

## Popular Three.js Projects & Examples

-   A-Frame.io (VR framework)
-   Virtual Showrooms
-   Architectural Visualization
-   Bitburger 3D Experience
-   Educational projects (Penguin in a Globe, Low Poly Terrain)
-   Interactive elements (Particles Text, Animated Rocket)
-   Seasonal projects (Xmas Ornaments, Ghost Card)
-   Physics simulations (Space Globe, Pendulum)
-   Blender and Houdini Integration

## Setting up a TypeScript Project with Three.js and Vite

1.  **Initialize Vite Project:** `npm create vite@latest my-threejs-project --template react-ts`
2.  **Install Dependencies:** `npm install three @types/three`
3.  **Configure TypeScript:** Ensure `tsconfig.json` is set for `ESNext` and `Node` module resolution.
4.  **Configure Vite:** Exclude `three` from `optimizeDeps` and `external` in `rollupOptions` in `vite.config.ts`.
5.  **Create Basic Scene:** Set up `scene`, `camera`, `renderer`, and add objects (e.g., cube).
6.  **Handle Static Assets:** Place assets in the `public` folder.
7.  **Run and Build:** `npm run dev` and `npm run build`.

## Voxel-Based Landing Page

-   **Concept:** Combine voxel art aesthetic with modern web design for a visually engaging landing page.
-   **Tech Stack:** React, `@react-three/fiber`, `@react-three/drei`.
-   **Basic Scene:** Create a 5x5x5 voxel grid with `Box` components.
-   **Curved Sections:** Use CSS `clip-path` or SVG for visual appeal.
-   **Interactive Elements:** Implement `InteractiveBox` components with hover effects (scaling, color change) using `useFrame` and `useState`.
-   **On-Scroll Animation:** Use `IntersectionObserver` to detect when elements enter the viewport and trigger CSS transitions (opacity, transform) for text sections and the voxel scene.
-   **Optimization:** Use LOD, limit lights, compress assets.
-   **Deployment:** Vercel, Netlify, GitHub Pages.

## WebGL Animated Penrose Triangle (Three.js)

A code example for creating an animated Penrose Triangle using WebGL and the Three.js library:

```javascript
// Create a WebGL renderer
const renderer = new THREE.WebGLRenderer();
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

// Create a camera
const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 1, 1000);
camera.position.set(0, 0, 5);

// Create a scene
const scene = new THREE.Scene();

// Create a Penrose Triangle geometry
const geometry = new THREE.Geometry();
const vertices = [
  new THREE.Vector3(-1, -1, 0),
  new THREE.Vector3(1, -1, 0),
  new THREE.Vector3(0, 1, 0),
  new THREE.Vector3(-1, -1, 0),
  new THREE.Vector3(0, -1, -1),
  new THREE.Vector3(0, 1, 0),
  new THREE.Vector3(0, -1, -1),
  new THREE.Vector3(1, -1, 0),
  new THREE.Vector3(0, 1, 0),
];
geometry.vertices = vertices;

// Create a material
const material = new THREE.LineBasicMaterial({ color: 0xffffff });

// Create a Penrose Triangle shape and add it to the scene
const penroseTriangle = new THREE.Line(geometry, material);
scene.add(penroseTriangle);

// Define the animation loop
function animate() {
  requestAnimationFrame(animate);
  penroseTriangle.rotation.x += 0.01;
  penroseTriangle.rotation.y += 0.01;
  renderer.render(scene, camera);
}

// Start the animation loop
animate();
```

## Related Documents

- [[30-All-Notes/Developing_with_ThreeJs.md]]
- [[30-All-Notes/Omnizya_Startup_Launch..md]]
