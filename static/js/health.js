const SOLAR_COLOR_STOPS = [
    { value: 0, color: [37, 52, 148] },
    { value: 0.35, color: [68, 130, 195] },
    { value: 0.55, color: [123, 204, 196] },
    { value: 0.75, color: [254, 224, 139] },
    { value: 1, color: [215, 48, 39] },
];

const DEFAULT_REGION = { latitude: 28.6139, longitude: 77.209, latitudeDelta: 0.4, longitudeDelta: 0.4 };
const GRID_SIZE = 14;
const effectiveDate = new Date();

const statusEl = document.getElementById("healthStatus");
const legendGradientEl = document.getElementById("healthLegendGradient");
const legendDateEl = document.getElementById("healthLegendDate");
const snapshotEl = document.getElementById("healthSolarSnapshot");
const timelineEl = document.getElementById("healthSolarTimeline");
const loaderEl = document.getElementById("healthLoading");
const searchInputEl = document.getElementById("healthLocationInput");
const searchBtnEl = document.getElementById("healthSearchBtn");
const recenterBtnEl = document.getElementById("healthRecenterBtn");

let healthMap = null;
let tileLayerGroup = null;
let centerMarker = null;

const clamp = (val, min, max) => Math.min(Math.max(val, min), max);
const toRadians = (deg) => (deg * Math.PI) / 180;

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

const computeSolarPotential = (lat, lon, date, region) => {
    const day = getDayOfYear(date);
    const declination = 23.44 * Math.sin(toRadians(((360 / 365) * (284 + day)) % 360));
    const latRad = toRadians(lat);
    const decRad = toRadians(declination);

    const solarAltitude = Math.asin(Math.sin(latRad) * Math.sin(decRad) + Math.cos(latRad) * Math.cos(decRad));
    const altitudeFactor = clamp(Math.sin(solarAltitude), 0, 1);

    const noise = pseudoRandom(lat, lon);
    const hazeFactor = 0.75 + noise * 0.25;

    const reliefNoise = pseudoRandom(lat * 0.7, lon * 0.7) - 0.5;
    const reliefFactor = clamp(0.85 + reliefNoise * 0.25, 0, 1.1);

    const latOffset = Math.abs(lat - region.latitude) / Math.max(region.latitudeDelta, 0.0001);
    const lonOffset = Math.abs(lon - region.longitude) / Math.max(region.longitudeDelta, 0.0001);
    const distanceFactor = clamp(1 - Math.sqrt(latOffset * latOffset + lonOffset * lonOffset) * 0.45, 0.55, 1);

    return clamp(altitudeFactor * hazeFactor * reliefFactor * distanceFactor, 0, 1);
};

const generateSolarHeatTiles = (region, date, gridSize = GRID_SIZE) => {
    const tiles = [];
    const effectiveDate = date ?? new Date();

    const latStart = region.latitude - region.latitudeDelta / 2;
    const lonStart = region.longitude - region.longitudeDelta / 2;
    const latStep = region.latitudeDelta / gridSize;
    const lonStep = region.longitudeDelta / gridSize;

    for (let row = 0; row < gridSize; row++) {
        const latBottom = latStart + row * latStep;
        const latTop = latBottom + latStep;

        for (let col = 0; col < gridSize; col++) {
            const lonLeft = lonStart + col * lonStep;
            const lonRight = lonLeft + lonStep;

            const centerLat = latBottom + latStep / 2;
            const centerLon = lonLeft + lonStep / 2;
            const value = computeSolarPotential(centerLat, centerLon, effectiveDate, region);

            if (value <= 0.02) continue;

            tiles.push({
                coordinates: [
                    { latitude: latBottom, longitude: lonLeft },
                    { latitude: latBottom, longitude: lonRight },
                    { latitude: latTop, longitude: lonRight },
                    { latitude: latTop, longitude: lonLeft },
                ],
                fillColor: interpolateColor(value),
                value,
            });
        }
    }

    return tiles;
};

const setStatus = (message, tone = "info") => {
    if (!statusEl) return;
    const toneClasses = {
        info: "text-xs text-slate-500",
        success: "text-xs text-emerald-600",
        error: "text-xs text-rose-600",
    };
    statusEl.textContent = message || "";
    statusEl.className = toneClasses[tone] || toneClasses.info;
};

const toggleLoader = (show) => {
    if (!loaderEl) return;
    loaderEl.classList.toggle("hidden", !show);
};

const regionFromMap = () => {
    if (!healthMap) return DEFAULT_REGION;
    const bounds = healthMap.getBounds();
    const center = healthMap.getCenter();
    const latitudeDelta = Math.max(Math.abs(bounds.getNorth() - bounds.getSouth()), 0.0005);
    const longitudeDelta = Math.max(Math.abs(bounds.getEast() - bounds.getWest()), 0.0005);

    return {
        latitude: center.lat,
        longitude: center.lng,
        latitudeDelta,
        longitudeDelta,
    };
};

const renderLegend = () => {
    if (!legendGradientEl) return;
    legendGradientEl.innerHTML = "";

    const stops = Array.from({ length: 12 }).map((_, idx) => idx / 11);
    stops.forEach((value) => {
        const segment = document.createElement("div");
        segment.style.flex = "1";
        segment.style.backgroundColor = interpolateColor(value);
        segment.setAttribute("aria-hidden", "true");
        legendGradientEl.appendChild(segment);
    });

    if (legendDateEl) {
        legendDateEl.textContent = effectiveDate.toDateString();
    }
};

const updateSolarSummary = () => {
    if (!healthMap || !snapshotEl || !timelineEl) return;

    const center = healthMap.getCenter();
    const pos = SunCalc.getPosition(effectiveDate, center.lat, center.lng);
    const times = SunCalc.getTimes(effectiveDate, center.lat, center.lng);

    const elevation = ((pos.altitude * 180) / Math.PI).toFixed(1);
    const azimuth = (((pos.azimuth * 180) / Math.PI + 180) % 360).toFixed(1);

    snapshotEl.innerHTML = `
        <span class="text-slate-800">${elevation}° elevation</span>
        <span class="text-slate-400 px-2">|</span>
        <span class="text-slate-800">${azimuth}° azimuth</span>
    `;

    const formatTime = (date) =>
        date ? new Date(date).toLocaleTimeString(undefined, { hour: "2-digit", minute: "2-digit" }) : "—";

    timelineEl.innerHTML = `
        <span class="font-semibold text-emerald-600">Sunrise ${formatTime(times.sunrise)}</span>
        <span class="text-slate-400 px-1">/</span>
        <span class="font-semibold text-sky-600">Solar noon ${formatTime(times.solarNoon)}</span>
        <span class="text-slate-400 px-1">/</span>
        <span class="font-semibold text-rose-500">Sunset ${formatTime(times.sunset)}</span>
    `;
};

const drawHeatTiles = () => {
    if (!healthMap || !tileLayerGroup) return;
    tileLayerGroup.clearLayers();

    const region = regionFromMap();
    const tiles = generateSolarHeatTiles(region, effectiveDate);

    tiles.forEach((tile) => {
        const polygon = L.polygon(
            tile.coordinates.map((coord) => [coord.latitude, coord.longitude]),
            {
                stroke: false,
                fillColor: tile.fillColor,
                fillOpacity: 1,
                interactive: false,
            }
        );
        tileLayerGroup.addLayer(polygon);
    });
};

const syncMapState = () => {
    if (!healthMap) return;
    if (centerMarker) {
        centerMarker.setLatLng(healthMap.getCenter());
    }
    drawHeatTiles();
    updateSolarSummary();
};

const bootMap = (initialRegion) => {
    const mapContainer = document.getElementById("healthMap");
    if (!mapContainer) return;

    const defaultZoom = 13;
    healthMap = L.map(mapContainer, {
        zoomControl: false,
        attributionControl: false,
    }).setView([initialRegion.latitude, initialRegion.longitude], defaultZoom);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "&copy; OpenStreetMap contributors",
        maxZoom: 19,
    }).addTo(healthMap);

    L.control.zoom({ position: "bottomright" }).addTo(healthMap);

    tileLayerGroup = L.layerGroup().addTo(healthMap);
    centerMarker = L.marker([initialRegion.latitude, initialRegion.longitude], {
        icon: L.divIcon({
            className: "health-center-marker",
            html: '<div style="width:16px;height:16px;border-radius:9999px;background:#0ea5e9;border:2px solid white;box-shadow:0 0 0 4px rgba(14,165,233,0.25);"></div>',
            iconAnchor: [8, 8],
        }),
        interactive: false,
    }).addTo(healthMap);

    healthMap.on("moveend", () => {
        syncMapState();
    });

    renderLegend();
    syncMapState();
};

const fetchApproximateLocation = async () => {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 5000);

    try {
        const response = await fetch("https://ipapi.co/json/", { signal: controller.signal });
        clearTimeout(timeout);

        if (!response.ok) {
            throw new Error("Failed to fetch approximate location");
        }
        const data = await response.json();
        if (typeof data.latitude !== "number" || typeof data.longitude !== "number") {
            throw new Error("Incomplete location response");
        }

        return {
            latitude: data.latitude,
            longitude: data.longitude,
            latitudeDelta: 0.6,
            longitudeDelta: 0.6,
        };
    } catch (error) {
        clearTimeout(timeout);
        console.warn("Approx location unavailable", error);
        return DEFAULT_REGION;
    }
};

const geocodeQuery = async (query) => {
    const response = await fetch(
        `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}`
    );
    if (!response.ok) {
        throw new Error("Unable to search location");
    }
    const results = await response.json();
    if (!results.length) {
        throw new Error("Location not found");
    }
    return {
        latitude: parseFloat(results[0].lat),
        longitude: parseFloat(results[0].lon),
    };
};

const handleSearch = async () => {
    if (!searchInputEl) return;
    const query = searchInputEl.value.trim();
    if (!query) {
        setStatus("Enter an address or PIN to reposition the map.", "info");
        return;
    }
    setStatus("Searching for rooftop…", "info");
    toggleLoader(true);
    try {
        const result = await geocodeQuery(query);
        if (healthMap) {
            healthMap.setView([result.latitude, result.longitude], healthMap.getZoom());
        }
        setStatus("Pinned location successfully.", "success");
    } catch (error) {
        console.error(error);
        setStatus("Could not locate that search. Try another address.", "error");
    } finally {
        toggleLoader(false);
    }
};

const initialize = async () => {
    const mapContainer = document.getElementById("healthMap");
    if (!mapContainer) return;

    toggleLoader(true);
    setStatus("Fetching an approximate starting point…", "info");

    const initialRegion = await fetchApproximateLocation();
    bootMap(initialRegion);

    toggleLoader(false);
    setStatus("Drag to explore. Re-centre anytime with the controls.", "success");
};

if (searchBtnEl) {
    searchBtnEl.addEventListener("click", handleSearch);
}

if (searchInputEl) {
    searchInputEl.addEventListener("keydown", (event) => {
        if (event.key === "Enter") {
            event.preventDefault();
            handleSearch();
        }
    });
}

if (recenterBtnEl) {
    recenterBtnEl.addEventListener("click", async () => {
        toggleLoader(true);
        setStatus("Re-centering to your approximate location…", "info");
        const region = await fetchApproximateLocation();
        if (healthMap) {
            healthMap.setView([region.latitude, region.longitude], healthMap.getZoom());
        }
        toggleLoader(false);
        setStatus("View updated. Drag to fine-tune the map.", "success");
    });
}

document.addEventListener("DOMContentLoaded", initialize);

