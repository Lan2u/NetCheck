
// A dictionary of current statuses.
var current_status = {};

function create_status_obj(name, addr, avg_rtt, last_loss, elm) {
    var so = new Object();
    so.name = name;
    so.addr = addr;
    so.avg_rtt = avg_rtt;
    so.loss = last_loss;
    so.elm = elm;

    return so;
}

function gen_status_str(status) {
    return "Name: " + status.name + " Addr: " + status.addr + " Avg_RTT: " + status.avg_rtt + " Loss: " + status.loss;
}

function create_status_row(id, status) {
    $("#main_status_table").append(
        "<tr class=\"status_row\" id=\"" + id + "\"><td>waiting...</td></tr>"
    );
}

function update_status_row(elm, status) {
    var jelm = $(elm);
    jelm.text(gen_status_str(status));

    if (status.loss > 0){
        jelm.removeClass("ok_status")
        jelm.addClass("lossy_status")
    } else {
        jelm.removeClass("lossy_status")
        jelm.addClass("ok_status")
    }
}

function update_status_display(statuses) {
    for (var key in statuses){
        var id = statuses[key].name.replace(" " , "");

        x = document.getElementById(id);

        if (x == null) {
            create_status_row(id, statuses[key]);
            x = document.getElementById(id);
        }

        update_status_row(x, statuses[key]);
    }
}

function handle_host_status(res) {
    for (var key in res) {

        var so = create_status_obj(res[key].name,
             res[key].addr, 
             res[key].avg_rtt, 
             res[key].last_loss);

        current_status[so.name] = so;
    }

    update_status_display(current_status);
}

function get_host_status() {
    $.get("/host_status").done(handle_host_status);
}

$(document).ready(function() {
    setInterval(get_host_status, 3000);
});