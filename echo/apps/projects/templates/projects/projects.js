
function deleteSlotConfirm(slot_id, slot_name) {
    $('#voice_slot_id').val(slot_id);
    $('#voice_slot_name').html(slot_name);
    $('#modal_delete_slot').modal('show');
}

$('#modal_delete_slot_form').submit(function(event) {
    event.preventDefault();
    var slot_id = $('#voice_slot_id').val();
    var url = "{% url 'projects:delete_slot' '10000' %}";
    url = url.replace('10000', slot_id);
    var posting = $.post(url);
    posting.done(function(data){
        var data_obj = eval("(" + data + ")");
        if (data_obj.success === true) {
            location.reload(true);
        } else {
            $('#modal_delete_slot_error').html(data_obj.error);
        }
    })
});


function rollbackVuidConfirm(vuid_id, vuid_name) {
    $('#vuid_script_id').val(vuid_id);
    $('#vuid_script_name').html(vuid_name);
    $('#modal_rollback_vuid').modal('show');
}

$('#modal_rollback_vuid_form').submit(function(event) {
    event.preventDefault();
    var vuid_id = $('#vuid_script_id').val();
    var url = "{% url 'projects:rollback_vuid' '10000' %}";
    url = url.replace('10000', vuid_id);
    var posting = $.post(url);
    posting.done(function(data){
        var data_obj = eval("(" + data + ")");
        if (data_obj.success === true) {
            location.reload(true);
        } else {
            $('#modal_rollback_vuid_error').html(data_obj.error);
        }
    })
});