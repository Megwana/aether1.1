// Global chart variables for access across functions
let temperatureChart, humidityChart, tankLevelChart;

/**
 * Initializes the three line charts (Temperature, Humidity, Tank Level)
 * using Chart.js if the canvas elements are present.
 */
function createCharts() {
    const ctxTemp = document.getElementById("temperatureChart");
    const ctxHumidity = document.getElementById("humidityChart");
    const ctxTank = document.getElementById("tankLevelChart");

 // Only initialize charts if all chart elements exist
    if (ctxTemp && ctxHumidity && ctxTank) {
        temperatureChart = new Chart(ctxTemp.getContext("2d"), {
            type: "line",
            data: { labels: [], datasets: [{ label: "Temperature (°C)", data: [], borderColor: "#00ffee", fill: false }] },
            options: { responsive: true, maintainAspectRatio: false }
        });

        humidityChart = new Chart(ctxHumidity.getContext("2d"), {
            type: "line",
            data: { labels: [], datasets: [{ label: "Humidity (%)", data: [], borderColor: "#A100FF", fill: false }] },
            options: { responsive: true, maintainAspectRatio: false }
        });

        tankLevelChart = new Chart(ctxTank.getContext("2d"), {
            type: "line",
            data: { labels: [], datasets: [{ label: "Tank Level (%)", data: [], borderColor: "#39FF14", fill: false }] },
            options: { responsive: true, maintainAspectRatio: false }
        });
    }
}

/**
 * Updates the inner text of a DOM element by ID if it exists.
 * Keeps code DRY by reusing this for all data updates.
 * 
 * @param {string} id - The ID of the DOM element to update.
 * @param {string} value - The value to set as innerText.
 */
function updateElement(id, value) {
    const element = document.getElementById(id);
    if (element) element.innerText = value;
}

/**
 * Fetches the latest sensor data from the API endpoint,
 * updates both UI elements and chart datasets with new values.
 */
function fetchSensorData() {
    fetch(`${BASE_URL}/sensors/api/sensor-data/`)
        .then(response => {
            if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
            return response.json();
        })
        .then(data => {
            let currentTime = new Date().toLocaleTimeString();

            // Update UI text elements with the latest data
            updateElement("temperature", `${data.sensor_data.temperature} °C`);
            updateElement("humidity", `${data.sensor_data.humidity} %`);
            updateElement("rainfall", data.sensor_data.rainfall ? "Yes" : "No");
            updateElement("tankLevel", `${data.sensor_data.tank_level} %`);
            updateElement("hvacLoad", `${data.sensor_data.hvac_load} %`);
            updateElement("decision", data.decision);

            // Add new data points to each chart
            if (temperatureChart && humidityChart && tankLevelChart) {
                temperatureChart.data.labels.push(currentTime);
                temperatureChart.data.datasets[0].data.push(data.sensor_data.temperature);
                temperatureChart.update();

                humidityChart.data.labels.push(currentTime);
                humidityChart.data.datasets[0].data.push(data.sensor_data.humidity);
                humidityChart.update();

                tankLevelChart.data.labels.push(currentTime);
                tankLevelChart.data.datasets[0].data.push(data.sensor_data.tank_level);
                tankLevelChart.update();
            }
        })
        .catch(error => console.error("Error fetching sensor data:", error));
}


/**
 * Sends an override action to the server and updates the decision text.
 * Also displays a brief override confirmation message.
 * 
 * @param {string} action - The override action to send.
 */
function overrideDecision(action) {
    fetch(`${BASE_URL}/api/override?decision=${action}`, { method: "GET" })
        .then(response => response.json())
        .then(data => {
            updateElement("decision", data.new_decision); 

            // Display override confirmation message with fade effect
            const overrideMessage = document.getElementById("overrideMessage");
            if (overrideMessage) {
                overrideMessage.innerText = `Override Applied: ${data.new_decision}`;
                overrideMessage.style.opacity = "1";
                overrideMessage.style.transform = "scale(1)";
                setTimeout(() => {
                    overrideMessage.style.opacity = "0"; 
                    overrideMessage.style.transform = "scale(0.9)";
                }, 5000);
            }
        })
        .catch(error => console.error("Error overriding decision:", error));
}

document.addEventListener("DOMContentLoaded", function () {
    const thresholdForm = document.getElementById("thresholdForm");
    if (thresholdForm) {
        thresholdForm.addEventListener("submit", function (event) {
            event.preventDefault();

            const humidityThreshold = document.getElementById("humidityThreshold").value;
            const temperatureThreshold = document.getElementById("temperatureThreshold").value;

            fetch(`${BASE_URL}/api/set-thresholds`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ humidity: humidityThreshold, temperature: temperatureThreshold })
            })
            .then(response => response.json())
            .then(data => {
                const saveMessage = document.getElementById("saveMessage");
                if (saveMessage) {
                    saveMessage.style.opacity = "1";
                    setTimeout(() => saveMessage.style.opacity = "0", 3000);
                }
            })
            .catch(error => console.error("Error saving thresholds:", error));
        });
    }


    createCharts();
    setInterval(fetchSensorData, 5000);
});
