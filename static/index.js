
function handle_host_status(res) {
    console.log(res);
}

function get_host_status() {
    $.get("/host_status").done(handle_host_status);
}

$(document).ready(function() {
    setInterval(get_host_status, 3000);
});