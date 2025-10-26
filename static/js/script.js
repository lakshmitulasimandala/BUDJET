document.addEventListener("DOMContentLoaded", () => {
    const canvas = document.getElementById('expenseChart');
    if (!canvas) return;

    const labels = JSON.parse(canvas.dataset.labels);
    const values = JSON.parse(canvas.dataset.values);

    // Get current category filter (from URL)
    const urlParams = new URLSearchParams(window.location.search);
    const selectedCategory = urlParams.get('main_category');

    // Prepare data points with offsets
    const dataPoints = labels.map((label, index) => ({
        value: values[index],
        label: label,
        offset: (selectedCategory && label === selectedCategory) ? 25 : 0 // "explode" this slice
    }));

    new Chart(canvas, {
        type: 'pie',
        data: {
            labels: dataPoints.map(p => p.label),
            datasets: [{
                data: dataPoints.map(p => p.value),
                backgroundColor: [
                    '#ff6384','#36a2eb','#ffcd56',
                    '#4bc0c0','#9966ff','#ff9f40'
                ],
                // apply per-slice offset
                offset: dataPoints.map(p => p.offset)
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'bottom' },
                title: {
                    display: true,
                    text: selectedCategory
                        ? `Highlighted Category: ${selectedCategory}`
                        : 'Expense Summary by Category'
                }
            },
            animation: {
                animateRotate: true,
                duration: 1000
            }
        }
    });
});



// Modal logic
document.addEventListener("DOMContentLoaded", () => {
    const modal = document.getElementById('deleteModal');
    const closeModal = document.getElementById('closeModal');
    const cancelDelete = document.getElementById('cancelDelete');
    const confirmDelete = document.getElementById('confirmDelete');
    let formToSubmit = null;

    // attach click event to all delete buttons
    document.querySelectorAll('form[action^="/delete_transaction"]').forEach(form => {
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            formToSubmit = form;
            modal.style.display = 'flex';
        });
    });

    closeModal.onclick = () => modal.style.display = 'none';
    cancelDelete.onclick = () => modal.style.display = 'none';

    confirmDelete.onclick = () => {
        if (formToSubmit) formToSubmit.submit();
    };

    // click outside modal closes it
    window.onclick = function(event) {
        if (event.target === modal) {
            modal.style.display = "none";
        }
    };
});
