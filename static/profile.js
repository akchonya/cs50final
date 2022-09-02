$(document).ready(function ($) {
    $(".change_button").each(function(){
        $(this).click(function() {
            var button = $(this).val();
            span_id = "#" + button;
            html = "<form id=" + button + " method='post'><input name='post_button' class='col-md-1 input-sm' type='text'></input>/dunno</form>"
            $(span_id).html(html);
        })
    })
})


