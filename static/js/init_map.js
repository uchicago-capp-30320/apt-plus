// Import the shared map state object
import { mapState } from './map_state.js';

/**
 * Initializes a static MapLibre map for the login screens.
 *
 * This script checks for a DOM element with id="map" and ensures
 * the map is only initialized once using the shared `mapState` object.
 *
 * The map is non-interactive and centered on the University of Chicago.
 * Intended for use on basic login screens.
 */
document.addEventListener('DOMContentLoaded', () => {
  // Check if there is an element with id="map" on the page
  const mapContainer = document.getElementById('map');

  // If no map container exists, skip map initialization
  if (!mapContainer) {
    return;
  }

  // Prevent duplicate initialization if the map already exists (e.g., in home.html)
  if (mapState.map) {
    return;
  }

  // Initialize MapLibre map (STATIC at first)
  mapState.map = new maplibregl.Map({
    container: 'map',
    style: 'https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json',
    center: [-87.5995, 41.7925], 
    zoom: 13.6,
    interactive: false 
  });

});

