
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
    alert('Please enter an address.');
    return;
  }

  try {
    const response = await sendRequest(address);

    // Clean up the front page
    switchSearchViewLoading()

    // Check response 
    if (!response.ok) throw new Error(`Server responded with status ${response.status}`);

    // Parse data and place on map, assuming appropriate format from endpoint
    const data = await response.json();
    placeAddress(data);
  } catch (err) {
    console.error('Address request could not be resolved by Server:', err.message);
    alert('An error occurred while retrieving the apartment data.');
  }
}

async function sendRequest(address) {
  /** 
   * Sends a GET request for any address to the fetch_all_address endpoint
   * @param {string} address - compiled URL 
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
    rentSmarterBox.remove() // Will be reloaded if they refresh to this page, fine to delete
  }

  // Modifies the left panel
  const searchBox = document.getElementById("search-address-box");
  if (searchBox) {

    // Replace title
    const title = document.getElementById("search-box-title");
    title.textContent = "#### LongStreetName Type"; // Placeholder text for wrapping
    title.classList.add("is-skeleton","is-size-6-mobile","is-size-5-tablet","is-size-4-desktop");
    title.classList.remove("is-size-3-mobile","is-size-2-tablet","is-size-1-desktop"); // TODO refactor to utility function

    // Remove content below search bar
    const Content = document.getElementById('search-box-content')
    Content.remove()

    // Add control elements
    const saveButtonContainer = createElement('div', searchBox, ['mb-4']);
    const saveButton = createElement('button', saveButtonContainer, ['button', 'is-rounded', 'has-text-white', 'has-background-black']);
    saveButton.textContent = 'Save';
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
}

function createElement(type, parent, classes = [], id = null) {
  /** 
   * Utility function to create an element with styling and append it to a parent lement
   * @param {str} type - type of HTML element to create
   * @param {str} parent - parent element to append the newly created element to
   * @param {list} classes - list of classes to apply to elemenet
   * @param {str} id - OPTIONAL id attribute to apply
   * @returns {Element} - completed element returned to modify
  */
  const elem = document.createElement(type);

  // Option
  if (Array.isArray(classes)) elem.classList.add(...classes);
  if (id) elem.setAttribute('id', id);
  if (parent) parent.appendChild(elem);
  return elem;
}