let mapInstance = null;

const showMapBtn = document.getElementById("showMapBtn");
if (showMapBtn) {
    showMapBtn.addEventListener("click", async () => {
        const input = document.getElementById("locationInput").value.trim();
        if (!input) {
            alert("Please enter a city or coordinates.");
            return;
        }

        const geoRes = await fetch(
            `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(input)}`
        );
        const geoData = await geoRes.json();
        if (!geoData.length) {
            alert("Location not found.");
            return;
        }

        const lat = parseFloat(geoData[0].lat);
        const lon = parseFloat(geoData[0].lon);

        if (!mapInstance) {
            mapInstance = L.map("map").setView([lat, lon], 14);
            L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
                attribution: "&copy; OpenStreetMap contributors",
            }).addTo(mapInstance);
        } else {
            mapInstance.setView([lat, lon], 14);
            mapInstance.eachLayer((layer) => {
                if (layer instanceof L.Marker || layer instanceof L.Polyline) {
                    mapInstance.removeLayer(layer);
                }
            });
        }

        const now = new Date();
        const pos = SunCalc.getPosition(now, lat, lon);
        const times = SunCalc.getTimes(now, lat, lon);

        const elevation = (pos.altitude * 180) / Math.PI;
        const azimuth = ((pos.azimuth * 180) / Math.PI + 180) % 360;

        const sunrise = times.sunrise.toLocaleTimeString();
        const sunset = times.sunset.toLocaleTimeString();

        const solarText = `
            <b>Solar Elevation:</b> ${elevation.toFixed(1)}°<br>
            <b>Azimuth:</b> ${azimuth.toFixed(1)}°<br>
            <b>Sunrise:</b> ${sunrise}<br>
            <b>Sunset:</b> ${sunset}
        `;

        document.getElementById("solarData").innerHTML = solarText;

        const shadowLen = elevation > 0 ? 10 / Math.tan((elevation * Math.PI) / 180) : 0;
        const azRad = (azimuth * Math.PI) / 180;
        const lat2 = lat + (shadowLen / 111111) * Math.cos(azRad);
        const lon2 =
            lon + (shadowLen / (111111 * Math.cos((lat * Math.PI) / 180))) * Math.sin(azRad);

        L.marker([lat, lon]).addTo(mapInstance).bindPopup(solarText).openPopup();
        L.polyline(
            [
                [lat, lon],
                [lat2, lon2],
            ],
            { color: "orange", weight: 3 }
        ).addTo(mapInstance);

        drawSunPath(lat, lon);
    });
}

function drawSunPath(lat, lon) {
    if (!mapInstance) return;
    const pathPoints = [];
    for (let h = 6; h <= 18; h++) {
        const date = new Date();
        date.setHours(h, 0, 0);
        const pos = SunCalc.getPosition(date, lat, lon);
        const az = ((pos.azimuth * 180) / Math.PI + 180) % 360;
        const alt = (pos.altitude * 180) / Math.PI;
        if (alt > 0) {
            const len = 10 / Math.tan((alt * Math.PI) / 180);
            const azRad = (az * Math.PI) / 180;
            const lat2 = lat + (len / 111111) * Math.cos(azRad);
            const lon2 =
                lon + (len / (111111 * Math.cos((lat * Math.PI) / 180))) * Math.sin(azRad);
            pathPoints.push([lat2, lon2]);
        }
    }

    if (pathPoints.length > 1) {
        L.polyline(pathPoints, { color: "gold", weight: 2, dashArray: "5,5" }).addTo(mapInstance);
    }
}

const eligibilityForm = document.getElementById("eligibilityForm");
if (eligibilityForm) {
    eligibilityForm.addEventListener("submit", (event) => {
        event.preventDefault();
        const form = new FormData(event.target);
        const area = Number(form.get("area") || 0);

        const packingFactor = 0.7;
        const kwPerSqm = 0.17;
        const estKw = Math.max(0, area * packingFactor * kwPerSqm);
        const annualGen = estKw * 4.5 * 365;
        const estSavings = Math.round(annualGen * 6);

        const lines = [
            `Installable Capacity: ${estKw.toFixed(2)} kW`,
            `Annual Generation: ${Math.round(annualGen)} kWh`,
            `Approx. Annual Savings: ₹${estSavings.toLocaleString("en-IN")}`,
        ];

        document.getElementById("resultText").innerText = lines.join("\n");
        document.getElementById("resultCard").classList.remove("hidden");
    });
}

