// Increase shadow of the search field on hover.
$("#form-input")
    .mouseenter(function () {
        $("#form-input").addClass('shadow');
    })
    .mouseout(function () {
        $("#form-input").removeClass('shadow');
    });