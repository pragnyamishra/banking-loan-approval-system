// Main JavaScript for Loan Approval System

$(document).ready(function() {
    // Initialize all tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize all DataTables with default settings
    $('.data-table').DataTable({
        pageLength: 20,
        order: [[0, 'desc']],
        responsive: true
    });
    
    // Format currency
    $('.currency').each(function() {
        var value = parseFloat($(this).text());
        $(this).text('$' + value.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2}));
    });
    
    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        $('.alert').fadeOut('slow');
    }, 5000);
});

// Utility function to format numbers
function formatNumber(num, decimals = 0) {
    return num.toLocaleString('en-US', {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
    });
}

// Utility function to format currency
function formatCurrency(num) {
    return '$' + formatNumber(num, 2);
}

// Utility function to format percentage
function formatPercent(num, decimals = 2) {
    return num.toFixed(decimals) + '%';
}
