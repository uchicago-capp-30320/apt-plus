/*-----------------------------------------------------------------------------
 Utility Functions
------------------------------------------------------------------------------*/
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

  // A couple references below for how to handle if the class Array is empty:
  // Ref: https://matcha.fyi/javascript-optional-chaining/
  // Ref: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Spread_syntax
  if (classes?.length) elem.classList.add(...classes); 
  if (id) elem.id = id;
  if (parent) parent.appendChild(elem);
  return elem;
}

function toTitleCase(str) {
  /**
   * Function to convert text to title case
   * @param {string} str - string to convert to Title case
   * Note: From: https://stackoverflow.com/a/196991
  */
  return str.replace(/[^-\s]+/g, s => s.charAt(0).toUpperCase() + s.substring(1).toLowerCase());
}


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
