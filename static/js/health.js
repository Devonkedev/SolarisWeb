let healthMap = null;

const healthShowMapBtn = document.getElementById("healthShowMapBtn");
if (healthShowMapBtn) {
    healthShowMapBtn.addEventListener("click", async () => {
        const input = document.getElementById("healthLocationInput").value.trim();
        if (!input) {
            alert("Please enter a location to analyse.");
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

        if (!healthMap) {
            healthMap = L.map("healthMap").setView([lat, lon], 15);
            L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
                attribution: "&copy; OpenStreetMap contributors",
            }).addTo(healthMap);
        } else {
            healthMap.setView([lat, lon], 15);
            healthMap.eachLayer((layer) => {
                if (layer instanceof L.Marker || layer instanceof L.Polyline) {
                    healthMap.removeLayer(layer);
                }
            });
        }

        const now = new Date();
        const pos = SunCalc.getPosition(now, lat, lon);
        const times = SunCalc.getTimes(now, lat, lon);

        const elevation = (pos.altitude * 180) / Math.PI;
        const azimuth = ((pos.azimuth * 180) / Math.PI + 180) % 360;

        const sunrise = times.sunrise.toLocaleTimeString();
        const solarNoon = times.solarNoon.toLocaleTimeString();
        const sunset = times.sunset.toLocaleTimeString();

        const solarText = `
            <b>Solar elevation:</b> ${elevation.toFixed(1)}°<br>
            <b>Azimuth:</b> ${azimuth.toFixed(1)}°<br>
            <b>Sunrise:</b> ${sunrise}<br>
            <b>Solar noon:</b> ${solarNoon}<br>
            <b>Sunset:</b> ${sunset}
        `;

        document.getElementById("healthSolarData").innerHTML = solarText;

        const shadowLen = elevation > 0 ? 10 / Math.tan((elevation * Math.PI) / 180) : 0;
        const azRad = (azimuth * Math.PI) / 180;
        const lat2 = lat + (shadowLen / 111111) * Math.cos(azRad);
        const lon2 =
            lon + (shadowLen / (111111 * Math.cos((lat * Math.PI) / 180))) * Math.sin(azRad);

        L.marker([lat, lon]).addTo(healthMap).bindPopup(solarText).openPopup();
        L.polyline(
            [
                [lat, lon],
                [lat2, lon2],
            ],
            { color: "orange", weight: 3 }
        ).addTo(healthMap);

        drawHealthSunPath(lat, lon);
    });
}

function drawHealthSunPath(lat, lon) {
    if (!healthMap) return;
    const pathPoints = [];
    for (let h = 5; h <= 19; h++) {
        const date = new Date();
        date.setHours(h, 0, 0, 0);
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
        L.polyline(pathPoints, { color: "gold", weight: 2, dashArray: "5,5" }).addTo(healthMap);
    }
}

