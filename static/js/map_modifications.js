import { mapState } from "./map_state.js";

let currentMarker = null; // To store the marker

export async function placeAddress(response) {
  /**
  * Places the submitted address on the map.
  * 
  * @param {response} - JSON response from `/fetch_all_data` with lat, lon
  * @returns {void} - Modifies the map in place by adding a marker 
  */
  // Input error handling
  if (!response) return;

  // Start by clearing the map (for when the user does another search)
  clearMap();
  resetButtons()
  clearBusRoutes(mapState.map);

  // Handle both string and object inputs
  const data = typeof response === 'string' ? JSON.parse(response) : response;

  // Check for different possible formats
  let coords = data.address_geojson.features[0].geometry.coordinates;

  // Display warning for not inside Hyde Park
  if (!data.has_data_inside_hyde_park) {
    showSearchError(data.notes)
  }

  const lat = parseFloat(coords[0]);
  const lon = parseFloat(coords[1]);

  // Enable map interaction
  const map = mapState.map;
  enableMapInteraction(map);

  // Move to the address
  map.flyTo({
    center: [lon, lat],
    zoom: 14
  });

  // Add marker
  currentMarker = new maplibregl.Marker({ color: 'tomato' })
    .setLngLat([lon, lat])
    .addTo(map);

    // Add a fixed maroon marker with popup for University of Chicago
    markUChicago();
}

function enableMapInteraction() {
  /**
    * Helper function to enable map interaction on a delay.
    * @param {void}, no inputs
    * @returns {void}, no return
  */
  const map = mapState.map;
  if (!map.dragPan.isEnabled()) map.dragPan.enable();
  if (!map.scrollZoom.isEnabled()) map.scrollZoom.enable();
  if (!map.boxZoom.isEnabled()) map.boxZoom.enable();
  if (!map.keyboard.isEnabled()) map.keyboard.enable();
  if (!map.doubleClickZoom.isEnabled()) map.doubleClickZoom.enable();
  if (!map.touchZoomRotate.isEnabled()) map.touchZoomRotate.enable();
  map.addControl(new maplibregl.NavigationControl(), 'bottom-right');
}

// Helper function to remove address and amenities markers
function clearMap() {
  if (currentMarker) {
    currentMarker.remove();
    currentMarker = null;
  }
  groceryMarkers = removeMarkers(groceryMarkers);
  busStopMarkers = removeMarkers(busStopMarkers);

}

// Helper function to deselect buttons
function resetButtons() {
  mapState.groceriesOn = false;
  mapState.busStopsOn = false;
  mapState.busRoutesOn = false;
  const groceriesBtn = document.getElementById('groceriesButton');
  const busStopsBtn = document.getElementById('busStopsButton');
  const busRoutesBtn = document.getElementById('busRoutesButton');
  if (groceriesBtn) groceriesBtn.classList.remove('is-success');
  if (busStopsBtn) busStopsBtn.classList.remove('is-info');
  if (busRoutesBtn) busRoutesBtn.classList.remove('is-warning');
}

function getDistanceFilter() {
  let filterSelect = document.getElementById("distanceFilter");
  return filterSelect ? parseInt(filterSelect.value) : 5;
}

let groceryMarkers = [];
let busStopMarkers = [];

function loadMarkersToMap(geojson, filterDistance, color, getPopupHTML) {
  /** Function to add markers to map given input data
   * @param {object} geojson - data stored as geoJSON
   * @param {int} filterDistance - distance to filter the map from
   * @param {string} color - strng color to implement
   * @param {string} getPopupHTML - HTML input for the pop-up hover
   * @returns {void} none - modifies object on map, not return 
   */
  const map = mapState.map;
  const markers = [];
  geojson.features.forEach(f => {
    // Extract properties
    let coords = f.geometry.coordinates;
    let props = f.properties;
    // Apply filter
    if (props.distance_min > filterDistance) return;
    // Popup
    let popup = new maplibregl.Popup({ offset: 25, closeButton: false }).setHTML(getPopupHTML(props));
    let marker = new maplibregl.Marker({ color: color }).setLngLat(coords).addTo(map);
    marker.getElement().addEventListener('mouseenter', () => popup.setLngLat(coords).addTo(map));
    marker.getElement().addEventListener('mouseleave', () => popup.remove());
    markers.push(marker);
  });
  return markers;
}

function removeMarkers(markers) {
  markers.forEach(m => m.remove());
  return [];
}

export function updateGroceries() {
  groceryMarkers = removeMarkers(groceryMarkers);
  const distanceMin = getDistanceFilter();
  console.log(mapState)
  groceryMarkers = loadMarkersToMap(
    mapState.groceryData.grocery_geojson,
    distanceMin,
    'seagreen',
    props => `<strong>${props.name}</strong><br>${props.address}`
  );
}

export function updateBusStops() {
  busStopMarkers = removeMarkers(busStopMarkers);
  const distanceMin = getDistanceFilter();
  busStopMarkers = loadMarkersToMap(
    mapState.busStopData.bus_stops_geojson,
    distanceMin,
    'deepskyblue',
    props => `<strong>${props.stop_name}</strong><br>Routes: ${props.routes.join(", ")}`
  );
}

export function toggleGroceries() {
  const groceriesBtn = document.getElementById('groceriesButton');
  mapState.groceriesOn = !mapState.groceriesOn;
  groceriesBtn.classList.toggle('is-success', mapState.groceriesOn);
  if (mapState.groceriesOn) {
    console.log("Groceries button turned ON");
    updateGroceries();
  } else {
    console.log("Groceries button turned OFF");
    groceryMarkers = removeMarkers(groceryMarkers);
  }
}

export function toggleBusStops() {
  const busStopsBtn = document.getElementById('busStopsButton');
  mapState.busStopsOn = !mapState.busStopsOn;
  busStopsBtn.classList.toggle('is-info', mapState.busStopsOn);
  if (mapState.busStopsOn) {
    console.log("BusStops button turned ON");
    updateBusStops();
  } else {
    console.log("BusStops button turned OFF");
    busStopMarkers = removeMarkers(busStopMarkers);
  }
}

// Bus routes
mapState.routes = {};

export function displayBusRoute(map, geojsonFeature) {
  /**
   * Function to display a bus route on the map
   * @param {maplibregl.Map} map - MapLibre map object
   * @param {object} geojsonFeature - GeoJSON MultiLineString Feature
   */
  const routeId = geojsonFeature.properties.route_id;
  if (!routeId || mapState.routes[routeId]) return;

  const sourceId = `bus-route-source-${routeId}`;
  const layerId = `bus-route-layer-${routeId}`;

  map.addSource(sourceId, {
      type: "geojson",
      data: {
          type: "FeatureCollection",
          features: [geojsonFeature]
      }
  });

  map.addLayer({
      id: layerId,
      type: "line",
      source: sourceId,
      paint: {
          "line-color": geojsonFeature.properties.color,
          "line-width": 4
      }
  });

  // Popups
  map.on('click', layerId, (e) => {
    const props = e.features[0].properties;
    new maplibregl.Popup({ closeButton: false, closeOnClick: true })
      .setLngLat(e.lngLat)
      .setHTML(`<strong>Route ${props.route_id}</strong>`)
      .addTo(map);
  });

  mapState.routes[routeId] = {sourceId, layerId};
}

export function removeBusRoute(map, routeId) {
  /** Function to remove a bus route from the map
   * @param {maplibregl.Map} map - MapLibre map object
   * @param {string} routeId - route identifier
   */
  const route = mapState.routes[routeId];
  if (!route) return;

  if (map.getLayer(route.layerId)) {
      map.removeLayer(route.layerId);
  }
  if (map.getSource(route.sourceId)) {
      map.removeSource(route.sourceId);
  }

  delete mapState.routes[routeId];
}

export function clearBusRoutes(map) {
  /** Function to clear all bus routes from the map (after button is toggled off)
   * @param {maplibregl.Map} map - MapLibre map object
   */
  Object.keys(mapState.routes).forEach(routeId => {
      removeBusRoute(map, routeId);
  });
  // Reset tracked routes
  mapState.routes = {};
}

export function toggleBusRoute(map, geojsonFeature) {
  const routeId = geojsonFeature.route_id;
  if (!routeId) return;

  if (mapState.routes[routeId]) {
      removeBusRoute(map, routeId);
  } else {
      displayBusRoute(map, geojsonFeature);
  }
}

/**
 * Marks the University of Chicago on the map with a maroon pin
 * and displays a fixed popup showing the name.
 */
function markUChicago() {
  const uchicagoCoords = [-87.5997, 41.7897]; 

  // Create a fixed popup with the name "University of Chicago"
  const popup = new maplibregl.Popup({
    closeButton: false,
    closeOnClick: false,
    offset: 40   
  })
    .setText("University of Chicago");

    // Add a maroon pin at UChicago coordinates and attach the popup
    new maplibregl.Marker({ color: '#800000' })  
    .setLngLat(uchicagoCoords)
    .setPopup(popup)
    .addTo(mapState.map);

    // Ensure the popup is visible immediately  
    popup.addTo(mapState.map);  
}




