$(document).ready(function() {

$('#reg_form').on('submit', function(event) {

    $.ajax({
        data : {
            email : $('#email').val(),
            username : $('#username').val(),
            password : $('#password').val(),
            confirm : $('#confirm').val()
            
        },
        type : 'POST',
        url : '/register_process'
    })
    .done(function(data) {

        if (data.error) {
            $('#infodiv').text(data.error);
        }
        else {
            window.location.replace("/confirm_email");
        }
    });

    event.preventDefault();

});


$('#login_form').on('submit', function(event) {

    $.ajax({
        data : {
            username : $('#username').val(),
            password : $('#password').val(),      
        },
        type : 'POST',
        url : '/login_process'
    })
    .done(function(data) {

        if (data.error) {
            $('#infodiv').text(data.error);
        }
        else {
            window.location.replace("/");
        }
    });

    event.preventDefault();

});

});