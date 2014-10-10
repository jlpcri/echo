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

function updateProgress(a, b) {
//    console.log(parseInt(getPerc(a, b)) + "%")
    $("#player-progress").css("width", parseInt(getPerc(a, b)) + "%");
//    $("#player-progress").css("width", '50%');
}

function getPlayer(pid) {
    var obj = document.getElementById(pid);
    if (obj.doPlay) return obj;
    for (i = 0; i < obj.childNodes.length; i++) {
        var child = obj.childNodes[i];
        if (child.tagName == "EMBED") return child;
    }
}
function doPlay(fname) {
    var player = getPlayer('audio1');
    player.doPlay(fname);
}
function doStop() {
    var player = getPlayer('audio1');
    player.doStop();
}
function setVolume(v) {
    var player = getPlayer('audio1');
    player.setVolume(v);
}
function setPan(p) {
    var player = getPlayer('audio1');
    player.setPan(p);
}
var SoundLen = 0;
var SoundPos = 0;
var Last = undefined;
var State = "STOPPED";
var Timer = undefined;
function getPerc(a, b) {
    return ((b == 0 ? 0.0 : a / b) * 100).toFixed(2);
}
function FileLoad(bytesLoad, bytesTotal) {
    document.getElementById('InfoFile').innerHTML = "Loaded " + bytesLoad + "/" + bytesTotal + " bytes (" + getPerc(bytesLoad, bytesTotal) + "%)";
//    console.log(getPerc(bytesLoad, bytesTotal));
//    updateProgress(bytesLoad, bytesTotal);
}
function SoundLoad(secLoad, secTotal) {
    document.getElementById('InfoSound').innerHTML = "Available " + secLoad.toFixed(2) + "/" + secTotal.toFixed(2) + " seconds (" + getPerc(secLoad, secTotal) + "%)";
//    updateProgress(secLoad, secTotal);
    SoundLen = secTotal;
}
var InfoState = undefined;
function Inform() {
    if (Last != undefined) {
        var now = new Date();
        var interval = (now.getTime() - Last.getTime()) / 1000;
        SoundPos += interval;
        console.log(SoundPos);
        Last = now;
        console.log(Last);
    }
    InfoState.innerHTML = State + "(" + SoundPos.toFixed(2) + "/" + SoundLen.toFixed(2) + ") sec (" + getPerc(SoundPos, SoundLen) + "%)";
    updateProgress(SoundPos, SoundLen);
}
function SoundState(state, position) {
    console.log(state);
    if (position != undefined) SoundPos = position;
    if (State != "PLAYING" && state == "PLAYING") {
        Last = new Date();
        Timer = setInterval(Inform, 178);
//        Inform();
    } else if (State == "PLAYING" && state != "PLAYING") {
        clearInterval(Timer);
        Timer = undefined;
//        Inform();
    }
    State = state;
    Inform();
}
function init() {
    var player = getPlayer('audio1');
    if (!player || !player.attachHandler) setTimeout(init, 100); // Wait for load
    else {
        player.attachHandler("progress", "FileLoad");
        player.attachHandler("PLAYER_LOAD", "SoundLoad");
        player.attachHandler("PLAYER_BUFFERING", "SoundState", "BUFFERING");
        player.attachHandler("PLAYER_PLAYING", "SoundState", "PLAYING");
        player.attachHandler("PLAYER_STOPPED", "SoundState", "STOPPED");
        player.attachHandler("PLAYER_PAUSED", "SoundState", "PAUSED");
        InfoState = document.getElementById('InfoState')
        Inform();
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
        attemptConnect.show()
    });

    $('[name="update_files"]').click(function () {
        attemptConnect.show()
    });
});
