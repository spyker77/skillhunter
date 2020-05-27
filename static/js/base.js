// Hide reminder by default.
$('#reminder').css({
    display: 'none'
});

// Show reminder on submit.
$(document).ready(function () {
    $("#home-form").submit(function () {
        $("#reminder").show();
    });
});