function checkConfirmation() {
    $.ajax({
        url: "{{ url_for('confirm_login') }}",
        type: "GET",
        data: {nickname: '{{ nickname }}'},
        success: function (response) {
            if (response.redirect) {
                window.location.href = response.redirect;
            }
        }
    });
}

setInterval(checkConfirmation, 1000);

if (window.location.pathname === '/confirm_login') {
    setInterval(function () {
        window.location.reload();
    }, 30000);
}
