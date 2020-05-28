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

// Increase shadow of the search field on hover.
$("#form-input")
    .mouseenter(function () {
        $("#form-input").removeClass('shadow-sm');
        $("#form-input").addClass('shadow');
    })
    .mouseout(function () {
        $("#form-input").removeClass('shadow');
        $("#form-input").addClass('shadow-sm');
    });