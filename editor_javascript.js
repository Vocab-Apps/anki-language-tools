
function add_loading_indicator(field_id) {
    var div_id = 'name' + field_id;
    $field_name_tr = $("#" + div_id).parent();
    $(`<tr><td><span><i>loading...</i></span></td></tr>`).insertAfter($field_name_tr);
}


function add_inline_field(field_type, field_id, header_text) {
    var div_id = 'f' + field_id;
    $field_div = $("#" + div_id);
    $tr_element = $field_div.parent().parent();
    var row_id = 'row_'+field_type+field_id;
    $(`<tr id="${row_id}"  >
        <td width=100% style='padding-bottom: 10px;'>
            <i>${header_text}</i>: <span id="${field_type}${field_id}">translation loading...</span>
        </td>
      </tr>`).insertAfter($tr_element);
}

function remove_inline_field(field_type, field_id) {
    var row_id = 'row_'+field_type+field_id;
    $("#"+row_id).remove();
}

function set_inline_field_value(field_type, field_id, value) {
    var decoded_value = decodeURI(value);
    // console.log('decoded_value: ', decoded_value);
    var element_id = field_type + field_id;
    $element = $("#" + element_id);
    $element.html(decoded_value);
}

function set_field_value(field_id, value) {
    var decoded_value = decodeURI(value);
    // console.log('decoded_value: ', decoded_value);
    var element_id = 'f' + field_id;
    $element = $("#" + element_id);
    $element.html(decoded_value);
}