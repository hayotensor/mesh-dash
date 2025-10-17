// globe.js

// Default data in case WebSocket hasn't connected yet
let gElavationData = window.gElavationData || [
  {
    "name": "peer_1",
    "lat": 0.07 * 180,
    "lon": 0.07 * 360,
    "elevation": 10000
  },
  {
    "name": "peer_2",
    "lat": -0.01 * 180,
    "lon": -0.01 * 360,
    "elevation": 10000
  },
];

function spreadClusterCircle(cluster, radiusDeg = 0.5) {
  const n = cluster.length;
  if (n === 0) return cluster;
  
  const centerLat = cluster[0].lat;
  const centerLon = cluster[0].lon;

  if (n === 1) return cluster;

  let placed = 0;
  let layer = 1;

  while (placed < n) {
    const r = (layer / Math.ceil(Math.sqrt(n))) * radiusDeg;
    const nodesInLayer = Math.min(n - placed, layer * 6);

    for (let i = 0; i < nodesInLayer && placed < n; i++, placed++) {
      const angle = (i / nodesInLayer) * 2 * Math.PI;
      cluster[placed].lat = centerLat + r * Math.cos(angle);
      cluster[placed].lon = centerLon + r * Math.sin(angle);
    }

    layer++;
  }

  return cluster;
}

function spreadOverlappingNodesCircular(peers, radiusDeg = 0.5) {
  if (!peers || peers.length === 0) return peers;
  
  function roundCoord(coord, precision = 4) {
    return Math.round(coord * 10 ** precision) / 10 ** precision;
  }

  const clusters = {};
  peers.forEach(peer => {
    const key = `${roundCoord(peer.lat)},${roundCoord(peer.lon)}`;
    if (!clusters[key]) clusters[key] = [];
    clusters[key].push(peer);
  });

  Object.values(clusters).forEach(cluster => {
    if (cluster.length > 1) {
      spreadClusterCircle(cluster, radiusDeg);
    }
  });

  return peers;
}

function generateArcsData(peers, color = 'white') {
  if (!peers || peers.length === 0) return [];
  
  const arcs = [];

  for (let i = 0; i < peers.length; i++) {
    for (let j = 0; j < peers.length; j++) {
      if (i === j) continue;
      arcs.push({
        startLat: peers[i].lat,
        startLng: peers[i].lon,
        endLat: peers[j].lat,
        endLng: peers[j].lon,
        color: color
      });
    }
  }

  return arcs;
}

// Spread out the nodes in similar locations
spreadOverlappingNodesCircular(gElavationData, 10.5);

// Usage
let arcsData = generateArcsData(gElavationData);

const OPACITY = 0.6;
const getAlt = d => d.elevation * 5e-5;
const getTooltip = d => `
  <div style="text-align: center">
    <div><b>${d.name}</b></div>
  </div>
`;

const POINT_HEIGHT = 0.06;
const POINT_THICKNESS = 0.03;

const container = document.getElementById('globe-view');
const width = container.offsetWidth;
const height = container.offsetHeight;

fetch('../static/datasets/ne_110m_admin_0_countries.geojson')
  .then(res => res.json())
  .then(countries => {
    const world = new Globe(document.getElementById('globeViz'))
      .pointOfView({ lat: 39.6, lng: -98.5, altitude: 2 })
      .width(width)
      .height(height)
      .backgroundColor("black")
      .atmosphereColor("null")
      .atmosphereAltitude(0.0)
      .hexPolygonsData(countries.features)
      .hexPolygonResolution(3)
      .hexPolygonMargin(0.3)
      .hexPolygonUseDots(false)
      .hexPolygonColor(() => `grey`)
      .arcDashLength(0.25)
      .arcDashGap(1)
      .arcDashInitialGap(() => Math.random())
      .arcDashAnimateTime(4000)
      .arcColor(d => [`rgba(0, 255, 0, ${OPACITY})`, `rgba(255, 0, 0, ${OPACITY})`])
      .arcsTransitionDuration(0)
      .pointsMerge(true)
      .arcsData(arcsData)
      .pointLat('lat')
      .pointLng('lon')
      .pointAltitude(POINT_HEIGHT)
      .pointRadius(POINT_THICKNESS)
      .pointColor(d => 'white')
      .pointLabel(getTooltip)
      .labelLat('lat')
      .labelLng('lon')
      .labelAltitude(POINT_HEIGHT)
      .labelDotRadius(POINT_THICKNESS)
      .labelDotOrientation(() => 'bottom')
      .labelColor(d => 'white')
      .labelText('name')
      .labelSize(0.8)
      .labelResolution(1)
      .labelLabel(getTooltip)
      .pointsData(gElavationData)
      .labelsData(gElavationData);

    function resizeGlobe() {
      const container = document.getElementById('globe-view');
      const width = container.offsetWidth;
      const height = container.offsetHeight;
      world.width(width).height(height);
    }

    resizeGlobe();
    window.addEventListener('resize', resizeGlobe);

    // Expose update function globally for WebSocket updates
    window.updateGlobe = function(newData) {
      console.log("🌍 Updating globe with new data:", newData.length, "peers");
      
      if (!newData || newData.length === 0) {
        console.warn("No data to display on globe");
        return;
      }
      
      // Spread overlapping nodes
      const spreadData = spreadOverlappingNodesCircular([...newData], 10.5);
      
      // Generate new arcs
      const newArcs = generateArcsData(spreadData);
      
      console.log("Generated arcs:", newArcs.length);
      
      // Update globe data
      world
        .arcsData(newArcs)
        .pointsData(spreadData)
        .labelsData(spreadData);
      
      console.log("✅ Globe updated successfully");
    };

    // If data was loaded before globe initialized, update now
    if (window.gElavationData && window.gElavationData.length > 1) {
      console.log("Initial data available, updating globe");
      window.updateGlobe(window.gElavationData);
    }
  });