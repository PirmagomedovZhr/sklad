// Dependencies:
// CONFIG.cart_get_deliveries_url
// CONFIG.cart_qty_set_url


$(function() {
    $(".toggle-form input").live("focus", function(e) {
        $(".toggle-form").removeClass("active_form").addClass("not_active_form");
        $(this).closest(".toggle-form").removeClass("not_active_form");
        $(this).closest(".toggle-form").addClass("active_form");
    });
});


// remove good from cart
$(function() {
    $('.good_del').click(function() {
        $.ajax({
            url: $(this).attr('href'),
            cache: false,
            context: this,
            success: function(data) {
                if (data.items_count < 1) {
                    $('div#cart').children().remove();
                    $('div#cart').append('<h2 class="align-center">Ваша корзина пуста</h2>');
                }
                else {
                    $(this).closest('div.cart-good[id^=item_]').remove();
                    //
                    $('#total_price .pprice').text(format_price(data['total_price']) + ' p.');
                    $('#total_discount .pprice').text('- ' + format_price(data['total_discount']) + ' p.');
                    $('#total_discount .ppercent').text(data['total_discount_percent']);
                }
                update_block_cart(data);
            }
        });
        return false;
    });
});


// handle change and increment/decrement cart item quantity
$(function() {
    var cart_goods = $('#cart .cart-good');

    function disable_item_controls(el_item) {
        el_item.find('*').attr('disabled', 'disabled');
    }

    function enable_item_controls(el_item) {
        el_item.find('*').removeAttr('disabled');
    }

	function good_quantity_inc_or_dec(e) {
        if ($(this).attr('disabled'))
            return false;

		if ($(this).attr('id').indexOf('popup_') > 0) {
			var item_id = $(this).attr('id').split('_')[4]; // pattern 'item_qty_inc_123' or 'item_qty_dec_123'
			var popup_item = $(this).closest('div.good-popup');
			var el_item = $(this).closest('div.good-popup').prev('div.cart-good[id^=item_]');
		} else {
			var item_id = $(this).attr('id').split('_')[3]; // pattern 'item_qty_inc_123' or 'item_qty_dec_123'
			var el_item = $(this).closest('div.cart-good[id^=item_]');
			var popup_item = $(this).closest('div.cart-good[id^=item_]').next('div.good-popup');
		}

        $.ajax({
            url: $(this).attr('href'),
            cache: false,
            beforeSend: function() { disable_item_controls(el_item) },
            success: function(data) {
                popup_item.find('#item_qty_popup_'+item_id).val(data['item_qty']);
                el_item.find('#item_qty_'+item_id).val(data['item_qty']);
                el_item.find('.total-price .pprice').text(format_price(data['item_total_price']) + ' p.');
                //
                $('#total_price .pprice').text(format_price(data['total_price']) + ' p.');
                $('#total_discount .pprice').text('- ' + format_price(data['total_discount']) + ' p.');
                $('#total_discount .ppercent').text(data['total_discount_percent']);
            },
            complete: function() { enable_item_controls(el_item) },
            error: function() { alert('Не удалось связаться с сервером. Повторите попытку позже.'); }
        });

        return false;
    }
    cart_goods.find('.item-qty-inc, .item-qty-dec').click(good_quantity_inc_or_dec);

	function change_qty(e) {
        if ($(this).attr('disabled'))
            return false;

		if ($(this).attr('id').indexOf('popup_') > 0) {
			var item_id = $(this).attr('id').split('_')[3]; // pattern 'item_qty_inc_123' or 'item_qty_dec_123'
			var popup_item = $(this).closest('div.good-popup');
			var el_item = $(this).closest('div.good-popup').prev('div.cart-good[id^=item_]');
		} else {
			var item_id = $(this).attr('id').split('_')[2]; // pattern 'item_qty_inc_123' or 'item_qty_dec_123'
			var el_item = $(this).closest('div.cart-good[id^=item_]');
			var popup_item = $(this).closest('div.cart-good[id^=item_]').next('div.good-popup');
		}

        var qty = parseInt($(this).val());
        if (qty && qty > 0) {
            $.ajax({
                url: CONFIG['cart_qty_set_url'] + item_id + '/' + qty + '/',
                cache: false,
                beforeSend: function() { disable_item_controls(el_item) },
                success: function(data) {
					popup_item.find('#item_qty_popup_'+item_id).val(data['item_qty']);
					el_item.find('#item_qty_'+item_id).val(data['item_qty']);
                    el_item.find('.total-price .pprice').text(format_price(data['item_total_price']) + ' p.');

                    $('#total_price .pprice').text(format_price(data['total_price']) + ' p.');
                    $('#total_discount .pprice').text('- ' + format_price(data['total_discount']) + ' p.');
                    $('#total_discount .ppercent').text(data['total_discount_percent']);
                },
                complete: function() { enable_item_controls(el_item) },
                error: function() { alert('Не удалось связаться с сервером. Повторите попытку позже.'); }
            });
        }
        else
            alert('Введите корректное количество.');
			popup_item.find('#item_qty_popup_'+item_id).val(el_item.find('#item_qty_'+item_id).val());

        return false;
    }

    cart_goods.find('[id^=item_qty_]').change(change_qty);

    $('div#cart').find('a.good-popup-trigger').click(function(e) {
        e.preventDefault();

        var $trigger = $(this);
        var $popup = $('#good_popup_' + $trigger.data('name'));

        if (!$popup.hasClass('content-ready')) {
            $.ajax({
                url: $trigger.data('url'),
                type: 'GET',
                cache: false,
                dataType: 'html',
                context: this,
                success: function(html) {
                    $popup.html($popup.html() + html);
                    $popup.addClass('content-ready');
                    //
                    $popup.find('.close-btn').click(function(e) {
                        e.preventDefault();
                        $popup.trigger('hide');
                    });
                    //
                    $popup.find('.in_cart > a').click(function(e) {
                        e.preventDefault();
                        $popup.trigger('hide');
                    });
                    //
					$popup.find('.item-qty-inc, .item-qty-dec').click(good_quantity_inc_or_dec);
					$popup.find('input[id^=item_qty_popup_]').change(change_qty);
                    $popup.omniWindow();
                    $popup.trigger('show');
                },
                error: function() {
                    alert('Не удалось связаться с сервером. Повторите попытку позже.');
                }
            });
        }
        else {
            $popup.trigger('show');
        }
    });
});


// cart tabs
$(function () {
    var tabs = $('div.tabs > div');

    tabs.hide().filter(':first').show();

    $('div.tabs ul.tab-nav a').click(function () {
        tabs.hide();
        tabs.filter(this.hash).show();
        $('div.tabs ul.tab-nav a').removeClass('selected');
        $(this).addClass('selected');
        return false;
    });

    if (window.location.hash)
        $('div.tabs ul.tab-nav a[href=' + window.location.hash + ']').click();
    else
        $('div.tabs ul.tab-nav a').filter(':first').click();
});


// handle order cancel
$(function () {
    var form = $('#order_cancel_form');

    form.dialog({
        modal: true,
        autoOpen: false,
        width: 400
    });

    $('input[name=_cancel]', form).click(function() {
        form.dialog('close');
        return false;
    });

    $('a.order-cancel').click(function() {
        var link = $(this);
        var order_id = link.attr('id').split('_')[2]; // pattern 'order_cancel_123'
        form.attr('action', link.attr('href'));
        form.removeData('ajax_data');
        var options = {
            title: link.attr('title'),
            close: function() {
                if (form.data('ajax_data') && form.data('ajax_data').success) {
                    $('#order_'+order_id).remove();
                    update_block_cart(form.data('ajax_data').cart || null);
                }
            }
        };
        form.dialog(options).dialog('open');
        return false;
    });
});


// handle order noreg
$(function () {
    var form = $('#order_noreg_form');

    form.dialog({
        modal: true,
        autoOpen: false,
        width: 414
    });

    $('a#order_noreg').click(function() {
        form.dialog('open');
        return false;
    });
});
