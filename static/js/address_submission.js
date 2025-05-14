
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
    switchSearchView()

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


function switchSearchView() {
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
    const Title = document.getElementById("search-box-title");
    Title.textContent = "#### LongStreetName Type"; // Placeholder text for wrapping
    Title.classList.add("is-skeleton","is-size-6-mobile","is-size-5-tablet","is-size-4-desktop");
    Title.classList.remove("is-size-3-mobile","is-size-2-tablet","is-size-1-desktop"); // TODO refactor to utility function

    // Remove content below search bar
    const Content = document.getElementById('search-box-content')
    Content.remove()

    // Add button to search
    const saveButtonContainer = document.createElement('div');
    saveButtonContainer.classList.add('mb-4');
    searchBox.appendChild(saveButtonContainer);

    const saveButton = document.createElement('button');
    saveButton.classList.add('button', 'is-rounded','has-text-white','has-background-black');
    saveButton.textContent = 'Save';
    saveButtonContainer.appendChild(saveButton);

    // Add filters panel
    const Filters = document.createElement('div');
    const filtersTemplate = document.getElementById("filters-template").innerHTML; // loaded from Django templates in main.html
    Filters.classList.add("media", "mb-4"); // TODO: Should this be a media element?
    Filters.innerHTML = filtersTemplate;
    searchBox.appendChild(Filters);

    // Update content with inspections
    // To-do: 
    //    - remove content
    //    - add box with scroll bar, but skeleton-lines text
    const Violations = document.createElement('div');
    Violations.classList.add("media");
    searchBox.appendChild(Violations);

    const ViolationsIcon = document.createElement('div');
    ViolationsIcon.classList.add("media-left");
    ViolationsIcon.innerHTML = `<span class="icon" style="color: #DB0B0B;"><i class="fas fa-exclamation-triangle fa-lg"></i></span>`
    Violations.appendChild(ViolationsIcon)

    const ViolationsDesc = document.createElement('div');
    ViolationsDesc.classList.add("media-content");
    Violations.appendChild(ViolationsDesc)

    const ViolationsTitle = document.createElement('p');
    ViolationsTitle.classList.add('has-text-weight-bold', 'mb-2');
    ViolationsTitle.textContent = "Code Violations";
    ViolationsDesc.appendChild(ViolationsTitle);

    // Violations
    const ViolationsSummary = document.createElement('div');
    ViolationsSummary.classList.add('has-text-justified', 'is-size-7', 'skeleton-lines', 'mb-2');
    ViolationsSummary.setAttribute('id', 'violations-summary');
    ViolationsDesc.appendChild(ViolationsSummary);
    
    // Fill with five skeleton lines to update based on API call
    const violationsIds = [
      'violationsSummary',
      'violationsNote',
      'violationsTotal',
      'violationsInspections',
      'violationsStartDate'
    ];

    // Create and append each div
    for (const id of violationsIds) {
      const div = document.createElement('div');
      div.setAttribute('id', id);
      ViolationsSummary.appendChild(div);
    }

    // Violations
    const ViolationsIssues = document.createElement('div');
    ViolationsIssues.classList.add('box', 'has-background-light', 'mt-2', 'p-3', 'violations-box', 'skeleton-lines');
    ViolationsIssues.setAttribute('id', 'violations-summary');
    ViolationsDesc.appendChild(ViolationsIssues);
  
    // Final
    for (let i = 0; i < 10; i++) {
      const line = document.createElement('div');
      ViolationsIssues.appendChild(line);
    } 
  }
}
