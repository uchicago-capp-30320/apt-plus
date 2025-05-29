import { mapState } from "./map_state.js";
import { placeAddress } from "./map_modifications.js"

// Initialize cache for property status button
const propertyStatusCache = {};

export async function getApartment() {
  /**
    * Makes a GET request for the apartment and then updates the entire 
    * left panel of the app to display data from follow-up calls.
    * @param {void} 
    * @returns {void} - Sends a series of requests and modifies elements.
  */

  // Need this inside getApartment since we need this on submit
  const address = document.getElementById('addressInput').value.trim();

  // Data validation
  if (!address) {
    showSearchError('Please enter an address.'); // Use pop-up error handler to show validation error
    return;
  }
  
  // First clean up mapState as we've just started modifying the address state
  mapState.busStopData = null;
  mapState.groceryData = null;

  // Show loading spinner while waiting for response
  toggleLoadingWheel();
  let response, inspectionsPromise, groceriesPromise, busStopsPromise, routesPromise;

  try {
    response = await sendRequest('/fetch_all_data/', address); 
  
    // fetch_all_data returned an error - show popup error message 
    if (!response.ok) {
      const errorData = await response.json(); 
      const message = errorData.Error;
      showSearchError(message || 'Something went wrong.');

      // Clean up violations panel as relevant
      const violationsSummary = document.getElementById('violations-summary');
      const violationsIssues = document.getElementById('violations-issues');
      if (violationsSummary) {
        violationsSummary.innerText = '-';
        violationsIssues.classList.add('is-hidden');
      }

      return;
    }
  
    // Parse data and place on map, assuming appropriate format from endpoint
    const data = await response.json();
    const coord = data.address_geojson.features[0].geometry.coordinates;
    groceriesPromise = sendRequest('/fetch_groceries/', [coord, data['property_id']]); // start fetch_* requests ASAP
    busStopsPromise = sendRequest('/fetch_bus_stops/', [coord, data['property_id']]); 
    inspectionsPromise = sendRequest('/fetch_inspections/', data["cleaned_address"]);
    // let routesPromise = make_requests(data); // placeholder for routes endpoint
    
    placeAddress(data);
    switchSearchViewLoading(); // Clean up the front page and update left panel
    updateSearchView(data); // Pull in data from the response to update the overlay
  } catch (err) {
    console.error('Address request could not be resolved by Server:', err.message);
    showSearchError('An error occurred while retrieving the apartment data.'); // Use popup error handler to show network failure
   } finally {
    toggleLoadingWheel();
  }

   // Handle remaining calls
   try {
    const inspections = await inspectionsPromise; 
    updateViolations(inspections);
    const groceries = await groceriesPromise;
    const busStops = await busStopsPromise;
    mapState.groceryData = await groceries.json(); // Per 5/24 discussion add Globally-scoped Grocery data, to refactor
    mapState.busStopData = await busStops.json();  // Per 5/24 discussion add Globally-scoped Bus data, to refactor 

    // Send routes API call  
    const routes = await parse_busroutes(mapState.busStopData);
    routesPromise = sendRequest('/fetch_bus_routes/', routes.join(','));

    // update buttons
    document.querySelectorAll('#filter-buttons .button.is-loading').forEach(button => {
      if (button.id !== "busRoutesButton") {
        button.classList.remove('is-loading');
      }
    });
  } catch (err) {
    console.error('Details request could not be resolved by server:', err.message);
    showSearchError('An error occured while retrieving apartment details. Please try again.');
  }

  // Save route data
  try {
    const busRoutes = await routesPromise;
    mapState.busRoutesData = await busRoutes.json();
    document.querySelectorAll('#filter-buttons .button.is-loading').forEach(button => {
      if (button.id === "busRoutesButton") {
        button.classList.remove('is-loading');
      }
    });
  } catch (err) {
    console.error('Details request could not be resolved by server:', err.message);
    showSearchError('An error occured while retrieving bus route details. Please try again.');
  }
}

async function sendRequest(endpoint, body) {
  /** 
   * Sends a GET request for any address to a fetch endpoint
   * @param {string} endpoint - endpoint to direct
   * @param {string} body - address or lat/lon to add into the compiled URL 
   * @returns {Promise<response>} returns the promise object of the get request
  */

  // Construct GET request
  const url = new URL(endpoint, window.location.origin);
  if (endpoint==='/fetch_all_data/' || endpoint==='/fetch_inspections/') {
    url.searchParams.append('address', body);
  } else if (endpoint==='/fetch_bus_routes/') {
    url.searchParams.append('bus_route', body);
  } else {
      url.searchParams.append('geocode', body[0]);
      url.searchParams.append('property_id', body[1]); 
      url.searchParams.append('walking_time', 15);
  }

  // Send the request and then store it as a variable so we can operate on the DOM
  return fetch(url, { method: 'GET' });
}

async function parse_busroutes(data) {
  /** Takes the fetch_routes output and produces a list of unique routes.
   *  @param {Object} data - a JSON formatted list of responses.
   *  @returns {array} routes - a list of unique bus routes to request 
  */
  let routes = []; 
  for (const elem of data.bus_stops_geojson.features) {
    routes = routes.concat(elem.properties.routes); // ['171', '55']
  } 
  return [...new Set(routes)]; // ref: https://stackoverflow.com/a/9229821
}

function switchSearchViewLoading() {
  /**
    * Modifies the main page view with placeholder information after a request 
    * is sent to the fetch_all_data endpoint.
    * @param {void}  
    * @returns {void} 
  */

  // Remove right panel box
  const rentSmarterBox = document.getElementById("rent-smarter-box");
  if (rentSmarterBox) {
    rentSmarterBox.remove(); // Will be reloaded if they refresh to this page, fine to remove
  }

  // Fully update the left panel if the landing page Search Bar content exists
  const content = document.getElementById('search-box-content')
  if (content) { 
    initialSearchViewUpdate();
  } else {
    // Wipe elements for new search
    const title = document.getElementById("search-box-title");
    title.textContent = "#### LongStreetName Type"; // Placeholder text for wrapping
    title.classList.add("is-skeleton");

    // Wipe violations for new search
    const violationsSummary = document.getElementById('violations-summary');
    const violationsIssues = document.getElementById('violations-issues');
    violationsSummary.innerText = '';
    violationsSummary.classList.add('skeleton-lines');
    violationsIssues.classList.add('skeleton-lines');

    // Add formatting for skeleton lines
    const violationsIds = [
      'violationsNote',
      'violationsTotal',
      'violationsInspections',
      'violationsStartDate'
    ];
    violationsIds.forEach(id => {
      createElement('div', violationsSummary, [], id);
    }); 
  }
}

function initialSearchViewUpdate() {
  /** Function to swap out the landing page elements with search elements.
   *  Moves vertically through the box to modify, delete, then add content.
  * @returns {void} - modifies the DOM, no returned object
  */
    const searchBox = document.getElementById('search-address-box')
    const searchBar = document.getElementById('search-box-bar')
    const content = document.getElementById('search-box-content')
    content.remove()

    // Replace title to placeholder text
    const title = document.getElementById("search-box-title");
    title.textContent = "#### LongStreetNameMaxLen Type"; // Placeholder text for wrapping, 30 char max in the DB
    title.classList.add("is-skeleton","is-size-6-mobile","is-size-5-tablet","is-size-4-desktop", 'mb-0');
    title.classList.remove("is-size-3-mobile","is-size-2-tablet","is-size-1-desktop");
    
    // Add subtitle under
    const subtitle = createElement('p', null, ['is-size-7', 'is-skeleton'], 'search-box-subtitle')
    searchBox.insertBefore(subtitle, searchBar)

    // Add save button elements
    const saveButtonContainer = createElement('div', searchBox, ['mb-4', 'slide-it'], 'save-button-container');
    const placeholderButton = createElement('button', saveButtonContainer, 
      ['button', 'is-rounded', 'is-loading'], 'placeholder-button');
    placeholderButton.textContent = 'Checking status...';
    
    // Update filters section
    const filtersTemplate = document.getElementById("filters-template").innerHTML;
    const filters = createElement('div', searchBox, ['media', 'mb-4']);
    filters.innerHTML = filtersTemplate;
     
    // Update content with inspections
    const violations = createElement('div', searchBox, ['media']);
    const violationsIcon = createElement('div', violations, ['media-left']);
    const violationsIconSpan = createElement('span', violationsIcon, ['icon']);
    const violationsIconFa = createElement('i', violationsIconSpan, ['fas','fa-exclamation-triangle','fa-lg'])
    const violationsDesc = createElement('div', violations, ['media-content']);
    const violationsTitle = createElement('p', violationsDesc, ['has-text-weight-bold', 'mb-2']);
    violationsTitle.textContent = "Code Violations";
    
    // Summary containers
    const violationsSummary = createElement('div', violationsDesc, ['has-text-justified', 'is-size-6', 'skeleton-lines', 'mb-2'], 'violations-summary');
    const violationsIssues = createElement('div', violationsDesc, ['box', 'has-background-light', 'mt-2', 'p-3', 'violations-box', 'skeleton-lines'], 'violations-issues');
  
     // Fill summary containers with named and anonymous lines
     const violationsIds = [
       'violationsNote',
       'violationsTotal',
       'violationsInspections',
       'violationsStartDate'
     ];
     violationsIds.forEach(id => {
       createElement('div', violationsSummary, [], id);
     }); 
     for (let i = 0; i < 10; i++) {
       createElement('div', violationsIssues);
     }
   }

function updateSearchView(data) {
  /** Updates the loading text for the title basd on the returned GET response.
   *  @param {Object} data - JSON object from GET response to update the search view with. 
   *  @returns {void} - returns nothing, just updates the DOM as relevant.
  */
  // First, extract address parts from the `fetch_all_data` reponse
  let address_parts = data["cleaned_address"].split(/,(.*)/s); // Ref: https://stackoverflow.com/a/4607799

  const title = document.getElementById("search-box-title");
  mapState.address = data["cleaned_address"];
  mapState.geocode = data.address_geojson.features[0].geometry.coordinates;
  title.innerText = toTitleCase(address_parts[0]);
  title.classList.remove("is-skeleton");

  const subtitle = document.getElementById("search-box-subtitle");
  subtitle.innerText = toTitleCase(address_parts[1]);
  subtitle.classList.remove("is-skeleton");

  // Collect buttons and add loading
  document.querySelectorAll('#filter-buttons .button').forEach(button => {
    button.classList.add('is-loading');
  });

  // Check if the property is already saved
  checkPropertyStatus(data["cleaned_address"]);
}

// Add this new function to check property status and update the button accordingly
async function checkPropertyStatus(propertyAddress) {
  // Only proceed if container exists
  const saveButtonContainer = document.getElementById("save-button-container");
  if (!saveButtonContainer) return;

  try {
    // Check cache first
    if (propertyStatusCache[propertyAddress] !== undefined) {
      console.log("Using cached property status");
      updateButtonBasedOnStatus(
        propertyAddress, 
        propertyStatusCache[propertyAddress], 
        saveButtonContainer
      );
      return;
    }

    // Make request to check if property is saved
    const url = new URL('/check_property_status/', window.location.origin);
    url.searchParams.append('property_address', propertyAddress);

    const response = await fetch(url);
    const data = await response.json();

    // Store in cache
    propertyStatusCache[propertyAddress] = data.is_saved;

    // Update the button
    updateButtonBasedOnStatus(propertyAddress, data.is_saved, saveButtonContainer);
  } catch (error) {
    console.error("Error checking property status:", error);
    // Show default save button on error
    updateButtonBasedOnStatus(propertyAddress, false, saveButtonContainer);
  }
}

async function updateViolations(response) {
  /** Function to update the violations panel of the frontend
   * @param {Promise<object>} response - response object from `/fetch_violations/`
   * @returns {void} - modifies violations data directly.
  */
  const data = await response.json();

  // Update violations panel to display information
  const violationsSummary = document.getElementById('violations-summary');
  const violationsIssues = document.getElementById('violations-issues');
  violationsSummary.classList.remove("skeleton-lines");
  violationsIssues.classList.remove("skeleton-lines", 'is-hidden');
  // ref: https://stackoverflow.com/a/3955238
  while (violationsIssues.firstChild) { // Removes empty divs used for loading styling
    violationsIssues.removeChild(violationsIssues.lastChild);
  }
  
  // Add in data to display response issues by format
  violationsSummary.innerText = data['summary'];
  if (data['data_status'] == "available") { // Only add issues list if they exist
    let i = 0;
    for (const elemTime of data.summarized_issues) {
      const time = createElement('p', violationsIssues, [`has-text-weight-bold`, `is-size-7`],  `time${i}`);
      time.innerText = elemTime['date'];
      
      const list = createElement('ul', violationsIssues, [`is-size-7`], `list${i}`);
      let j = 0;
      for (const elemIssue of elemTime['issues']) {
        const issue = createElement('li', list, null, `item${j}`);
        issue.innerText = elemIssue['emoji'] + elemIssue['description'];
        j++;
      }
      i++;
    }
  } else {
    violationsIssues.classList.add('is-hidden');
  }
}

// Extract button creation to a separate function
function updateButtonBasedOnStatus(propertyAddress, isSaved, container) {
  // Clear the container
  container.innerHTML = '';
  if (isSaved) {
    // Add status notification 
    const statusNote = createElement('div', container, ['notification', 'is-info', 'is-light', 'py-2', 'px-3', 'mb-2'], 'saved-status');
    statusNote.innerHTML = '<span class="icon-text"><span class="icon"><i class="fas fa-bookmark"></i></span> <span>This property is in your saved list</span></span>';

    // Property is saved - show delete button
    const deleteButton = createElement('button', container, 
      ['button', 'is-danger', 'is-outlined', 'is-rounded'], 'delete-button');
    // Add icon and text as children
    const iconSpan = createElement('span', deleteButton, ['icon', 'is-small']);
    const icon = createElement('i', iconSpan, ['fas', 'fa-trash']);
    const textSpan = createElement('span', deleteButton);
    textSpan.textContent = 'Remove';

    // Add HTMX attributes for delete
    deleteButton.setAttribute('hx-post', '/delete_property/');
    deleteButton.setAttribute('hx-vals', `js:{property_address: "${propertyAddress}"}`);
    deleteButton.setAttribute('hx-target', '#save-button-container');
    deleteButton.setAttribute('hx-trigger', 'click');
    deleteButton.setAttribute('hx-swap', 'outerHTML transition:true');

    // Tell HTMX to process the button
    htmx.process(deleteButton);
  } else {
    // Property is not saved - show save button
    const saveButton = createElement('button', container, 
      ['button', 'is-rounded', 'has-text-white', 'has-background-black'], 'save-button');

    // Add icon and text as children
    const iconSpan = createElement('span', saveButton, ['icon', 'is-small']);
    const icon = createElement('i', iconSpan, ['fas', 'fa-bookmark']);
    const textSpan = createElement('span', saveButton);
    textSpan.textContent = 'Save to my list';

    // Add HTMX attributes for save
    saveButton.setAttribute('hx-post', '/save_property/');
    saveButton.setAttribute('hx-vals', `js:{propertyAddress: "${propertyAddress}"}`);
    saveButton.setAttribute('hx-target', '#save-button-container');
    saveButton.setAttribute('hx-trigger', 'click'); 
    saveButton.setAttribute('hx-swap', 'outerHTML transition:true');

    // Tell HTMX to process the button
    htmx.process(saveButton);
  }
}

function toggleLoadingWheel() {
  /** Add a loader to the searchBox
    * @params {none} - no inputs 
    * @returns {void} - modifies the DOM directly, does not modify div
  */

  // First check if a loader exists, then remove if so
  const existingLoadingWheel = document.getElementById("loading-wheel");
  if (existingLoadingWheel) {
    existingLoadingWheel.remove();
    return;
  } else {
    const searchBox = document.getElementById("search-address-box");
    const overlay = createElement("div", null, ["loader-overlay"], "loading-wheel");
    const loadingWheel = createElement("div", overlay, ["loader"]);
    searchBox.appendChild(overlay);
    return;
  }
}