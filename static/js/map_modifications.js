  // Initialize MapLibre map (STATIC at first)
  const map = new maplibregl.Map({
    container: 'map',
    style: 'https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json',
    center: [-87.5995, 41.7925],
    zoom: 13.6,
    interactive: false
  });

  let currentMarker = null; // To store the marker

  async function placeAddress(response) {
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

    // Handle both string and object inputs
    const data = typeof response === 'string' ? JSON.parse(response) : response;

    // Check for different possible formats
    let coords = data.address_geojson.features[0].geometry.coordinates;

    // Display warning for not inside Hyde Park
    console.log(data)
    if (!data.has_data_inside_hyde_park) {
      showSearchError(data.notes)
    }

    const lat = parseFloat(coords[0]);
    const lon = parseFloat(coords[1]);

    // Enable map interaction
    enableMapInteraction(map);

    // Move to the address
    map.flyTo({
      center: [lon, lat],
      zoom: 15
    });

    // Add marker
    currentMarker = new maplibregl.Marker({ color: 'yellow' })
      .setLngLat([lon, lat])
      .addTo(map);
  }

  function enableMapInteraction(map) {
    /**
      * Helper function to enable map interaction on a delay.
      * 
      * @param {map} - map object to enable interactions
      * @returns {void}, no return
    */
    if (!map.dragPan.isEnabled()) map.dragPan.enable();
    if (!map.scrollZoom.isEnabled()) map.scrollZoom.enable();
    if (!map.boxZoom.isEnabled()) map.boxZoom.enable();
    if (!map.keyboard.isEnabled()) map.keyboard.enable();
    if (!map.doubleClickZoom.isEnabled()) map.doubleClickZoom.enable();
    if (!map.touchZoomRotate.isEnabled()) map.touchZoomRotate.enable();
    map.addControl(new maplibregl.NavigationControl(), 'bottom-right');
  }

  // Helper function to remove address marker
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
    groceriesON = false;
    busStopsON = false;
    const groceriesBtn = document.getElementById('groceriesButton');
    const busStopsBtn = document.getElementById('busStopsButton');
    if (groceriesBtn) groceriesBtn.classList.remove('is-info');
    if (busStopsBtn) busStopsBtn.classList.remove('is-info');
  }

  function getDistanceFilter() {
    let filterSelect = document.getElementById("distanceFilter");
    return filterSelect ? parseInt(filterSelect.value) : 5;
  }

  let groceryMarkers = [];
  let busStopMarkers = [];
  let groceriesON = false;
  let busStopsON = false;

  const groceryData = {
    "address": "123 Main St",
    "walking_time": 5,
    "grocery_geojson": {
      "type": "FeatureCollection",
      "features": [
        {
          "type": "Feature",
          "geometry": { "type": "Point", "coordinates": [-87.587851, 41.801710] },
          "properties": { "name": "Whole Foods", "distance_min": 4, "address": "1521 E Hyde Park Blvd" }
        },
        {
          "type": "Feature",
          "geometry": { "type": "Point", "coordinates": [-87.588746, 41.796868] },
          "properties": { "name": "Trader Joe's", "distance_min": 6, "address": "55th & Lake Park" }
        }
      ]
    }
  };

  const busStopData = {
    "address": "123 Main St",
    "walking_time": 5,
    "bus_stops_geojson": {
      "type": "FeatureCollection",
      "features": [
        {
          "type": "Feature",
          "geometry": { "type": "Point", "coordinates": [-87.5960, 41.7942] },
          "properties": {
            "stop_name": "Lake Park & 56th",
            "distance_min": 13,
            "routes": ["2", "6", "28"],
            "stop_id": "BUS12345"
          }
        },
        {
          "type": "Feature",
          "geometry": { "type": "Point", "coordinates": [-87.5911, 41.8005] },
          "properties": {
            "stop_name": "Hyde Park & 53rd",
            "distance_min": 4,
            "routes": ["15", "55"],
            "stop_id": "BUS67890"
          }
        }
      ]
    }
  };

  function loadMarkersToMap(geojson, filterDistance, color, getPopupHTML) {
    const markers = [];
    geojson.features.forEach(f => {
      // Extract properties
      let coords = f.geometry.coordinates;
      let props = f.properties;
      // Apply filter
      if (props.distance_min > filterDistance) return;
      // Popup
      let popup = new maplibregl.Popup({ offset: 25 }).setHTML(getPopupHTML(props));
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

  function updateGroceries() {
    groceryMarkers = removeMarkers(groceryMarkers);
    const distanceMin = getDistanceFilter();
    groceryMarkers = loadMarkersToMap(
      groceryData.grocery_geojson,
      distanceMin,
      'green',
      props => `<strong>${props.name}</strong><br>${props.address}`
    );
  }

  function updateBusStops() {
    busStopMarkers = removeMarkers(busStopMarkers);
    const distanceMin = getDistanceFilter();
    busStopMarkers = loadMarkersToMap(
      busStopData.bus_stops_geojson,
      distanceMin,
      'blue',
      props => `<strong>${props.stop_name}</strong><br>Routes: ${props.routes.join(", ")}`
    );
  }

  function toggleGroceries() {
    const groceriesBtn = document.getElementById('groceriesButton');
    groceriesON = !groceriesON;
    groceriesBtn.classList.toggle('is-info', groceriesON);
    if (groceriesON) {
      console.log("Groceries button turned ON");
      updateGroceries();
    } else {
      console.log("Groceries button turned OFF");
      groceryMarkers = removeMarkers(groceryMarkers);
    }
  }

  function toggleBusStops() {
    const busStopsBtn = document.getElementById('busStopsButton');
    busStopsON = !busStopsON;
    busStopsBtn.classList.toggle('is-info', busStopsON);
    if (busStopsON) {
      console.log("BusStops button turned ON");
      updateBusStops();
    } else {
      console.log("BusStops button turned OFF");
      busStopMarkers = removeMarkers(busStopMarkers);
    }
  }