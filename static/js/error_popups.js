/**
 * Displays an error message directly below the search bar, inside the same box.
 * Uses Bulma's 'help is-danger' class and adds spacing below.
 * @param {string} message - The error message to show
 * @returns {void}
 */
function showSearchError(message) {
    // Get the search bar container
    const searchBar = document.getElementById('search-box-bar');
  
    // Remove any existing error
    clearSearchError();
  
    // Create the error message element
    const error = document.createElement('p');
    error.classList.add('help', 'is-danger', 'mb-3');
    error.id = 'search-error-message';
    error.textContent = message;
  
    // Insert the error directly after the search bar
    searchBar.insertAdjacentElement('afterend', error);
  }
  
  /**
   * Removes the search error message, if it exists.
   * @returns {void}
   */
  function clearSearchError() {
    const existingError = document.getElementById('search-error-message');
    if (existingError) {
      existingError.remove();
    }
  }
  
  // Clear error dynamically when user types in address bar
  document.addEventListener('DOMContentLoaded', () => {
    const addressInput = document.getElementById('addressInput');
    if (addressInput) {
      addressInput.addEventListener('input', () => {
        clearSearchError();
      });
    }
  });
