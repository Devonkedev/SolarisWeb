let healthMap = null;
let solarTileLayer = null;

const SOLAR_COLOR_STOPS = [
    { value: 0, color: [37, 52, 148] },
    { value: 0.35, color: [68, 130, 195] },
    { value: 0.55, color: [123, 204, 196] },
    { value: 0.75, color: [254, 224, 139] },
    { value: 1, color: [215, 48, 39] },
];

const clamp = (val, min, max) => {
    if (val < min) return min;
    if (val > max) return max;
    return val;
};

const pseudoRandom = (lat, lon) => {
    const x = Math.sin(lat * 12.9898 + lon * 78.233) * 43758.5453;
    return x - Math.floor(x);
};

const interpolateColor = (value) => {
    const v = clamp(value, 0, 1);
    let lower = SOLAR_COLOR_STOPS[0];
    let upper = SOLAR_COLOR_STOPS[SOLAR_COLOR_STOPS.length - 1];
    for (let i = 0; i < SOLAR_COLOR_STOPS.length - 1; i++) {
        const current = SOLAR_COLOR_STOPS[i];
        const next = SOLAR_COLOR_STOPS[i + 1];
        if (v >= current.value && v <= next.value) {
            lower = current;
            upper = next;
            break;
        }
    }
    const range = upper.value - lower.value || 1;
    const t = clamp((v - lower.value) / range, 0, 1);
    const r = Math.round(lower.color[0] + (upper.color[0] - lower.color[0]) * t);
    const g = Math.round(lower.color[1] + (upper.color[1] - lower.color[1]) * t);
    const b = Math.round(lower.color[2] + (upper.color[2] - lower.color[2]) * t);
    const alpha = 0.18 + v * 0.55;
    return `rgba(${r}, ${g}, ${b}, ${alpha.toFixed(2)})`;
};

const getDayOfYear = (date) => {
    const utc = Date.UTC(date.getUTCFullYear(), date.getUTCMonth(), date.getUTCDate());
    const start = Date.UTC(date.getUTCFullYear(), 0, 0);
    return Math.floor((utc - start) / (24 * 60 * 60 * 1000));
};

const toRadians = (deg) => (deg * Math.PI) / 180;

const computeSolarPotential = (lat, lon, date, region) => {
    const day = getDayOfYear(date);
    const declination = 23.44 * Math.sin(toRadians(((360 / 365) * (284 + day)) % 360));
    const latRad = toRadians(lat);
    const decRad = toRadians(declination);
    const solarAltitude = Math.asin(
        Math.sin(latRad) * Math.sin(decRad) + Math.cos(latRad) * Math.cos(decRad)
    );
    const altitudeFactor = clamp(Math.sin(solarAltitude), 0, 1);
    const noise = pseudoRandom(lat, lon);
    const hazeFactor = 0.75 + noise * 0.25;
    const reliefNoise = pseudoRandom(lat * 0.7, lon * 0.7) - 0.5;
    const reliefFactor = clamp(0.85 + reliefNoise * 0.25, 0, 1.1);
    const latOffset = Math.abs(lat - region.latitude) / Math.max(region.latitudeDelta, 0.0001);
    const lonOffset = Math.abs(lon - region.longitude) / Math.max(region.longitudeDelta, 0.0001);
    const distanceFactor = clamp(
        1 - Math.sqrt(latOffset * latOffset + lonOffset * lonOffset) * 0.45,
        0.55,
        1
    );
    return clamp(altitudeFactor * hazeFactor * reliefFactor * distanceFactor, 0, 1);
};

const generateSolarHeatTiles = (bounds, date, region, gridSize = 12) => {
    const tiles = [];
    if (!bounds || !bounds.isValid()) return tiles;

    const south = bounds.getSouth();
    const north = bounds.getNorth();
    const west = bounds.getWest();
    const east = bounds.getEast();

    const latDelta = north - south;
    const lonDelta = east - west;
    const latStep = latDelta / gridSize;
    const lonStep = lonDelta / gridSize;

    for (let row = 0; row < gridSize; row++) {
        const latBottom = south + row * latStep;
        const latTop = latBottom + latStep;
        for (let col = 0; col < gridSize; col++) {
            const lonLeft = west + col * lonStep;
            const lonRight = lonLeft + lonStep;
            const centerLat = latBottom + latStep / 2;
            const centerLon = lonLeft + lonStep / 2;
            const value = computeSolarPotential(centerLat, centerLon, date, region);
            if (value <= 0.02) continue;
            tiles.push({
                coordinates: [
                    [latBottom, lonLeft],
                    [latBottom, lonRight],
                    [latTop, lonRight],
                    [latTop, lonLeft],
                ],
                fillColor: interpolateColor(value),
            });
        }
    }

    return tiles;
};

const renderSolarTiles = () => {
    if (!healthMap) return;
    const bounds = healthMap.getBounds();
    if (!bounds || !bounds.isValid()) return;

    const center = bounds.getCenter();
    const region = {
        latitude: center.lat,
        longitude: center.lng,
        latitudeDelta: Math.max(bounds.getNorth() - bounds.getSouth(), 0.0001),
        longitudeDelta: Math.max(bounds.getEast() - bounds.getWest(), 0.0001),
    };

    const tiles = generateSolarHeatTiles(bounds, new Date(), region);

    if (solarTileLayer) {
        solarTileLayer.remove();
    }
    solarTileLayer = L.layerGroup();
    tiles.forEach((tile) => {
        const polygon = L.polygon(tile.coordinates, {
            stroke: false,
            fillColor: tile.fillColor,
            fillOpacity: 1,
            interactive: false,
        });
        solarTileLayer.addLayer(polygon);
    });
    solarTileLayer.addTo(healthMap);
};

const updateSolarInfo = (lat, lon) => {
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
    const lon2 = lon + (shadowLen / (111111 * Math.cos((lat * Math.PI) / 180))) * Math.sin(azRad);

    L.marker([lat, lon]).addTo(healthMap).bindPopup(solarText).openPopup();
    L.polyline(
        [
            [lat, lon],
            [lat2, lon2],
        ],
        { color: "orange", weight: 3 }
    ).addTo(healthMap);

    drawHealthSunPath(lat, lon);
};

const resetDynamicLayers = () => {
    if (!healthMap) return;
    healthMap.eachLayer((layer) => {
        if (layer instanceof L.Marker || layer instanceof L.Polyline) {
            healthMap.removeLayer(layer);
        }
    });
    if (solarTileLayer) {
        solarTileLayer.remove();
        solarTileLayer = null;
    }
};

const initializeMap = (lat, lon, zoom = 13) => {
    if (!healthMap) {
        healthMap = L.map("healthMap").setView([lat, lon], zoom);
        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
            attribution: "&copy; OpenStreetMap contributors",
        }).addTo(healthMap);
        healthMap.on("moveend", () => {
            renderSolarTiles();
        });
    } else {
        healthMap.setView([lat, lon], zoom);
    }
    renderSolarTiles();
};

const handleLocationSearch = async () => {
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

    resetDynamicLayers();
    initializeMap(lat, lon, 14);
    updateSolarInfo(lat, lon);
};

const healthShowMapBtn = document.getElementById("healthShowMapBtn");
if (healthShowMapBtn) {
    healthShowMapBtn.addEventListener("click", async () => {
        try {
            await handleLocationSearch();
        } catch (err) {
            console.error("Unable to render solar heat map", err);
            alert("Unable to render solar heat map right now. Please try again shortly.");
        }
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
            const lon2 = lon + (len / (111111 * Math.cos((lat * Math.PI) / 180))) * Math.sin(azRad);
            pathPoints.push([lat2, lon2]);
        }
    }
    if (pathPoints.length > 1) {
        L.polyline(pathPoints, { color: "gold", weight: 2, dashArray: "5,5" }).addTo(healthMap);
    }
}

