$(document).ready(function () {
    $('#form-input').keypress(function (event) {
        var keycode = (event.keyCode ? event.keyCode : event.which);
        if (keycode == '13') {
            $("#reminder").toggle();
        };
    });
});