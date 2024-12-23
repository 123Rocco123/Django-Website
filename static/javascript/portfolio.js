document.addEventListener("DOMContentLoaded", function () {
    const graphContainer = document.querySelector('.graphContainer');
    const newsContainer = document.querySelector('.news');

    // Show placeholder messages initially
    graphContainer.innerHTML = "<p>Select a stock to view its graph.</p>";
    newsContainer.innerHTML = "<p>Select a stock to view its related news.</p>";

    const stockItems = document.querySelectorAll('.stock-item');
    stockItems.forEach(item => {
        item.addEventListener('click', function () {
            const stockName = this.querySelector('.stock-name').textContent.trim();

            // Show loading messages while fetching data
            graphContainer.innerHTML = "<p>Loading graph...</p>";
            newsContainer.innerHTML = "<p>Loading news...</p>";

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
                        // Clear and populate the news container with articles
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
        });
    });
});
