"use strict";

// These methods make the forms for creating
// and updating tasks more dynamic.



function addDynamicTimeForm() {

    var is_timed = document.getElementById("id_is_timed");
    var total_time = document.getElementById("id_total_time");
    toggleTotalTime(is_timed, total_time);

    // total_time.parentNode.style.display = "none";

    is_timed.addEventListener('change', function() {
                                toggleTotalTime(is_timed, total_time)
    });


}
function toggleTotalTime(is_timed, total_time) {
    if (is_timed.checked) {
        total_time.parentNode.style.display = "inherit";

    }
    else if (!is_timed.checked) {
        total_time.parentNode.style.display = "none";
    }
}



$( addDynamicTimeForm );
