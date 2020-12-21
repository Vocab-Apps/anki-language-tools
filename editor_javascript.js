function add_inline_field(field_type, field_id, header_text) {
    var div_id = 'f' + field_id;
    $field_div = $("#" + div_id);
    $tr_element = $field_div.parent().parent();
    $(`<tr>
        <td width=100%>
            <b>${header_text}</b>: <span id="${field_type}${field_id}">translation loading...</span>
        </td>
      </tr>`).insertAfter($tr_element);
}

function set_inline_field_value(field_type, field_id, value) {
    var decoded_value = decodeURI(value);
    // console.log('decoded_value: ', decoded_value);
    var element_id = field_type + field_id;
    $element = $("#" + element_id);
    $element.html(decoded_value);
}