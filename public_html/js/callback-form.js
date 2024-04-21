$(function() {
    var block = $('#block-callback');
    var form = $('form', block);

    $('.tel').click(function() {
        $('.message', form).hide();
        form.clearForm();
        $('div#phone', form).show();
        $('input[type=submit]', form).show();
        block.css('display', 'block');
    });

    $('.close_callback').click(function() {
        $(this).parent().parent().css('display', 'none');
        form.removeData('ajax_data'); // remove previously fetched data from form object
    });
});

function callback_form_before_ajax_success(form, data) {
    if (data.success) {
        $('div#phone', form).hide();
        $('input[type=submit]', form).hide();
        $('.message', form).show();
    }
}

function callback_form_after_ajax_success(form, data) {
    // auto close form
    if (data.success) {
        setTimeout(function() {
            if (form.data('ajax_data') && form.data('ajax_data').success)
                form.parent().fadeOut('slow');
        }, 5000);
    }
}
