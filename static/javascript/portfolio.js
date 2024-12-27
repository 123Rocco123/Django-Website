document.addEventListener("DOMContentLoaded", function () {
    const graphContainer = document.querySelector('.graphContainer');
    const newsContainer = document.querySelector('.news');
    const predictionContainer = document.querySelector('.predictionList');

    // Store the currently displayed prediction trace
    let currentPredictionTrace = null;

    // Show placeholder messages initially
    graphContainer.innerHTML = "<p>Select a stock to view its graph.</p>";
    newsContainer.innerHTML = "<p>Select a stock to view its related news.</p>";
    predictionContainer.innerHTML = "<p>Select a stock to view prediction models.</p>";

    const stockItems = document.querySelectorAll('.stock-item');
    stockItems.forEach(item => {
        item.addEventListener('click', function () {
            const stockName = this.querySelector('.stock-name').textContent.trim();

            // Show loading messages while fetching data
            graphContainer.innerHTML = "<p>Loading graph...</p>";
            newsContainer.innerHTML = "<p>Loading news...</p>";
            predictionContainer.innerHTML = "<p>Loading prediction models...</p>";

            // Fetch and render the stock graph
            fetch(`/get-stock-graph/?stock_name=${encodeURIComponent(stockName)}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.data && data.layout) {
                        graphContainer.innerHTML = "";
                        Plotly.newPlot(graphContainer, data.data, data.layout);
                        currentPredictionTrace = null; // Reset prediction trace when new stock is selected
                    } else if (data.error) {
                        graphContainer.innerHTML = `<p>Error: ${data.error}</p>`;
                    }
                })
                .catch(error => {
                    console.error('Error fetching stock graph:', error);
                    graphContainer.innerHTML = `<p>Could not load graph. Please try again later.</p>`;
                });

            // Fetch and render the stock-related news
            fetch(`/get-stock-articles/?stock_name=${encodeURIComponent(stockName)}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.articles && data.articles.length > 0) {
                        newsContainer.innerHTML = data.articles
                            .map(article => `
                                <div class="news-article">
                                    <p class='dateOfArticle'>${article["Date Posted"]}</p>
                                    <h5>${article.Headline}</h5>
                                    <p>${article.Preview}</p>
                                    <a href="${article.Link}" target="_blank">Read more</a>
                                </div>
                            `)
                            .join('');
                    } else if (data.error) {
                        newsContainer.innerHTML = `<p>Error: ${data.error}</p>`;
                    } else {
                        newsContainer.innerHTML = "<p>No news articles available for this stock.</p>";
                    }
                })
                .catch(error => {
                    console.error('Error fetching stock news:', error);
                    newsContainer.innerHTML = `<p>Could not load news. Please try again later.</p>`;
                });

            // Fetch and render the prediction models
            fetch(`/get-stock-predictions/?stock_name=${encodeURIComponent(stockName)}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.predictions && data.predictions.length > 0) {
                        predictionContainer.innerHTML = `
                            <h4>Prediction Models</h4>
                            <div class="button-list">
                                ${data.predictions
                                    .map(prediction => `
                                        <button class="prediction-button" data-stock-name="${stockName}" data-model-name="${prediction}">
                                            ${prediction}
                                        </button>
                                    `)
                                    .join('')}
                            </div>
                        `;

                        // Add event listeners to prediction buttons
                        const predictionButtons = predictionContainer.querySelectorAll('.prediction-button');
                        predictionButtons.forEach(button => {
                            button.addEventListener('click', function () {
                                const modelName = this.getAttribute('data-model-name');
                                const stockName = this.getAttribute('data-stock-name');

                                // Check if this prediction trace is already added
                                if (currentPredictionTrace && currentPredictionTrace.name === modelName) {
                                    // Remove the current prediction trace
                                    Plotly.deleteTraces(graphContainer, -1);
                                    currentPredictionTrace = null; // Reset the trace tracker
                                } else {
                                    // Fetch the model's prediction data
                                    fetch(`/get-model-prediction/?stock_name=${encodeURIComponent(stockName)}&model_name=${encodeURIComponent(modelName)}`)
                                        .then(response => {
                                            if (!response.ok) {
                                                throw new Error(`HTTP error! status: ${response.status}`);
                                            }
                                            return response.json();
                                        })
                                        .then(data => {
                                            if (data.data) {
                                                // Add model data to the graph
                                                const newTrace = {
                                                    x: data.data.x, // Ensure sorted dates are sent from the backend
                                                    y: data.data.y,
                                                    type: "scatter",
                                                    mode: "lines+markers", // Add markers for clarity
                                                    name: modelName,
                                                    line: { color: "red", dash: "dot" } // Customize line style
                                                };
                                                Plotly.addTraces(graphContainer, newTrace);
                                                currentPredictionTrace = newTrace; // Update the tracker
                                            } else if (data.error) {
                                                console.error(`Error: ${data.error}`);
                                            }
                                        })
                                        .catch(error => {
                                            console.error('Error fetching model prediction:', error);
                                        });
                                }
                            });
                        });
                    } else if (data.error) {
                        predictionContainer.innerHTML = `<p>Error: ${data.error}</p>`;
                    } else {
                        predictionContainer.innerHTML = "<p>No prediction models available for this stock.</p>";
                    }
                })
                .catch(error => {
                    console.error('Error fetching prediction models:', error);
                    predictionContainer.innerHTML = `<p>Could not load prediction models. Please try again later.</p>`;
                });
        });
    });
});
