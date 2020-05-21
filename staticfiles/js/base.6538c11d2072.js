// $(document).ready(function () {
//     $('#form-input').keypress(function (event) {
//         var keycode = (event.keyCode ? event.keyCode : event.which);
//         if (keycode == '13') {
//             $("#reminder").show();
//         };
//     });
// });


$(document).ready(function () {
    $("#home-form").submit(function () {
        $("#reminder").show();
    });
});