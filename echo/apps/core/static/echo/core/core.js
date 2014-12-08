var attemptConnect;
attemptConnect = attemptConnect || (function () {
    var modalAttemptConnect = $('<div class="modal" data-backdrop="static" data-keyboard="false"><div class="modal-dialog"><div class="modal-content"><div class="modal-header"><h3 class="text-center">Connecting...</h3></div><div class="modal-body"><div class="text-center"><i class="fa fa-spinner fa-5x fa-spin"></i></div></div></div></div></div>');
    return {
        show: function () {
            modalAttemptConnect.modal('show');
        },
        hide: function () {
            modalAttemptConnect.modal('hide');
        }
    };
})();

var playerInfo = undefined;
var playerTime = undefined;
var playerState = "STOPPED";
var soundLength = 0;
var soundPosition = 0;
var last = undefined;
var timer = undefined;
var listened = false;

function getPlayer(pid) {
    var obj = document.getElementById(pid);
    if (obj.doPlay) return obj;
    for (i = 0; i < obj.childNodes.length; i++) {
        var child = obj.childNodes[i];
        if (child.tagName == "EMBED") return child;
    }
}

function buttonPlayPauseHandler(fname) {
    var player = getPlayer('player');
    if (playerState == 'PLAYING') {
        player.doPause();
    } else if (playerState == 'PAUSED') {
        player.doResume();
    } else {
        player.doPlay(fname);
    }
}

function buttonStopHandler() {
    var player = getPlayer('player');
    player.doStop();
}

function setVolume(v) {
    var player = getPlayer('player');
    player.setVolume(v);
}

function getPercent(a, b) {
    return ((b == 0 ? 0.0 : a / b) * 100).toFixed(2);
}

function soundLoad(secLoad, secTotal) {
    soundLength = secTotal;
}

function inform() {
    if (last != undefined) {
        var now = new Date();
        t = now.getTime() - last.getTime();
        soundPosition += t / 1000;
        if (soundPosition > soundLength) {
            listened = true;
            document.getElementById('finish_listen').value = 'heard';
        }
        last = now;
    }
    playerInfo.innerHTML = playerState;
    playerTime.innerHTML = soundPosition.toFixed(0) + '/' + soundLength.toFixed(0) + ' SEC';
}

function playerController(state, position) {
    if (position != undefined) soundPosition = position;
    if (state == "BUFFERING") {
        // empty
    } else if (state == 'STOPPED') {
        $('#button_play').children().first().removeClass('fa-pause').addClass('fa-play');
        clearInterval(timer);
        last = undefined;
        timer = undefined;
    } else if (state == "PAUSED") {
        $('#button_play').children().first().removeClass('fa-pause').addClass('fa-play');
        clearInterval(timer);
        timer = undefined
    } else if (state == "PLAYING") {
        $('#button_play').children().first().removeClass('fa-play').addClass('fa-pause');
        last = new Date();
        timer = setInterval(inform, 10);
    }
    playerState = state;
    inform();
}

function init() {
    var player = getPlayer('player');
    if (!player || !player.attachHandler) {
        setTimeout(init, 100); // Wait for load
    } else {
        player.attachHandler("PLAYER_LOAD", "soundLoad");
        player.attachHandler("PLAYER_BUFFERING", "playerController", "BUFFERING");
        player.attachHandler("PLAYER_PLAYING", "playerController", "PLAYING");
        player.attachHandler("PLAYER_STOPPED", "playerController", "STOPPED");
        player.attachHandler("PLAYER_PAUSED", "playerController", "PAUSED");
        playerInfo = document.getElementById('player_info');
        playerTime = document.getElementById('player_time');
        inform();
    }
}

$(document).on('change', '.btn-file :file', function () {
    var input = $(this);
    var numFiles = input.get(0).files ? input.get(0).files.length : 1;
    var label = input.val().replace(/\\/g, '/').replace(/.*\//, '');
    input.trigger('fileselect', [numFiles, label]);
});

$(document).ready(function () {
    $('.btn-file :file').on('fileselect', function (event, numFiles, label) {
        var input = $(this).parents('.input-group').find(':text');
        input.val(numFiles > 1 ? numFiles + ' files selected' : label);
    });

    $('[name="test_connection"]').click(function () {
        attemptConnect.show();
    });

    $('[name="update_files"]').click(function () {
        attemptConnect.show();
    });
});
