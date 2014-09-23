var attemptConnect;
attemptConnect = attemptConnect || (function () {
    var modalAttemptConnect = $('<div class="modal" data-backdrop="static" data-keyboard="false"><div class="modal-dialog"><div class="modal-content"><div class="modal-header"><h3 class="text-center">Attempting to Connect</h3></div><div class="modal-body"><div class="text-center"><i class="fa fa-spinner fa-5x fa-spin"></i></div></div></div></div></div>');
    return {
        show: function() {
            modalAttemptConnect.modal('show');
        },
        hide: function () {
            modalAttemptConnect.modal('hide');
        }
    };
})();

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

    $('[name="test_connection"]').click(function(){
        attemptConnect.show()
    });
});
