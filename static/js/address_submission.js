
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
    * Modifies the main page view after the GET request is sent with
    * placeholder information.
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
    const searchBoxTitle = document.getElementById("search-box-title");
    searchBoxTitle.textContent = "#### LongStreetName Type"; // Placeholder text for wrapping
    searchBoxTitle.classList.add("is-skeleton","is-size-6-mobile","is-size-5-tablet","is-size-4-desktop");
    searchBoxTitle.classList.remove("is-size-3-mobile","is-size-2-tablet","is-size-1-desktop"); // TODO refactor to utility function

    // Add button to search
    const saveButtonContainer = document.createElement('div');
    const saveButton = document.createElement('button');
    saveButtonContainer.className = 'mb-4';
    saveButton.className = 'button is-rounded has-text-white has-background-black';
    saveButton.textContent = 'Save';
    saveButtonContainer.appendChild(saveButton);

    const searchBoxContent = document.getElementById("search-box-content"); // location
    searchBox.insertBefore(saveButtonContainer, searchBoxContent);

    // Add filters panel
    const searchBoxFilters = document.createElement('div');
    const filtersTemplate = document.getElementById("filters-template").innerHTML; // loaded from Django templates in main.html
    searchBoxFilters.classList.add("media", "mb-4");
    searchBoxFilters.innerHTML = filtersTemplate;
    searchBox.insertBefore(searchBoxFilters, searchBoxContent);

    // Update content with inspections
    // To-do: 
    //    - remove content
    //    - add box with scroll bar, but skeleton-lines text
    searchBoxContent.innerHTML = `
    <!-- Code Violations Section -->
    <div class="media">
      <div class="media-left">
        <span class="icon" style="color: #DB0B0B;">
          <i class="fas fa-exclamation-triangle fa-lg"></i>
        </span>
      </div>
      <div class="media-content">
        <p><strong>Code Violations</strong></p>
        <br>
        <!-- JSON Key:"Summary" -->
          <p class="has-text-justified"><small>This building has received complaints about heating issues, hot water problems, and maintenance concerns in the past 5 years.</small></p>

          <!-- Json Key:"Note" -->
          <p class="has-text-justified mt-2 is-size-7"><em>*Note:</em> Unauthorized uses and cases where inspectors were denied entry were omitted.</p>

          <!-- Stats -->
          <p class="mt-2 mb-2">
            <small>
              <!-- JSON key:"total_violations_count" -->
              <strong>Total Violations:</strong> 12 |
                <!-- JSON key:"total_inspections_count" -->
              <strong>Total Inspections:</strong> 2 |
                <!-- JSON key:"start_date" -->
              <strong>Since:</strong> Jan 2020
            </small>
          </p>

          <!-- JSON key: "summarized_issues" -->
          <div class="box has-background-light p-3" style="max-height: 150px; overflow-y: auto;">

            <!-- JSON key:"date" -->
            <p class="has-text-weight-semibold is-size-7">Jan 2024</p>
            <ul class="ml-4 mb-3 is-size-7">
              <!-- JSON key:"issues" -->
              <!-- JSON key:"emoji" and key:"description" -->
              <li>🌡️ Inadequate heating and drafty windows with air seepage in Units 102, 103, and 104</li>
              <li>🚿 Hot water issues with low temperature (45-59°F) and low pressure in Units 102, 103, 104, and 205</li>
            </ul>

            
            <p class="has-text-weight-semibold is-size-7">Oct 2023</p>
            <ul class="ml-4 is-size-7">
              <li>🗑️ Overfilled trash cans and bags on the ground at west elevation</li>
            </ul>

              
            <p class="has-text-weight-semibold is-size-7">Jan 2024</p>
            <ul class="ml-4 mb-3 is-size-7">
              <li>🌡️ Inadequate heating and drafty windows with air seepage in Units 102, 103, and 104</li>
              <li>🚿 Hot water issues with low temperature (45-59°F) and low pressure in Units 102, 103, 104, and 205</li>
            </ul>

            
            <p class="has-text-weight-semibold is-size-7">Oct 2023</p>
            <ul class="ml-4 is-size-7">
              <li>🗑️ Overfilled trash cans and bags on the ground at west elevation</li>
            </ul>

    </div>
  `;

      //Reconnect searchButton after replacing the HTML
    document.getElementById("searchButton").addEventListener("click", getApartment);
  }
}
