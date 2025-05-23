// Main JavaScript file for EWE MLM Platform

// Global variables
let currentUser = null;
let notifications = [];
let websocketConnection = null;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    initializeComponents();
    setupEventListeners();
    loadUserData();
});

// Initialize main application features
function initializeApp() {
    console.log('EWE MLM Platform Initialized');
    
    // Setup CSRF token for AJAX requests
    setupCSRFToken();
    
    // Initialize tooltips
    initializeTooltips();
    
    // Setup auto-logout
    setupAutoLogout();
    
    // Load theme preference
    loadThemePreference();
}

// Setup CSRF token for AJAX requests
function setupCSRFToken() {
    const token = document.querySelector('[name=csrfmiddlewaretoken]');
    if (token) {
        window.csrfToken = token.value;
        
        // Set up AJAX defaults
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", window.csrfToken);
                }
            }
        });
    }
}

// Initialize all interactive components
function initializeComponents() {
    // Initialize dropdowns
    initializeDropdowns();
    
    // Initialize modals
    initializeModals();
    
    // Initialize charts
    initializeCharts();
    
    // Initialize form validations
    initializeFormValidations();
    
    // Initialize real-time updates
    initializeRealTimeUpdates();
}

// Setup event listeners
function setupEventListeners() {
    // Mobile menu toggle
    const mobileMenuButton = document.getElementById('mobile-menu-button');
    if (mobileMenuButton) {
        mobileMenuButton.addEventListener('click', toggleMobileMenu);
    }
    
    // Search functionality
    const searchInputs = document.querySelectorAll('[data-search]');
    searchInputs.forEach(input => {
        input.addEventListener('input', debounce(handleSearch, 300));
    });
    
    // Copy to clipboard functionality
    const copyButtons = document.querySelectorAll('[data-copy]');
    copyButtons.forEach(button => {
        button.addEventListener('click', copyToClipboard);
    });
    
    // Form auto-save
    const autoSaveForms = document.querySelectorAll('[data-autosave]');
    autoSaveForms.forEach(form => {
        form.addEventListener('input', debounce(autoSaveForm, 1000));
    });
    
    // Confirmation dialogs
    const confirmButtons = document.querySelectorAll('[data-confirm]');
    confirmButtons.forEach(button => {
        button.addEventListener('click', handleConfirmAction);
    });
}

// Dropdown functionality
function initializeDropdowns() {
    window.toggleDropdown = function() {
        const dropdown = document.getElementById('dropdown');
        if (dropdown) {
            dropdown.classList.toggle('hidden');
        }
    };
    
    // Close dropdown when clicking outside
    document.addEventListener('click', function(event) {
        const dropdown = document.getElementById('dropdown');
        const trigger = event.target.closest('[onclick*="toggleDropdown"]');
        
        if (dropdown && !trigger && !dropdown.contains(event.target)) {
            dropdown.classList.add('hidden');
        }
    });
}

// Modal functionality
function initializeModals() {
    // Generic modal functions
    window.openModal = function(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.remove('hidden');
            document.body.style.overflow = 'hidden';
            
            // Focus management
            const firstFocusable = modal.querySelector('input, button, select, textarea, [tabindex]:not([tabindex="-1"])');
            if (firstFocusable) {
                firstFocusable.focus();
            }
        }
    };
    
    window.closeModal = function(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add('hidden');
            document.body.style.overflow = '';
        }
    };
    
    // Close modal on ESC key
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            const openModals = document.querySelectorAll('.modal-overlay:not(.hidden)');
            openModals.forEach(modal => {
                modal.classList.add('hidden');
            });
            document.body.style.overflow = '';
        }
    });
}

// Chart initialization
function initializeCharts() {
    // Income chart
    const incomeChartCanvas = document.getElementById('incomeChart');
    if (incomeChartCanvas) {
        createIncomeChart(incomeChartCanvas);
    }
    
    // Team growth chart
    const teamChartCanvas = document.getElementById('teamChart');
    if (teamChartCanvas) {
        createTeamChart(teamChartCanvas);
    }
}

// Create income chart
function createIncomeChart(canvas) {
    const ctx = canvas.getContext('2d');
    
    // Sample data - would be replaced with real data
    const data = {
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        datasets: [{
            label: 'Total Income',
            data: [0, 0, 0, 0, 0, 0],
            borderColor: '#3B82F6',
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            tension: 0.4
        }]
    };
    
    const config = {
        type: 'line',
        data: data,
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '₹' + value.toLocaleString();
                        }
                    }
                }
            }
        }
    };
    
    new Chart(ctx, config);
}

// Create team growth chart
function createTeamChart(canvas) {
    const ctx = canvas.getContext('2d');
    
    const data = {
        labels: ['Left Team', 'Right Team'],
        datasets: [{
            data: [0, 0],
            backgroundColor: ['#10B981', '#8B5CF6'],
            borderWidth: 0
        }]
    };
    
    const config = {
        type: 'doughnut',
        data: data,
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    };
    
    new Chart(ctx, config);
}

// Form validation
function initializeFormValidations() {
    const forms = document.querySelectorAll('form[data-validate]');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!validateForm(form)) {
                event.preventDefault();
                return false;
            }
        });
        
        // Real-time validation
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                validateField(input);
            });
        });
    });
}

// Validate form
function validateForm(form) {
    let isValid = true;
    const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
    
    inputs.forEach(input => {
        if (!validateField(input)) {
            isValid = false;
        }
    });
    
    return isValid;
}

// Validate individual field
function validateField(field) {
    const value = field.value.trim();
    let isValid = true;
    let errorMessage = '';
    
    // Required validation
    if (field.hasAttribute('required') && !value) {
        isValid = false;
        errorMessage = 'This field is required';
    }
    
    // Email validation
    if (field.type === 'email' && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            isValid = false;
            errorMessage = 'Please enter a valid email address';
        }
    }
    
    // Phone validation
    if (field.name === 'mobile_no' && value) {
        const phoneRegex = /^[6-9]\d{9}$/;
        if (!phoneRegex.test(value)) {
            isValid = false;
            errorMessage = 'Please enter a valid 10-digit mobile number';
        }
    }
    
    // Password validation
    if (field.type === 'password' && value) {
        if (value.length < 8) {
            isValid = false;
            errorMessage = 'Password must be at least 8 characters long';
        }
    }
    
    // Update field appearance
    updateFieldValidation(field, isValid, errorMessage);
    
    return isValid;
}

// Update field validation appearance
function updateFieldValidation(field, isValid, errorMessage) {
    const fieldGroup = field.closest('.form-group') || field.parentElement;
    
    // Remove existing validation classes
    field.classList.remove('field-success', 'field-error');
    
    // Remove existing error message
    const existingError = fieldGroup.querySelector('.field-error-message');
    if (existingError) {
        existingError.remove();
    }
    
    if (!isValid) {
        field.classList.add('field-error');
        
        // Add error message
        const errorElement = document.createElement('div');
        errorElement.className = 'field-error-message text-red-600 text-sm mt-1';
        errorElement.textContent = errorMessage;
        fieldGroup.appendChild(errorElement);
    } else if (field.value.trim()) {
        field.classList.add('field-success');
    }
}

// Real-time updates
function initializeRealTimeUpdates() {
    // Update balances every 30 seconds
    if (document.querySelector('[data-balance]')) {
        setInterval(updateBalances, 30000);
    }
    
    // Update notifications every 60 seconds
    setInterval(updateNotifications, 60000);
}

// Update user balances
function updateBalances() {
    fetch('/api/balance-update/')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateBalanceElements(data.balances);
            }
        })
        .catch(error => {
            console.error('Error updating balances:', error);
        });
}

// Update balance elements in DOM
function updateBalanceElements(balances) {
    Object.keys(balances).forEach(key => {
        const elements = document.querySelectorAll(`[data-balance="${key}"]`);
        elements.forEach(element => {
            element.textContent = '₹' + parseFloat(balances[key]).toFixed(2);
        });
    });
}

// Update notifications
function updateNotifications() {
    fetch('/api/notifications/')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayNotifications(data.notifications);
            }
        })
        .catch(error => {
            console.error('Error updating notifications:', error);
        });
}

// Display notifications
function displayNotifications(notifications) {
    const container = document.getElementById('notifications-container');
    if (!container) return;
    
    notifications.forEach(notification => {
        showNotification(notification.message, notification.type);
    });
}

// Show notification
function showNotification(message, type = 'info', duration = 5000) {
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 max-w-sm w-full bg-white shadow-lg rounded-lg pointer-events-auto ring-1 ring-black ring-opacity-5 z-50 transform transition-all duration-300 translate-x-full`;
    
    const bgColor = {
        'success': 'bg-green-50 border-green-400 text-green-800',
        'error': 'bg-red-50 border-red-400 text-red-800',
        'warning': 'bg-yellow-50 border-yellow-400 text-yellow-800',
        'info': 'bg-blue-50 border-blue-400 text-blue-800'
    }[type] || 'bg-blue-50 border-blue-400 text-blue-800';
    
    notification.innerHTML = `
        <div class="p-4 ${bgColor} border-l-4 rounded">
            <div class="flex items-center">
                <div class="flex-1">
                    <p class="text-sm font-medium">${message}</p>
                </div>
                <button onclick="this.parentElement.parentElement.parentElement.remove()" class="ml-4 text-gray-400 hover:text-gray-600">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.classList.remove('translate-x-full');
    }, 100);
    
    // Auto remove
    if (duration > 0) {
        setTimeout(() => {
            notification.classList.add('translate-x-full');
            setTimeout(() => {
                if (notification.parentElement) {
                    notification.remove();
                }
            }, 300);
        }, duration);
    }
}

// Mobile menu toggle
function toggleMobileMenu() {
    const mobileMenu = document.getElementById('mobile-menu');
    if (mobileMenu) {
        mobileMenu.classList.toggle('hidden');
    }
}

// Search functionality
function handleSearch(event) {
    const query = event.target.value.toLowerCase();
    const searchType = event.target.dataset.search;
    
    if (searchType === 'members') {
        searchMembers(query);
    } else if (searchType === 'transactions') {
        searchTransactions(query);
    }
}

// Search members
function searchMembers(query) {
    const memberRows = document.querySelectorAll('[data-member-row]');
    
    memberRows.forEach(row => {
        const memberData = row.textContent.toLowerCase();
        if (memberData.includes(query)) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

// Search transactions
function searchTransactions(query) {
    const transactionRows = document.querySelectorAll('[data-transaction-row]');
    
    transactionRows.forEach(row => {
        const transactionData = row.textContent.toLowerCase();
        if (transactionData.includes(query)) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

// Copy to clipboard
function copyToClipboard(event) {
    const target = event.target.closest('[data-copy]');
    const text = target.dataset.copy || target.textContent;
    
    navigator.clipboard.writeText(text).then(() => {
        showNotification('Copied to clipboard!', 'success', 2000);
    }).catch(() => {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        showNotification('Copied to clipboard!', 'success', 2000);
    });
}

// Auto-save form
function autoSaveForm(event) {
    const form = event.target.closest('form');
    if (!form) return;
    
    const formData = new FormData(form);
    const data = Object.fromEntries(formData);
    
    // Save to localStorage
    const formId = form.id || 'auto-save-form';
    localStorage.setItem(`autosave_${formId}`, JSON.stringify(data));
    
    // Show save indicator
    showSaveIndicator(form);
}

// Show save indicator
function showSaveIndicator(form) {
    let indicator = form.querySelector('.save-indicator');
    if (!indicator) {
        indicator = document.createElement('div');
        indicator.className = 'save-indicator fixed bottom-4 right-4 bg-green-500 text-white px-3 py-1 rounded text-sm';
        indicator.textContent = 'Auto-saved';
        form.appendChild(indicator);
    }
    
    indicator.style.display = 'block';
    setTimeout(() => {
        indicator.style.display = 'none';
    }, 2000);
}

// Handle confirmation actions
function handleConfirmAction(event) {
    const target = event.target.closest('[data-confirm]');
    const message = target.dataset.confirm || 'Are you sure?';
    
    if (!confirm(message)) {
        event.preventDefault();
        return false;
    }
}

// Load user data
function loadUserData() {
    const userDataElement = document.getElementById('user-data');
    if (userDataElement) {
        try {
            currentUser = JSON.parse(userDataElement.textContent);
        } catch (error) {
            console.error('Error parsing user data:', error);
        }
    }
}

// Initialize tooltips
function initializeTooltips() {
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    
    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', showTooltip);
        element.addEventListener('mouseleave', hideTooltip);
    });
}

// Show tooltip
function showTooltip(event) {
    const element = event.target;
    const text = element.dataset.tooltip;
    
    const tooltip = document.createElement('div');
    tooltip.className = 'absolute bg-gray-800 text-white px-2 py-1 rounded text-xs z-50 tooltip';
    tooltip.textContent = text;
    
    document.body.appendChild(tooltip);
    
    const rect = element.getBoundingClientRect();
    tooltip.style.left = `${rect.left + rect.width / 2 - tooltip.offsetWidth / 2}px`;
    tooltip.style.top = `${rect.top - tooltip.offsetHeight - 5}px`;
}

// Hide tooltip
function hideTooltip() {
    const tooltips = document.querySelectorAll('.tooltip');
    tooltips.forEach(tooltip => tooltip.remove());
}

// Setup auto-logout
function setupAutoLogout() {
    let logoutTimer;
    const timeout = 30 * 60 * 1000; // 30 minutes
    
    function resetTimer() {
        clearTimeout(logoutTimer);
        logoutTimer = setTimeout(() => {
            if (confirm('Your session is about to expire. Do you want to stay logged in?')) {
                resetTimer();
            } else {
                window.location.href = '/auth/logout/';
            }
        }, timeout);
    }
    
    // Reset timer on user activity
    document.addEventListener('mousedown', resetTimer);
    document.addEventListener('mousemove', resetTimer);
    document.addEventListener('keypress', resetTimer);
    document.addEventListener('scroll', resetTimer);
    document.addEventListener('touchstart', resetTimer);
    
    resetTimer();
}

// Theme management
function loadThemePreference() {
    const theme = localStorage.getItem('theme') || 'light';
    applyTheme(theme);
}

function applyTheme(theme) {
    if (theme === 'dark') {
        document.documentElement.classList.add('dark');
    } else {
        document.documentElement.classList.remove('dark');
    }
    localStorage.setItem('theme', theme);
}

function toggleTheme() {
    const isDark = document.documentElement.classList.contains('dark');
    applyTheme(isDark ? 'light' : 'dark');
}

// Utility functions
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

function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR'
    }).format(amount);
}

function formatDate(date) {
    return new Intl.DateTimeFormat('en-IN', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    }).format(new Date(date));
}

// Export functions for global use
window.EWE = {
    showNotification,
    openModal,
    closeModal,
    toggleTheme,
    formatCurrency,
    formatDate,
    copyToClipboard: (text) => {
        navigator.clipboard.writeText(text).then(() => {
            showNotification('Copied to clipboard!', 'success', 2000);
        });
    }
};

// Service Worker registration for PWA capabilities
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/static/js/sw.js')
            .then(registration => {
                console.log('SW registered: ', registration);
            })
            .catch(registrationError => {
                console.log('SW registration failed: ', registrationError);
            });
    });
}

console.log('EWE MLM Platform JavaScript loaded successfully');
