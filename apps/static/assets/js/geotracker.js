let myMap = null;
let violetIcon = null;
let watchId = null;
let currentLocationMarker = null;
let trackingMarkers = new Array(5);
let trackingMarkerIndex = 0; // current counter

function single_locate() {
    navigator.geolocation.getCurrentPosition(function (position) {
        console.log("Moving to current location", position);
        currentLocationMarker.setLatLng([position.coords.latitude, position.coords.longitude]).addTo(myMap);
        myMap.panTo([position.coords.latitude, position.coords.longitude]);
    },
        function (positionError) {
            alert("Geolocation failure");
            console.debug(positionError.message);
        }, { timeout: 5000, enableHighAccuracy: true });
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
        }, { maximumAge: 5000, timeout: 5000, enableHighAccuracy: true });
}

function start_tracking(username, ad_id) {
    if (watchId) {
        alert("You're already tracking. Stop it or refresh this page");
    } else {
        let tracking_name = username;
        tracking_name.disabled = true;
        watchId = navigator.geolocation.watchPosition(function (position) {
            console.log("Tracked new position", position);
            if (trackingMarkers[trackingMarkerIndex]) {
                // Remove oldest markeer
                myMap.removeLayer(trackingMarkers[trackingMarkerIndex]);

            }
            trackingMarkers[trackingMarkerIndex] = L.marker([position.coords.latitude, position.coords.longitude], { icon: violetIcon });
            trackingMarkers[trackingMarkerIndex].addTo(myMap);
            trackingMarkerIndex++;
            if (trackingMarkerIndex >= trackingMarkers.length) {
                trackingMarkerIndex = 0;  // Rollover
            }

            let xhttp = new XMLHttpRequest();
            xhttp.onreadystatechange = function () {
                // Handle error, in case of successful we don't care
            };
            xhttp.open("POST", tracking_point_url);
            xhttp.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
            let data = new URLSearchParams();
            data.append('username', tracking_name);
            data.append('timestamp', position.timestamp.toString());
            data.append('ad_id', ad_id);
            data.append('altitude', position.coords.altitude == null ? "" : position.coords.altitude.toString());
            data.append('altitude_accuracy', position.coords.altitudeAccuracy == null ? "" : position.coords.altitudeAccuracy.toString());
            data.append('accuracy', position.coords.accuracy.toString());
            data.append('latitude', position.coords.latitude.toString());
            data.append('longitude', position.coords.longitude.toString());
            xhttp.send(data);

        }, null, { timeout: 5000, enableHighAccuracy: true });
        localStorage.setItem("ad_id", ad_id);
    }
}

function stop_tracking(username, ad_id) {
    if (!watchId) {
        alert("You haven't started tracking this ad yet. Start tracking first. ");
    } else {
        if (localStorage.getItem("ad_id") != ad_id.toString()) {
            alert("You have another Ad in progress or haven't started this task yet");
        } else {
            navigator.geolocation.clearWatch(watchId);
            let tracking_name = username;
            tracking_name.disabled = false;
            let xhttp = new XMLHttpRequest();
            xhttp.open("POST", stop_tracking_url);
            xhttp.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
            let data = new URLSearchParams();
            data.append('ad_id', ad_id);
            xhttp.send(data);
        }
    }
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
            return { "color": feature.properties.color }
        }
    }).addTo(myMap);
}

function show_line_on_map(geojson) {
    jsonLayer.clearLayers();
    jsonLayer.addData(geojson);
    myMap.fitBounds(jsonLayer.getBounds());
}
