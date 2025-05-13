let temperatureChart, humidityChart, tankLevelChart;

function createCharts() {
    const ctxTemp = document.getElementById("temperatureChart").getContext("2d");
    const ctxHumidity = document.getElementById("humidityChart").getContext("2d");
    const ctxTank = document.getElementById("tankLevelChart").getContext("2d");

    if (temperatureChart) temperatureChart.destroy();
    if (humidityChart) humidityChart.destroy();
    if (tankLevelChart) tankLevelChart.destroy();

    temperatureChart = new Chart(ctxTemp, {
        type: "line",
        data: {
            labels: [],
            datasets: [{
                label: "Temperature (°C)",
                data: [],
                borderColor: "#00ffee",
                fill: false
            }]
        },
        options: { responsive: true, maintainAspectRatio: false }
    });

    humidityChart = new Chart(ctxHumidity, {
        type: "line",
        data: {
            labels: [],
            datasets: [{
                label: "Humidity (%)",
                data: [],
                borderColor: "#A100FF",
                fill: false
            }]
        },
        options: { responsive: true, maintainAspectRatio: false }
    });

    tankLevelChart = new Chart(ctxTank, {
        type: "line",
        data: {
            labels: [],
            datasets: [{
                label: "Tank Level (%)",
                data: [],
                borderColor: "#39FF14",
                fill: false
            }]
        },
        options: { responsive: true, maintainAspectRatio: false }
    });
}

function updateElement(id, value) {
    const el = document.getElementById(id);
    if (el) el.innerText = value;
}

function fetchSensorData() {
    fetch("/sensors/api/sensor-data/")
        .then(res => res.json())
        .then(data => {
            const d = data.sensor_data;
            const time = new Date().toLocaleTimeString();

            updateElement("temperature", `${d.temperature} °C`);
            updateElement("humidity", `${d.humidity} %`);
            updateElement("rainfall", d.rainfall ? "Yes" : "No");
            updateElement("tankLevel", `${d.tank_level} %`);
            updateElement("hvacLoad", `${d.hvac_load} %`);
            updateElement("decision", data.decision);

            temperatureChart.data.labels.push(time);
            temperatureChart.data.datasets[0].data.push(d.temperature);
            temperatureChart.update();

            humidityChart.data.labels.push(time);
            humidityChart.data.datasets[0].data.push(d.humidity);
            humidityChart.update();

            tankLevelChart.data.labels.push(time);
            tankLevelChart.data.datasets[0].data.push(d.tank_level);
            tankLevelChart.update();
        })
        .catch(err => console.error("Sensor fetch error:", err));
}

document.addEventListener("DOMContentLoaded", () => {
    createCharts();
    setInterval(fetchSensorData, 5000);

    // Manual Override Button click handler
    document.getElementById("manualOverrideBtn").addEventListener("click", function () {
        const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

        fetch("/sensors/api/manual-override/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken
            }
        })
        .then(response => response.json())
        .then(data => {
            alert(data.new_decision || "Override applied.");
            updateElement("decision", data.new_decision);
        
            const btn = document.getElementById("manualOverrideBtn");
            if (btn && data.new_decision.includes("Stop")) {
                btn.innerText = "Start Water Redirection";
            } else if (btn) {
                btn.innerText = "Stop Water Redirection";
            }
        })
        .catch(error => {
            console.error("Error during manual override:", error);
        });
    });
});
