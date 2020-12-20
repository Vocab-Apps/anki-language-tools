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