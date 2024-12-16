document.addEventListener("DOMContentLoaded", function () {
    const graphContainer = document.querySelector('.graphContainer');

    // Show a placeholder message initially
    graphContainer.innerHTML = "<p>Select a stock to view its graph.</p>";

    const stockItems = document.querySelectorAll('.stock-item');
    stockItems.forEach(item => {
        item.addEventListener('click', function () {
            const stockName = this.querySelector('.stock-name').textContent.trim();

            // Show a loading message while fetching the graph
            graphContainer.innerHTML = "<p>Loading graph...</p>";

            fetch(`/get-stock-graph/?stock_name=${encodeURIComponent(stockName)}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.data && data.layout) {
                        graphContainer.innerHTML = ""
                        // Render the fetched graph
                        Plotly.newPlot(graphContainer, data.data, data.layout);
                    } else if (data.error) {
                        // Handle backend errors
                        graphContainer.innerHTML = `<p>Error: ${data.error}</p>`;
                    }
                })
                .catch(error => {
                    // Handle network or unexpected errors
                    console.error('Error fetching stock graph:', error);
                    graphContainer.innerHTML = `<p>Could not load graph. Please try again later.</p>`;
                });
        });
    });
});
