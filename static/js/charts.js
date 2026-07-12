document.addEventListener("DOMContentLoaded", function() {
    const ctx = document.getElementById('roiChart').getContext('2d');
    
    // Hardcoded data for hackathon UI purposes
    const roiChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Van-01', 'Van-02', 'Truck-01', 'Truck-02', 'Van-05'],
            datasets: [{
                label: 'Vehicle ROI (%)',
                data: [12, 19, 8, 15, 22],
                backgroundColor: 'rgba(0, 123, 255, 0.6)',
                borderColor: 'rgba(0, 123, 255, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
});