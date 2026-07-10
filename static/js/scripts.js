// Smart Tourism Platform - Custom JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    var alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Search form auto-submit
    var searchInput = document.querySelector('input[name="search"]');
    if (searchInput) {
        var timeoutId;
        searchInput.addEventListener('input', function() {
            clearTimeout(timeoutId);
            timeoutId = setTimeout(function() {
                searchInput.closest('form').submit();
            }, 300);
        });
    }

    // Filter form auto-submit
    var filterSelects = document.querySelectorAll('select[onchange]');
    filterSelects.forEach(function(select) {
        select.addEventListener('change', function() {
            this.closest('form').submit();
        });
    });

    // Confirm delete actions
    var deleteButtons = document.querySelectorAll('.btn-delete');
    deleteButtons.forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this item?')) {
                e.preventDefault();
            }
        });
    });

    // Enable dark mode toggle (optional)
    var darkModeToggle = document.querySelector('#darkModeToggle');
    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', function() {
            document.body.classList.toggle('dark-mode');
        });
    }
});

// Chart.js helper for creating charts
function createChart(canvasId, config) {
    var ctx = document.getElementById(canvasId);
    if (ctx) {
        return new Chart(ctx.getContext('2d'), config);
    }
    return null;
}

// Format numbers with commas
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

// Truncate text with ellipsis
function truncateText(text, maxLength) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

// Get URL parameters
function getUrlParams() {
    var params = {};
    window.location.search.replace(/[?&]+([^=&]+)=([^&]*)/gi, function(str, key, value) {
        params[key] = value;
    });
    return params;
}

// Scroll to top
function scrollToTop() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Export to CSV (client-side)
function exportToCSV(data, filename) {
    if (!data || data.length === 0) {
        alert('No data to export');
        return;
    }
    
    var headers = Object.keys(data[0]);
    var csvContent = headers.join(',') + '\n';
    
    data.forEach(function(row) {
        var values = headers.map(function(header) {
            var val = row[header] || '';
            // Escape commas and quotes
            if (typeof val === 'string' && (val.includes(',') || val.includes('"'))) {
                val = '"' + val.replace(/"/g, '""') + '"';
            }
            return val;
        });
        csvContent += values.join(',') + '\n';
    });
    
    var blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    var link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = filename || 'export.csv';
    link.click();
    URL.revokeObjectURL(link.href);
}