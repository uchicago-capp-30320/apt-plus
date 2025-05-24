// Enable View Transitions for HTMX if the browser supports it
document.addEventListener('DOMContentLoaded', function() {
  if ('startViewTransition' in document) {
    htmx.config.globalViewTransitions = true;
    console.log("View Transitions API is supported and enabled");
  } else {
    console.log("View Transitions API is not supported in this browser");
  }

  // Check if we're returning from login with property address
  const returnAddress = localStorage.getItem('returnToProperty');
  if (returnAddress) {
    console.log("Returning to property view:", returnAddress);
    
    // Clear the stored address
    localStorage.removeItem('returnToProperty');
    
    // Wait for DOM to be fully loaded
    setTimeout(function() {
      // Set the address in the search input
      const addressInput = document.getElementById('addressInput');
      if (addressInput) {
        addressInput.value = returnAddress;
        
        // Trigger search
        const searchButton = document.querySelector('#search-box-bar .button');
        if (searchButton) {
          searchButton.click();
        }
      }
    }, 500);
  }
});

async function getApartment() {
  /**
    * Makes a GET request for the apartment and then updates the DOM to 
    * prepare for loading the data.
    * @param {void}  
    * @returns {void} - Sends the request 
  */

  // Need this inside getApartment since we need this on submit
  const address = document.getElementById('addressInput').value.trim();

  // Data validation
  if (!address) {
    showSearchError('Please enter an address.'); // Use popup error handler to show validation error
    return;
  }

  try {
    // Show loading spinner while waiting for response
    toggleLoadingWheel();
  
    // Send GET request to fetch_all_data
    const response = await sendRequest(address); 
  
  
    // fetch_all_data returned an error — show popup error message 
    if (!response.ok) {
      const errorData = await response.json(); 
      const message = errorData.Error;
      showSearchError(message || 'Something went wrong.');
      return;
    }
  
    // Parse data and place on map, assuming appropriate format from endpoint
    const data = await response.json();
    placeAddress(data);

    // Clean up the front page and update left panel
    switchSearchViewLoading();

    // Pull in data from the response to update the overlay
    updateSearchView(data);

    // Clear error message if everything worked
    clearSearchError(); 
  } catch (err) {
    console.error('Address request could not be resolved by Server:', err.message);
    toggleLoadingWheel(); //Ensure spinner is removed even on failure
    showSearchError('An error occurred while retrieving the apartment data.'); //Use popup error handler to show network failure
  } finally {
    // Stop spinner after response received
    toggleLoadingWheel();
  }
}

async function sendRequest(address) {
  /** 
   * Sends a GET request for any address to the fetch_all_address endpoint
   * @param {string} address - address to add into the compiled URL 
   * @returns {Promise<response>} returns the promise object of the get request
  */

  // Construct GET request
  const url = new URL('/fetch_all_data/', window.location.origin);
  url.searchParams.append('address', address);

  // Send the request and then store it as a variable so we can operate on the DOM
  return fetch(url, { method: 'GET' });
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

    const violationsSummary = getElementById('violations-summary');
    const violationsIssues = getElementById('violations-summary');
    violationsSummary.classList.add('skeleton-lines');
    violationsIssues.classList.add('skeleton-lines');
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

    // Add control elements
    const saveButtonContainer = createElement('div', searchBox, ['mb-4', 'slide-it'], 'save-button-container');
    const saveButton = createElement('button', saveButtonContainer, ['button', 'is-rounded', 'has-text-white', 'has-background-black'], 'save-button');
    saveButton.textContent = 'Save to my list';

    console.log("HTMX available:", typeof htmx !== 'undefined');
    console.log("Save button created:", saveButton);

    // Add HTMX attributes to the save button
    saveButton.setAttribute('hx-get', '/save_property/');
    saveButton.setAttribute('hx-target', '#save-button-container');
    saveButton.setAttribute('hx-trigger', 'click');
    saveButton.setAttribute('hx-swap', 'outerHTML transition:true');
    // HTMX will scan for attributes and add event listeners
    // Without this, dynamically created content is incompatible with HTMX
    htmx.process(saveButton);

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
    const violationsSummary = createElement('div', violationsDesc, ['has-text-justified', 'is-size-7', 'skeleton-lines', 'mb-2'], 'violations-summary');
    const violationsIssues = createElement('div', violationsDesc, ['box', 'has-background-light', 'mt-2', 'p-3', 'violations-box', 'skeleton-lines'], 'violations-summary');
  
     // Fill summary containers with named and anonymous lines
     const violationsIds = [
       'violationsSummary',
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
   *  @param {json} data - GET response object to update the search view with. 
   *  @returns {void} - returns nothing, just updates the DOM as relevant.
  */
  // First, extract address parts from the `fetch_all_data` reponse
  address_parts = data["cleaned_address"].split(/,(.*)/s); // Ref: https://stackoverflow.com/a/4607799
  
  const title = document.getElementById("search-box-title");
  title.dataset.address = data["cleaned_address"];
  title.innerText = toTitleCase(address_parts[0]);
  title.classList.remove("is-skeleton");

  const subtitle = document.getElementById("search-box-subtitle");
  subtitle.innerText = toTitleCase(address_parts[1]);
  subtitle.classList.remove("is-skeleton")

  // Update the Save button's HTMX properties now that we have the address 
  const saveButton = document.getElementById("save-button");
  if (saveButton) {
    // Update the hx-vals attribute with the actual address now that we have it
    saveButton.setAttribute('hx-vals', `js:{propertyAddress: "${data["cleaned_address"]}"}`);
    // Process the button since attributes were updated
    htmx.process(saveButton);
    
    // For debugging: log that we updated the button
    console.log("Save button updated with address:", data["cleaned_address"]);
    
  } else {
    console.warn("Save button not found when updating address data");
  }
}

function toggleLoadingWheel() {
  /** Add a loader to the searchBox
    * @returns {void} - modifies the DOM directly, does not modify div
  */

  // First check if a loader exists, then remove if so
  const existingLoadingWheel = document.getElementById("loading-wheel");
  if (existingLoadingWheel) {
    existingLoadingWheel.remove();
    return;
  }

  // If no loader, create loader
  const searchBox = document.getElementById("search-address-box");

  // Create overlay and loader
  const overlay = createElement("div", null, ["loader-overlay"], "loading-wheel")
  const loadingWheel = createElement("div", overlay, ["loader"]);

  // Link the overlay in the center of the underlaid object
  searchBox.appendChild(overlay);
  return;
}
