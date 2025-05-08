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

    // Placeholder for DOM modification

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