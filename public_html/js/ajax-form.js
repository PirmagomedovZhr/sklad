$(function () {
    $('form.ajax-form').each(function() {
        var form = $(this);
        var form_id = form.attr('id');

        var dlg_msg = $('#dialog-message');
        dlg_msg.dialog({
            modal: true,
            autoOpen: false,
            resizable: false,
            width: 310,
            buttons: {
                Ok: function() {
                    $(this).dialog('close');
                }
            }
        });

        var before_ajax_success_callback = window[form_id + '_before_ajax_success'] || null;
        var after_ajax_success_callback = window[form_id + '_after_ajax_success'] || null;

        var options = {
            dataType: 'json',
            timeout: 30000,
            cache: false,
            beforeSubmit: function() {
                $('input', form).attr('disabled', 'disabled');
                $('button', form).attr('disabled', 'disabled');
                form.removeData('ajax_data'); // remove previously fetched data from form object
            },
            complete: function(data) {
                $('input', form).removeAttr('disabled');
                $('button', form).removeAttr('disabled');
            },
            /*beforeSend: function() {
                $('.form-errors', form).html('').hide();
            },*/
            success: function(data) {
                if (before_ajax_success_callback)
                    before_ajax_success_callback(form, data);

                clear_form_errors(form);
                $('.message', form).html('');
                form.data('ajax_data', data); // save fetched data on form object
                if (data.success) {
                    if (form.hasClass('dialog-form')) {
                        form.dialog('close');
                        if (data.message) {
                            dlg_msg.html(data.message);
                            var options = {
                                title: data.message_title || 'Сообщение',
                                close: function() {
                                    if (data.redirect)
                                        window.location.href = data.redirect;
                                }
                            };
                            dlg_msg.dialog(options).dialog('open');
                        }
                    }
                    else {
                        if (data.message)
                            $('.message', form).html(data.message);
                        if (data.redirect)
                            window.location.href = data.redirect;
                    }
                }
                else {
                    process_form_errors(form, data);
                    process_fields_errors(form, data);
                    reload_captcha(form, data);
                }

                if (after_ajax_success_callback)
                    after_ajax_success_callback(form, data);
            }
        };
        form.ajaxForm(options);
    });
});

function clear_form_errors(form) {
    $('.form-errors', form).html('').hide();
    $('.field > .errors', form).html('').hide();
    form.find(':input').each(function() {
        $(this).removeClass('ui-state-error'); // remove fields highlight
    });
}

function process_form_errors(form, data) {
    if (data.form_errors) {
        var html = '<ul>';
        for (var err in data.form_errors) {
            if (data.form_errors.hasOwnProperty(err))
                html += '<li>' + data.form_errors[err] + '</li>';
        }
        html += '</ul>';
        $('.form-errors', form).html(html).show();
    }
}

function process_fields_errors(form, data) {
    for (var key in data.field_errors) {
        if (data.field_errors.hasOwnProperty(key)) {
            var input = $('[name^='+key+'],[field^='+key+']', form);
            input.addClass('ui-state-error'); // highlight field
            var field = $('.field#' + key, form);
            var value = data.field_errors[key];
            $('.errors', field).html(value[0]).show();
        }
    }
}

function reload_captcha(form, data) {
    var img = $("img[src!=/captcha/]", form)[0];
    if (img) {
        img.src = img.src + '#';
    }
}
