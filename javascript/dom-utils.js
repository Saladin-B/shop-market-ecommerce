/**
 * DOM Utilities & Helpers
 * Purpose: General utility functions for DOM manipulation and browser features
 * Used in: All pages as needed
 */

/**
 * Add Class to Element
 * Purpose: Helper to add single or multiple CSS classes
 * @param {HTMLElement} element - Target element
 * @param {string|array} classes - Class name(s) to add
 */
function addClass(element, classes) {
  if (typeof classes === 'string') {
    element.classList.add(classes);
  } else if (Array.isArray(classes)) {
    element.classList.add(...classes);
  }
}

/**
 * Remove Class from Element
 * Purpose: Helper to remove single or multiple CSS classes
 * @param {HTMLElement} element - Target element
 * @param {string|array} classes - Class name(s) to remove
 */
function removeClass(element, classes) {
  if (typeof classes === 'string') {
    element.classList.remove(classes);
  } else if (Array.isArray(classes)) {
    element.classList.remove(...classes);
  }
}

/**
 * Toggle Class on Element
 * Purpose: Helper to toggle CSS class
 * @param {HTMLElement} element - Target element
 * @param {string} className - Class name to toggle
 */
function toggleClass(element, className) {
  element.classList.toggle(className);
}

/**
 * Get Element by ID
 * Purpose: Shortcut for getElementById with null safety
 * @param {string} id - Element ID
 * @returns {HTMLElement|null}
 */
function getById(id) {
  return document.getElementById(id);
}

/**
 * Query Select Shortcut
 * Purpose: Shortcut for querySelector
 * @param {string} selector - CSS selector
 * @returns {HTMLElement|null}
 */
function query(selector) {
  return document.querySelector(selector);
}

/**
 * Query Select All Shortcut
 * Purpose: Shortcut for querySelectorAll
 * @param {string} selector - CSS selector
 * @returns {NodeList}
 */
function queryAll(selector) {
  return document.querySelectorAll(selector);
}

/**
 * Show Element
 * Purpose: Remove display:none from element
 * @param {HTMLElement} element - Element to show
 */
function show(element) {
  element.style.display = '';
  element.classList.remove('hidden');
}

/**
 * Hide Element
 * Purpose: Hide element by adding display:none
 * @param {HTMLElement} element - Element to hide
 */
function hide(element) {
  element.style.display = 'none';
  element.classList.add('hidden');
}

/**
 * Check if Device is Mobile
 * Purpose: Detect if viewport is mobile size
 * @returns {boolean}
 */
function isMobile() {
  return window.innerWidth < 768;
}

/**
 * Debounce Function
 * Purpose: Limit function execution frequency (useful for scroll, resize events)
 * @param {Function} func - Function to debounce
 * @param {number} wait - Milliseconds to wait
 * @returns {Function} - Debounced function
 */
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

/**
 * Throttle Function
 * Purpose: Limit function execution rate (useful for scroll, resize events)
 * @param {Function} func - Function to throttle
 * @param {number} limit - Milliseconds between executions
 * @returns {Function} - Throttled function
 */
function throttle(func, limit) {
  let inThrottle;
  return function(...args) {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
}

/**
 * Store Data in LocalStorage
 * Purpose: Safely store data in browser's local storage
 * @param {string} key - Storage key
 * @param {any} value - Value to store (automatically JSON stringified)
 */
function storeData(key, value) {
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch (e) {
    console.warn('LocalStorage not available:', e);
  }
}

/**
 * Retrieve Data from LocalStorage
 * Purpose: Safely retrieve and parse data from browser's local storage
 * @param {string} key - Storage key
 * @returns {any|null}
 */
function getData(key) {
  try {
    const item = localStorage.getItem(key);
    return item ? JSON.parse(item) : null;
  } catch (e) {
    console.warn('Error reading from LocalStorage:', e);
    return null;
  }
}

/**
 * Remove Data from LocalStorage
 * Purpose: Remove specific item from local storage
 * @param {string} key - Storage key
 */
function removeData(key) {
  try {
    localStorage.removeItem(key);
  } catch (e) {
    console.warn('Error removing from LocalStorage:', e);
  }
}

/**
 * Copy Text to Clipboard
 * Purpose: Copy text to clipboard with fallback for older browsers
 * @param {string} text - Text to copy
 * @returns {Promise<boolean>}
 */
async function copyToClipboard(text) {
  try {
    if (navigator.clipboard) {
      await navigator.clipboard.writeText(text);
      return true;
    } else {
      // Fallback for older browsers
      const textarea = document.createElement('textarea');
      textarea.value = text;
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand('copy');
      document.body.removeChild(textarea);
      return true;
    }
  } catch (e) {
    console.warn('Failed to copy to clipboard:', e);
    return false;
  }
}

// Make utilities globally available
window.DOMUtils = {
  addClass, removeClass, toggleClass,
  getById, query, queryAll,
  show, hide, isMobile,
  debounce, throttle,
  storeData, getData, removeData,
  copyToClipboard
};
