document.addEventListener("DOMContentLoaded", function () {
    const stockItems = document.querySelectorAll('.stock-item');
    stockItems.forEach(item => {
        item.addEventListener('click', function () {
            const stockName = this.querySelector('.stock-name').textContent.trim();

            console.log("Fetching graph for stock:", stockName); // Debugging log

            fetch(`/get-stock-graph/?stock_name=${encodeURIComponent(stockName)}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.data && data.layout) {
                        const graphContainer = document.querySelector('.graphContainer');

                        // Clear existing graph and render the new one
                        Plotly.newPlot(graphContainer, data.data, data.layout);
                    } else if (data.error) {
                        console.error(`Error: ${data.error}`);
                    }
                })
                .catch(error => {
                    console.error('Error fetching stock graph:', error);
                });
        });
    });
});
