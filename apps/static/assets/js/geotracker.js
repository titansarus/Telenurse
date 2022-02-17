let myMap = null;
let violetIcon = null;
let watchId = null;
let currentLocationMarker = null;
let currentLocationMarkerSecond = null;
let trackingMarkers = new Array(5);
let trackingMarkerIndex = 0; // current counter

function locate_position(latitude, longitude, second=false) {
    console.log("Moving to current location", latitude, longitude);
    if (second) {
        if (currentLocationMarkerSecond === null)
        {
            currentLocationMarkerSecond = L.marker([latitude, longitude], {icon: new L.Icon({
                iconUrl: 'https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png',
                shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.4.0/images/marker-shadow.png',
                iconSize: [25, 41],
                iconAnchor: [12, 41],
                popupAnchor: [1, -34],
                shadowSize: [41, 41]
            })}).addTo(myMap);
        }
        currentLocationMarkerSecond.setLatLng([latitude, longitude]).addTo(myMap);
    } else {
        if (currentLocationMarker === null) {
            currentLocationMarker = L.marker([latitude, longitude]).addTo(myMap);
        }
        currentLocationMarker.setLatLng([latitude, longitude]).addTo(myMap);
    }
    myMap.panTo([latitude, longitude]);
}

function single_locate() {
    navigator.geolocation.getCurrentPosition(function (position) {
            locate_position(position.coords.latitude, position.coords.longitude, false)
        },
        function (positionError) {
            console.debug(positionError.message);
        }, {timeout: 5000, enableHighAccuracy: true});
}

function index_startup() {
    if (window.location.protocol !== 'http:') {
        alert("Geolocation requires usage of HTTPS, and you're using HTTP. Trying to JS redirect...");
        window.location.protocol = "http:";
        return;
    }

    if (!navigator.geolocation) {
        alert("Your browser doesn't support geolocation.");
        return;
    }
    myMap = L.map("map");
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 18
    }).addTo(myMap);
    myMap.setView([62.6050, 29.756], 13);

    violetIcon = new L.Icon({
        iconUrl: 'https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-violet.png',
        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.4.0/images/marker-shadow.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]
    });

    navigator.geolocation.getCurrentPosition(function (position) {
        // First location got
        console.log("Moving to current location", position);
        currentLocationMarker = L.marker([position.coords.latitude, position.coords.longitude]).addTo(myMap);
        myMap.panTo([position.coords.latitude, position.coords.longitude]);
    },
    function (positionError) {
        alert("Geolocation failure");
        console.debug(positionError.message);
    }, {maximumAge: 5000, timeout: 5000, enableHighAccuracy: true});

    
    let is_tracking_active = localStorage.getItem("is_tracking_active")
    if (is_tracking_active) {

        watchId = navigator.geolocation.watchPosition(function (position) {
            watcherCallback(position);

        }, null, {timeout: 5000, enableHighAccuracy: true});
    }
}

function watcherCallback(position) {
    let ad_id = localStorage.getItem("tracking_ad_id");
    console.log("Tracked new position", position);
    if (trackingMarkers[trackingMarkerIndex]) {
        // Remove oldest markeer
        myMap.removeLayer(trackingMarkers[trackingMarkerIndex]);

    }
    trackingMarkers[trackingMarkerIndex] = L.marker([position.coords.latitude, position.coords.longitude], {icon: violetIcon});
    trackingMarkers[trackingMarkerIndex].addTo(myMap);
    trackingMarkerIndex++;
    if (trackingMarkerIndex >= trackingMarkers.length) {
        trackingMarkerIndex = 0;  // Rollover
    }

    let xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
        // Handle error, in case of successful we don't care
    };
    xhttp.open("POST", track_point_url);
    xhttp.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
    let data = new URLSearchParams();
    data.append('timestamp', position.timestamp.toString());
    data.append('ad_id', ad_id);
    data.append('altitude', position.coords.altitude == null ? "" : position.coords.altitude.toString());
    data.append('altitude_accuracy', position.coords.altitudeAccuracy == null ? "" : position.coords.altitudeAccuracy.toString());
    data.append('accuracy', position.coords.accuracy.toString());
    data.append('latitude', position.coords.latitude.toString());
    data.append('longitude', position.coords.longitude.toString());
    xhttp.send(data);
}

function start_tracking(ad_id) {
    if (!watchId) {
        localStorage.setItem("is_tracking_active", true)
        localStorage.setItem("tracking_ad_id", ad_id);
        watchId = navigator.geolocation.watchPosition(function (position) {
            watcherCallback(position);

        }, null, {timeout: 5000, enableHighAccuracy: true});
    }
    start_tracking_url = `/start-tracking/${ad_id}/`
    document.location.href = start_tracking_url
}

function stop_tracking() {
    stop_tracking_url = `/stop-tracking/`
    localStorage.removeItem("is_tracking_active")
    localStorage.removeItem("tracking_ad_id");
    document.location.href = stop_tracking_url
}

function line_startup() {
    myMap = L.map("map");
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 18,
        // id: 'mapbox.streets',
        // accessToken: 'pk.eyJ1IjoiamFuaS1kamFuZ29jb25ldTIwMTkiLCJhIjoiY2pyNTJ5NGFwMDJhZzQybXRsdWJtMWN6ZyJ9.2QeY2epXN0947hVFhFPqcA'
    }).addTo(myMap);
    myMap.setView([62.6050, 29.756], 13);

    violetIcon = new L.Icon({
        iconUrl: 'https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-violet.png',
        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.4.0/images/marker-shadow.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]
    });

    // Pre-created GeoJSON layer
    jsonLayer = L.geoJSON(null, {
        style: function (feature) {
            console.log(feature);
            return {"color": feature.properties.color}
        }
    }).addTo(myMap);
}

function show_line_on_map(geojson) {
    console.log(geojson)
    jsonLayer.clearLayers();
    jsonLayer.addData(geojson);
    myMap.fitBounds(jsonLayer.getBounds());
}
