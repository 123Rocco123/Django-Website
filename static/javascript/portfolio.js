document.addEventListener("DOMContentLoaded", function () {
    const graphContainer = document.querySelector('.graphContainer');
    const newsContainer = document.querySelector('.news');
    const predictionContainer = document.querySelector('.predictionList');
    const dailyStockTableBody = document.querySelector(".dailyStockTable tbody");

    // Store the currently displayed prediction trace
    let currentPredictionTrace = null;

    // Show placeholder messages initially
    graphContainer.innerHTML = "<p>Select a stock to view its graph.</p>";
    newsContainer.innerHTML = "<p>Select a stock to view its related news.</p>";
    predictionContainer.innerHTML = "<p>Select a stock to view prediction models.</p>";
    dailyStockTableBody.innerHTML = "<p>Select a stock to view daily values.</p>";

    const stockItems = document.querySelectorAll('.stock-item');
    stockItems.forEach(item => {
        item.addEventListener('click', function () {
            const stockName = this.querySelector('.stock-name').textContent.trim();

            // Show loading messages while fetching data
            graphContainer.innerHTML = "<p>Loading graph...</p>";
            newsContainer.innerHTML = "<p>Loading news...</p>";
            predictionContainer.innerHTML = "<p>Loading prediction models...</p>";
            dailyStockTableBody.innerHTML = "<tr><td colspan='4'>Loading stock data...</td></tr>";

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

            // Fetch and update the daily stock values
            fetch(`/get-stock-values/?stock_name=${encodeURIComponent(stockName)}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    dailyStockTableBody.innerHTML = "";
                    if (data.stock_values && data.stock_values.length > 0) {
                        data.stock_values.forEach(stock => {
                            const row = document.createElement("tr");
                            row.innerHTML = `
                                <td>${stock.date}</td>
                                <td>${stock.open}</td>
                                <td>${stock.high}</td>
                                <td>${stock.low}</td>
                                <td>${stock.closing}</td>
                                <td>${stock.volume}</td>
                            `;
                            dailyStockTableBody.appendChild(row);
                        });
                    } else {
                        dailyStockTableBody.innerHTML = "<tr><td colspan='4'>No stock data available for this stock.</td></tr>";
                    }
                })
                .catch(error => {
                    console.error('Error fetching stock values:', error);
                    dailyStockTableBody.innerHTML = "<tr><td colspan='4'>Could not load stock data. Please try again later.</td></tr>";
                });

            // Fetch and update the stock recommendations
            fetch(`/get-analyst-recommendations/?stock_name=${stockName}`)
                .then(response => response.json())
                    .then(data => {
                        if (data.error) {
                            console.error(data.error);
                            return;
                        }

                        // Ensure the table body element is correctly selected
                        const analystRecommendationsBody = document.querySelector('.analystRecommendations tbody');
                        if (!analystRecommendationsBody) {
                            console.error('Table body not found. Check the table structure or selector.');
                            return;
                        }

                        analystRecommendationsBody.innerHTML = ''; // Clear existing rows

                        data.recommendations.forEach(entry => {
                            const row = document.createElement('tr');

                            row.innerHTML = `
                                <td>${entry.date}</td>
                                <td>${entry.total}</td>
                                <td>${entry.strong_buy}</td>
                                <td>${entry.buy}</td>
                                <td>${entry.hold}</td>
                                <td>${entry.sell}</td>
                                <td>${entry.strong_sell}</td>
                            `;

                            analystRecommendationsBody.appendChild(row);
                        });
                    })
            .catch(error => console.error('Error fetching recommendations:', error));

            // Adds the functionality for the price target button
            fetch(`/get-pricetargets/?stock_name=${stockName}`)
                .then(response => response.json())
                    .then(data => {
                        if (data.error) {
                            console.error(data.error);
                            return;
                        }

                        // Ensure the table body element is correctly selected
                        const priceTargetBody = document.querySelector('.priceTarget tbody');
                        if (!priceTargetBody) {
                            console.error('Table body not found. Check the table structure or selector.');
                            return;
                        }

                        priceTargetBody.innerHTML = ''; // Clear existing rows

                        data.priceTargets.forEach(entry => {
                            const row = document.createElement('tr');

                            row.innerHTML = `
                                <td>${entry.date}</td>
                                <td>${entry.low}</td>
                                <td>${entry.high}</td>
                                <td>${entry.mean}</td>
                                <td>${entry.median}</td>
                                <td style="background-color: ${entry.more === false ? 'rgba(255, 99, 71, 0.5)' : 'rgba(144, 238, 144, 0.5)'};">${entry.current}</td>
                            `;

                            priceTargetBody.appendChild(row);
                        });
                    })
                    .catch(error => console.error('Error fetching recommendations:', error));

            // Adds the functionality for the price target button
            fetch(`/get-ratings/?stock_name=${stockName}`)
                .then(response => response.json())
                    .then(data => {
                        if (data.error) {
                            console.error(data.error);
                            return;
                        }

                        // Ensure the table body element is correctly selected
                        const RatingsBody = document.querySelector('.Ratings tbody');
                        if (!RatingsBody) {
                            console.error('Table body not found. Check the table structure or selector.');
                            return;
                        }

                        RatingsBody.innerHTML = ''; // Clear existing rows

                        if ("error" in data.ratings) {
                            const row = document.createElement('tr');
                            
                            row.innerHTML = `
                                <td colspan="5">N/a</td>
                            `;

                            RatingsBody.appendChild(row);
                        } else {
                            data.ratings.forEach(entry => {
                                const row = document.createElement('tr');
                                
                                row.innerHTML = `
                                <td>${entry.date}</td>
                                <td>${entry.Firm}</td>
                                <td>${entry.FromGrade}</td>
                                <td>${entry.ToGrade}</td>
                                <td style="background-color: ${
                                    entry.Outlook === 'up' ? 'rgba(144, 238, 144, 0.5)' :
                                    entry.Outlook === 'down' ? 'rgba(255, 99, 71, 0.5)' :
                                    ''
                                };">
                                    ${entry.Outlook}
                                </td>
                            `;
    
                                RatingsBody.appendChild(row);
                            });
                        }
                    })
                    .catch(error => console.error('Error fetching recommendations:', error));

            // Adds the stock information functionality to the main script
            fetch(`/getStockInfo/?stock_name=${stockName}`)
                .then(response => response.json())
                    .then(data => {
                        if (data.error) {
                            console.error(data.error);
                            return;
                        }

                        // Ensure the table body element is correctly selected
                            // We then output the data to the div tag inside of the stockInformationDiv class
                        const stockInformationBody = document.querySelector('.companyDetails ul');
                        if (!stockInformationBody) {
                            console.error('Table body not found. Check the table structure or selector.');
                            return;
                        }

                        // Clear existing rows
                        stockInformationBody.innerHTML = '';

                        data.information.forEach(entry => {
                            const row = document.createElement('p');

                            row.innerHTML = `
                                <li><strong>CEO:</strong> ${entry.CEO}</li>
                                <li><strong>Market:</strong> ${entry.market}</li>
                                <li><strong>Sector:</strong> ${entry.type}</li>
                                <li><strong>Industry:</strong> ${entry.industry}</li>
                                <br>
                                <li><strong>Headquarters:</strong> ${entry.hq}</li>
                                <li><strong>Country:</strong> ${entry.country}</li>
                                <li><strong>Employees:</strong> ${entry.employees || 'N/A'}</li>
                            `;

                            stockInformationBody.appendChild(row);
                        });
                    })
                    .catch(error => console.error('Error fetching recommendations:', error));

                // 
                fetch(`/getOfficeres/?stock_name=${stockName}`)
                    .then(response => response.json())
                        .then(data => {
                            if (data.error) {
                                console.error(data.error);
                                return;
                            }
    
                            // Ensure the table body element is correctly selected
                                // We then output the data to the div tag inside of the stockInformationDiv class
                            const keyPeopleListBody = document.querySelector('.keyPeople .keyPeopleList');
                            if (!keyPeopleListBody) {
                                console.error('Table body not found. Check the table structure or selector.');
                                return;
                            }
    
                            keyPeopleListBody.innerHTML = ''; // Clear existing rows
    
                            data.officers.forEach(entry => {
                                const row = document.createElement('p');
    
                                row.innerHTML = `
                                    <li><strong>Name:</strong> ${entry.name}</li>
                                    <li><strong>Role:</strong> ${entry.role}</li>
                                `;
    
                                keyPeopleListBody.appendChild(row);
                            });
                        })
                        .catch(error => console.error('Error fetching recommendations:', error));
                
                fetch(`/returnClosingPrices/?stock_name=${stockName}`)
                    .then(response => response.json())
                        .then(data => {
                            if (data.error) {
                                console.error(data.error);
                                return;
                            }
                    
                            // Ensure the elements for displaying stock data are correctly selected
                            const stockInfoDiv  = document.querySelector('.priceInformation');
                            if (!stockInfoDiv) {
                                console.error('Stock information div not found. Check the HTML structure or selector.');
                                return;
                            }
                    
                            // Clear existing content
                            stockInfoDiv.innerHTML  = '';
                    
                            // Display the fetched closing and after-hours prices
                            const closingPriceElem = document.createElement('div');
                            closingPriceElem.innerHTML = `
                                                    <div class="priceInformationInner">
                                                        <h3>Closing Price:</h3> <span class="closingPrice">${data.currency}${data.closing}</span>

                                                        <h3>After Hours Price:</h3> <span class="afterHour">${data.currency}${data.afterHours}</span>
                                                    </div>`;

                            stockInfoDiv.appendChild(closingPriceElem);
                        })
                        .catch(error => console.error('Error fetching stock closing prices:', error));
                    
        });
    });
});
