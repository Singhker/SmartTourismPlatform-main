/**
 * ==========================================
 * SMART TOURISM PLATFORM - COMPLETE JS
 * Interactive Features & Animations
 * ==========================================
 */

// ==========================================
// 1. DOM READY - INITIALIZE EVERYTHING
// ==========================================

document.addEventListener('DOMContentLoaded', function() {
    
    // Initialize all features
    initTooltips();
    initAutoDismissAlerts();
    initSearchAutoSubmit();
    initFilterAutoSubmit();
    initDeleteConfirmations();
    initScrollAnimations();
    initCounterAnimation();
    initSmoothScroll();
    initBackToTop();
    initNavbarScrollEffect();
    initMobileMenuClose();
    initDarkModeToggle();
    initChartResize();
    
    console.log('🚀 Smart Tourism Platform initialized!');
});


// ==========================================
// 2. BOOTSTRAP TOOLTIPS
// ==========================================

function initTooltips() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}


// ==========================================
// 3. AUTO-DISMISS ALERTS (5 seconds)
// ==========================================

function initAutoDismissAlerts() {
    var alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
}


// ==========================================
// 4. SEARCH AUTO-SUBMIT (with debounce)
// ==========================================

function initSearchAutoSubmit() {
    var searchInput = document.querySelector('input[name="search"]');
    if (searchInput) {
        var timeoutId;
        searchInput.addEventListener('input', function() {
            clearTimeout(timeoutId);
            timeoutId = setTimeout(function() {
                var form = searchInput.closest('form');
                if (form) form.submit();
            }, 300);
        });
    }
}


// ==========================================
// 5. FILTER AUTO-SUBMIT (dropdown change)
// ==========================================

function initFilterAutoSubmit() {
    var filterSelects = document.querySelectorAll('select[data-auto-submit="true"], select[onchange*="submit"]');
    filterSelects.forEach(function(select) {
        select.addEventListener('change', function() {
            var form = select.closest('form');
            if (form) form.submit();
        });
    });
}


// ==========================================
// 6. DELETE CONFIRMATION
// ==========================================

function initDeleteConfirmations() {
    var deleteButtons = document.querySelectorAll('.btn-delete, .delete-confirm');
    deleteButtons.forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            if (!confirm('⚠️ Are you sure you want to delete this item? This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    });
}


// ==========================================
// 7. SCROLL ANIMATIONS (fade-in on scroll)
// ==========================================

function initScrollAnimations() {
    var animatedElements = document.querySelectorAll('.animate-on-scroll, .feature-card, .place-card, .stat-item');
    
    if (animatedElements.length === 0) return;
    
    var observer = new IntersectionObserver(function(entries) {
        entries.forEach(function(entry) {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-fade-in-up');
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });
    
    animatedElements.forEach(function(el) {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });
}


// ==========================================
// 8. COUNTER ANIMATION (for stats)
// ==========================================

function initCounterAnimation() {
    var counters = document.querySelectorAll('.stat-number');
    
    counters.forEach(function(counter) {
        var target = parseInt(counter.textContent.replace(/[^0-9]/g, ''));
        if (isNaN(target) || target === 0) return;
        
        var isVisible = false;
        var observer = new IntersectionObserver(function(entries) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting && !isVisible) {
                    isVisible = true;
                    animateCounter(counter, target);
                }
            });
        });
        observer.observe(counter);
    });
}

function animateCounter(element, target) {
    var current = 0;
    var increment = Math.ceil(target / 60);
    var duration = 2000; // 2 seconds
    var stepTime = Math.floor(duration / 60);
    
    var timer = setInterval(function() {
        current += increment;
        if (current >= target) {
            current = target;
            clearInterval(timer);
        }
        element.textContent = current + (element.textContent.includes('+') ? '+' : '');
    }, stepTime);
}


// ==========================================
// 9. SMOOTH SCROLL (for anchor links)
// ==========================================

function initSmoothScroll() {
    var links = document.querySelectorAll('a[href^="#"]:not([href="#"])');
    links.forEach(function(link) {
        link.addEventListener('click', function(e) {
            var targetId = this.getAttribute('href');
            var targetElement = document.querySelector(targetId);
            if (targetElement) {
                e.preventDefault();
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}


// ==========================================
// 10. BACK TO TOP BUTTON
// ==========================================

function initBackToTop() {
    // Create button if it doesn't exist
    var btn = document.getElementById('backToTop');
    if (!btn) {
        btn = document.createElement('button');
        btn.id = 'backToTop';
        btn.innerHTML = '<i class="bi bi-arrow-up"></i>';
        btn.style.cssText = `
            position: fixed;
            bottom: 30px;
            right: 30px;
            width: 50px;
            height: 50px;
            border-radius: 50%;
            background: linear-gradient(135deg, #0d6efd, #0a58ca);
            color: white;
            border: none;
            font-size: 1.5rem;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(13, 110, 253, 0.3);
            opacity: 0;
            visibility: hidden;
            transition: all 0.3s ease;
            z-index: 1000;
            display: flex;
            align-items: center;
            justify-content: center;
        `;
        document.body.appendChild(btn);
        
        btn.addEventListener('click', function() {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }
    
    // Show/hide on scroll
    window.addEventListener('scroll', function() {
        if (window.scrollY > 300) {
            btn.style.opacity = '1';
            btn.style.visibility = 'visible';
            btn.style.transform = 'translateY(0)';
        } else {
            btn.style.opacity = '0';
            btn.style.visibility = 'hidden';
            btn.style.transform = 'translateY(20px)';
        }
    });
}


// ==========================================
// 11. NAVBAR SCROLL EFFECT
// ==========================================

function initNavbarScrollEffect() {
    var navbar = document.querySelector('.navbar');
    if (!navbar) return;
    
    window.addEventListener('scroll', function() {
        if (window.scrollY > 50) {
            navbar.style.boxShadow = '0 4px 30px rgba(0,0,0,0.2)';
            navbar.style.padding = '10px 0';
        } else {
            navbar.style.boxShadow = '0 4px 20px rgba(13, 110, 253, 0.3)';
            navbar.style.padding = '15px 0';
        }
    });
}


// ==========================================
// 12. MOBILE MENU - CLOSE ON LINK CLICK
// ==========================================

function initMobileMenuClose() {
    var navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    var navbarCollapse = document.querySelector('.navbar-collapse');
    
    if (!navbarCollapse) return;
    
    navLinks.forEach(function(link) {
        link.addEventListener('click', function() {
            var bsCollapse = bootstrap.Collapse.getInstance(navbarCollapse);
            if (bsCollapse) {
                bsCollapse.hide();
            }
        });
    });
}


// ==========================================
// 13. DARK MODE TOGGLE (optional)
// ==========================================

function initDarkModeToggle() {
    var toggleBtn = document.getElementById('darkModeToggle');
    if (!toggleBtn) return;
    
    // Check saved preference
    var darkMode = localStorage.getItem('darkMode');
    if (darkMode === 'enabled') {
        document.body.classList.add('dark-mode');
        toggleBtn.innerHTML = '<i class="bi bi-sun"></i>';
    }
    
    toggleBtn.addEventListener('click', function() {
        document.body.classList.toggle('dark-mode');
        if (document.body.classList.contains('dark-mode')) {
            localStorage.setItem('darkMode', 'enabled');
            toggleBtn.innerHTML = '<i class="bi bi-sun"></i>';
        } else {
            localStorage.setItem('darkMode', 'disabled');
            toggleBtn.innerHTML = '<i class="bi bi-moon"></i>';
        }
    });
}


// ==========================================
// 14. CHART RESIZE (for Plotly)
// ==========================================

function initChartResize() {
    var charts = document.querySelectorAll('.plotly-chart');
    if (charts.length === 0) return;
    
    var resizeTimeout;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(function() {
            charts.forEach(function(chart) {
                if (chart._fullLayout) {
                    Plotly.Plots.resize(chart);
                }
            });
        }, 200);
    });
}


// ==========================================
// 15. UTILITY FUNCTIONS (global helpers)
// ==========================================

// Format number with commas
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

// Truncate text with ellipsis
function truncateText(text, maxLength) {
    if (!text) return '';
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

// Export to CSV
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

// Toast notification
function showToast(message, type) {
    var types = {
        success: 'bg-success text-white',
        error: 'bg-danger text-white',
        warning: 'bg-warning text-dark',
        info: 'bg-info text-dark'
    };
    
    var toast = document.createElement('div');
    toast.className = 'toast align-items-center border-0 position-fixed bottom-0 end-0 m-3';
    toast.role = 'alert';
    toast.innerHTML = `
        <div class="d-flex ${types[type] || 'bg-primary text-white'}">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    document.body.appendChild(toast);
    
    var bsToast = new bootstrap.Toast(toast, { delay: 4000 });
    bsToast.show();
    
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}

// Make utilities globally available
window.formatNumber = formatNumber;
window.truncateText = truncateText;
window.getUrlParams = getUrlParams;
window.exportToCSV = exportToCSV;
window.showToast = showToast;


// ==========================================
// 16. RESPONSIVE TABLE WRAPPER
// ==========================================

document.addEventListener('DOMContentLoaded', function() {
    var tables = document.querySelectorAll('.table-responsive');
    tables.forEach(function(table) {
        if (!table.closest('.table-responsive')) {
            var wrapper = document.createElement('div');
            wrapper.className = 'table-responsive';
            table.parentNode.insertBefore(wrapper, table);
            wrapper.appendChild(table);
        }
    });
});


// ==========================================
// 17. KEYBOARD SHORTCUTS
// ==========================================

document.addEventListener('keydown', function(e) {
    // Ctrl + / to toggle dark mode
    if (e.ctrlKey && e.key === '/') {
        e.preventDefault();
        var toggleBtn = document.getElementById('darkModeToggle');
        if (toggleBtn) toggleBtn.click();
    }
    
    // Escape to close modals
    if (e.key === 'Escape') {
        var openModals = document.querySelectorAll('.modal.show');
        openModals.forEach(function(modal) {
            var bsModal = bootstrap.Modal.getInstance(modal);
            if (bsModal) bsModal.hide();
        });
    }
});


// ==========================================
// 18. LAZY LOAD IMAGES
// ==========================================

document.addEventListener('DOMContentLoaded', function() {
    var images = document.querySelectorAll('img[data-src]');
    if (images.length === 0) return;
    
    var imageObserver = new IntersectionObserver(function(entries) {
        entries.forEach(function(entry) {
            if (entry.isIntersecting) {
                var img = entry.target;
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
                imageObserver.unobserve(img);
            }
        });
    });
    
    images.forEach(function(img) {
        imageObserver.observe(img);
    });
});


// ==========================================
// 19. PRINT QUALITY REPORT
// ==========================================

function printReport() {
    window.print();
}

// Make print function global
window.printReport = printReport;


// ==========================================
// 20. LOADING SPINNER
// ==========================================

function showLoading(show) {
    var spinner = document.getElementById('loadingSpinner');
    if (!spinner) {
        spinner = document.createElement('div');
        spinner.id = 'loadingSpinner';
        spinner.className = 'position-fixed top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center';
        spinner.style.cssText = `
            background: rgba(255,255,255,0.8);
            z-index: 9999;
            display: none;
        `;
        spinner.innerHTML = `
            <div class="spinner-border text-primary" style="width: 4rem; height: 4rem;" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
        `;
        document.body.appendChild(spinner);
    }
    
    spinner.style.display = show ? 'flex' : 'none';
}

// Make loading function global
window.showLoading = showLoading;


// ==========================================
// 21. AUTO-REFRESH DATA (for dashboards)
// ==========================================

function autoRefresh(interval, callback) {
    if (!interval || interval < 1000) interval = 30000; // Default 30 seconds
    
    setInterval(function() {
        if (typeof callback === 'function') {
            callback();
        }
    }, interval);
}

// Make autoRefresh global
window.autoRefresh = autoRefresh;


// ==========================================
// 22. CHART.JS HELPER (if using Chart.js)
// ==========================================

function createChart(canvasId, config) {
    var ctx = document.getElementById(canvasId);
    if (ctx && typeof Chart !== 'undefined') {
        return new Chart(ctx.getContext('2d'), config);
    }
    return null;
}

// Make chart helper global
window.createChart = createChart;

console.log('✅ JavaScript loaded successfully!');