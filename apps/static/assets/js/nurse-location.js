let last_location_url = "/get-nurse-location/";
let nurse_id = 0;
let track = false;
let last_x = null, last_y = null;

function getLastLocation() {
    console.log("get last location for ", nurse_id, last_location_url)

    if (track) {
        $.post(last_location_url + nurse_id + "/",
            {'nurse_id': nurse_id},
            function(data, status) {
            if(data['success'] && (last_x != data['latitude'] || last_y != data['longitude']))
            {
                last_x = data['latitude'];
                last_y = data['longitude'];
                locate_position(data['latitude'], data['longitude']);
            }
        });
    }
    
    setTimeout(getLastLocation, 2000);
}

getLastLocation();


function setNurseId(id) {
    console.log("set nurse id", id);
    nurse_id = id;
    track = true;
    last_x = null;
    last_y = null;
}

function toggleDetails(id) {
    let item = document.getElementById(`details-${id}`);
    if(item.hasAttribute('hidden')) {
        item.removeAttribute('hidden')
    } else {
        item.setAttribute('hidden', 0)
    }
}

