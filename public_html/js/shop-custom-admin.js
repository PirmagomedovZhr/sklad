$(function() {
    $('form').each(function(i, el) {
        $(el).submit(function(e) {
            $('[type="submit"]').attr("disabled", true);
            $.blockUI({message: '<h1>Пожалуйста, подождите...</h1>'});
        });
        //$('[type="submit"]').removeAttr("disabled");
    });
});
