/**
 * Navigation & UI Utilities
 * Purpose: Core functionality for navigation, navigation menu interactions, and general UI utilities
 * Used in: base.html template and all pages
 */

/**
 * Initialize Navigation Menu
 * Purpose: Set up click handlers for mobile menu toggle and smooth scrolling
 */
function initializeNavigation() {
  // Handle mobile menu interactions
  const mobileMenuBtn = document.querySelector('[data-mobile-menu-btn]');
  const mobileMenu = document.querySelector('[data-mobile-menu]');

  if (mobileMenuBtn && mobileMenu) {
    mobileMenuBtn.addEventListener('click', () => {
      mobileMenu.classList.toggle('hidden');
    });
  }

  // Close mobile menu when link is clicked
  const mobileMenuLinks = document.querySelectorAll('[data-mobile-menu] a');
  mobileMenuLinks.forEach(link => {
    link.addEventListener('click', () => {
      if (mobileMenu) {
        mobileMenu.classList.add('hidden');
      }
    });
  });
}

/**
 * Smooth Scroll to Element
 * Purpose: Enable smooth scrolling to anchors for better UX
 * @param {string} selector - CSS selector of target element
 */
function smoothScrollToElement(selector) {
  const element = document.querySelector(selector);
  if (element) {
    element.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
}

/**
 * Add Active Class to Current Navigation Link
 * Purpose: Highlight the current page in navigation
 */
function highlightCurrentPage() {
  const currentPath = window.location.pathname;
  const navLinks = document.querySelectorAll('nav a[href]');

  navLinks.forEach(link => {
    if (link.getAttribute('href') === currentPath) {
      link.classList.add('text-primary', 'font-bold');
      link.classList.remove('text-muted-foreground');
    }
  });
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  initializeNavigation();
  highlightCurrentPage();
});
