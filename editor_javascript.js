function add_inline_fields() {
    $fnames = $("[id^=name]");
    if ($fnames.length > 0) {
        $fnames.each(function (index, fname){
            var $fname = $(fname);
            var i = parseInt($fname.attr("id").substring(4));
            $fname.prepend('<span>yo</span>');
        });
    } else {
        $fnames = $(".fname");
        for (var i=0; i<$fnames.length; i++) {
            var $fname = $($fnames[i]);
            $fname.prepend('<span>yo2</span>');
        }
    }
}

function add_inline_field(field_id) {
    var div_id = 'f' + field_id;
    $field_div = $("#" + div_id);
    $tr_element = $field_div.parent().parent();
    $("<tr><td><span>yo4</span></td></tr>").insertAfter($tr_element);
}