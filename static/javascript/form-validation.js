/**
 * Form Validation & Interaction
 * Purpose: Client-side form validation and interactive form helpers
 * Used in: Login, Register, and other form pages
 */

/**
 * Validate Email Format
 * Purpose: Checks if email follows valid format
 * @param {string} email - Email address to validate
 * @returns {boolean} - True if valid email format
 */
function isValidEmail(email) {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

/**
 * Validate Password Strength
 * Purpose: Checks password meets minimum security requirements
 * @param {string} password - Password to validate
 * @returns {object} - {isValid: boolean, score: number (0-3), feedback: string}
 */
function validatePasswordStrength(password) {
  let score = 0;
  let feedback = [];

  if (password.length >= 8) score++;
  else feedback.push('Password should be at least 8 characters');

  if (/[A-Z]/.test(password)) score++;
  else feedback.push('Add uppercase letters');

  if (/[0-9]/.test(password)) score++;
  else feedback.push('Add numbers');

  if (/[!@#$%^&*]/.test(password)) score++;
  else feedback.push('Add special characters (!@#$%^&*)');

  return {
    isValid: score >= 2,
    score: score,
    feedback: feedback.join(', ')
  };
}

/**
 * Real-time Form Field Validation
 * Purpose: Validates form fields as user types
 * @param {HTMLInputElement} field - Input field element
 * @param {string} type - Type of validation ('email', 'password', 'text', 'required')
 */
function validateFieldRealtime(field, type) {
  let isValid = false;

  switch(type) {
    case 'email':
      isValid = isValidEmail(field.value);
      break;
    case 'password':
      isValid = validatePasswordStrength(field.value).isValid;
      break;
    case 'required':
      isValid = field.value.trim().length > 0;
      break;
    default:
      isValid = field.value.trim().length > 0;
  }

  if (isValid) {
    field.classList.remove('border-destructive', 'bg-destructive/5');
    field.classList.add('border-primary/30');
  } else {
    field.classList.remove('border-primary/30');
    field.classList.add('border-destructive', 'bg-destructive/5');
  }

  return isValid;
}

/**
 * Setup Form Field Validators
 * Purpose: Attach real-time validation to all form fields with data-validate attribute
 */
function setupFormValidators() {
  const fields = document.querySelectorAll('[data-validate]');

  fields.forEach(field => {
    const validationType = field.getAttribute('data-validate');
    
    field.addEventListener('blur', () => {
      validateFieldRealtime(field, validationType);
    });

    field.addEventListener('input', () => {
      if (field.classList.contains('border-destructive')) {
        validateFieldRealtime(field, validationType);
      }
    });
  });
}

/**
 * Prevent Form Multiple Submissions
 * Purpose: Disable form submit button after first submission to prevent duplicates
 * @param {HTMLFormElement} form - Form element
 */
function preventFormDuplicateSubmits(form) {
  form.addEventListener('submit', () => {
    const submitBtn = form.querySelector('button[type="submit"]');
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.setAttribute('data-loading', 'true');
      submitBtn.textContent = 'Please wait...';
    }
  });
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  setupFormValidators();

  // Apply duplicate submit prevention to all forms
  const forms = document.querySelectorAll('form');
  forms.forEach(form => {
    preventFormDuplicateSubmits(form);
  });
});
