let url = "https://api.minetools.eu/ping/play.linyx.ru";

$.getJSON(url, function (r) {
    if (r.error) {
        $('#rest').html('Server Offline');
        return false;
    }
    let pl = '';
    if (r.players.sample.length > 0) {
        pl = '<br>OP: ' + r.players.sample[0].name;
    }
    $('#rest').html(r.description.replace(/§(.+?)/gi, '') + '<br><b>Игроков онлайн:</b> ' + r.players.online + pl);
    $('#favicon').attr('src', r.favicon);

});