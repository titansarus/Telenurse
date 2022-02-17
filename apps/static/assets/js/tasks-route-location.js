function toggleDetails(id) {
    let item = document.getElementById(`details-${id}`);
    if(item.hasAttribute('hidden')) {
        item.removeAttribute('hidden')
    } else {
        item.setAttribute('hidden', 0)
    }
}
