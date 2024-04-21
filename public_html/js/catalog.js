// Dependencies:
// CONFIG.good_popup_in_cart_html
// CONFIG.good_in_cart_html
// CONFIG.cart_qty_set_url


$(function() {
    // will only fire AFTER everything have loaded
    $(window).load(function() {
        // trigger click if url contains an #anchor
        var hash = window.location.hash;
        if (hash) {
            var $a = $('a[href="' + hash + '"]').first();
            if ($a.length == 1) {  // good is already on page
                $a.click();
            }
            else {
                // good is not on that page, so prepare zero popup trigger
                var $trigger = $('a#good_popup_trigger_0');
                if ($trigger.length == 1) {
                    $trigger.attr('data-url', hash.replace('#',''));  // $trigger.data('url') won't work here
                    $trigger.click(good_popup_trigger_click);
                    $trigger.click();
                }
            }
        }
    });
});


// good popup

function good_popup_trigger_click(e) {
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
                $popup.find('a.add_cart').click(good_popup_add_cart_click);
                $popup.find('input[id^=item_qty_popup_]').change(good_quantity_change);
				$popup.find('.item-qty-inc, .item-qty-dec').click(good_quantity_inc_or_dec_click);
				 
                //
                $('.close-btn', $popup).click(function(e) {
                    e.preventDefault();
                    $popup.trigger('hide');
                });
                //
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
}


// add good to cart from popup

function good_popup_add_cart_click(e) {
    e.preventDefault();

    var $el = $(this);
    var $popup = $el.closest('div.good-popup');
    var good_id = $popup.attr('id').split('_')[2];  // pattern 'good_popup_123'
    var $good = $('#good_'+good_id);

    $.ajax({
        url: $el.attr('href'),
        cache: false,
        context: this,
        success: function(data) {
            $good.find('.quantity input[id^=item_qty_]').val(data['item_qty']);
            $good.find('div.link').html(CONFIG['good_in_cart_html']);
            $popup.find('div.link').html(CONFIG['good_popup_in_cart_html']);
            $popup.find('.quantity input[id^=item_qty_popup_]').val(data['item_qty']);
            update_block_cart(data);
        },
        error: function() {
            alert('Не удалось связаться с сервером. Повторите попытку позже.');
        }
    });
}


// add good to cart

function good_add_cart_click(e) {
    e.preventDefault();

    var $el = $(this);
    var $good = $el.closest('div.good2');
    var good_id = $good.attr('id').split('_')[1];  // pattern 'good_123'
    var $popup = $('#good_popup_'+good_id);

    $.ajax({
        url: $el.attr('href'),
        cache: false,
        context: this,
        success: function(data) {
            $good.find('input[id^=item_qty_]').val(data['item_qty']);
            $good.find('div.link').html(CONFIG['good_in_cart_html']);
            $popup.find('div.link').html(CONFIG['good_popup_in_cart_html']);
            update_block_cart(data);
        },
        error: function() {
            alert('Не удалось связаться с сервером. Повторите попытку позже.');
        }
    });
}


// inc/dec good quantity

function good_quantity_inc_or_dec_click(e) {
    e.preventDefault();

    if ($(this).attr('disabled'))
        return false;

    var $el = $(this);
	if ($(this).attr('id').indexOf('popup_') > 0) {
		var $good = $el.closest('div.good-popup').prev('div.good2');
	} else {
		var $good = $el.closest('div.good2');
	}
    var good_id = $good.attr('id').split('_')[1];  // pattern 'good_123'
    var $quantity = $good.find('div.quantity');
    var $popup = $('#good_popup_'+good_id);

    $.ajax({
        url: $el.attr('href'),
        cache: false,
        context: this,
        beforeSend: function() {
            disable_children($quantity);
        },
        success: function(data) {
            $good.find('#item_qty_'+good_id).val(data['item_qty']);
            $popup.find('#item_qty_popup_'+good_id).val(data['item_qty']);
            $good.find('div.link').html(CONFIG['good_in_cart_html']);
            $popup.find('div.link').html(CONFIG['good_popup_in_cart_html']);
            update_block_cart(data);
        },
        complete: function() {
            enable_children($quantity);
        },
        error: function() {
            alert('Не удалось связаться с сервером. Повторите попытку позже.');
        }
    });
}


// change good quantity

function good_quantity_change(e) {
    e.preventDefault();

    if ($(this).attr('disabled'))
        return false;

    var $el = $(this);
	if ($(this).attr('id').indexOf('popup_') > 0) {
		var $good = $el.closest('div.good-popup').prev('div.good2');
	} else {
		var $good = $el.closest('div.good2');
	}
    var good_id = $good.attr('id').split('_')[1];  // pattern 'good_123'
    var $quantity = $good.find('div.quantity');
    var $popup = $('#good_popup_'+good_id);

    var qty = parseInt($el.val());

    if (qty && qty > 0) {
        $.ajax({
            url: CONFIG['cart_qty_set_url'] + good_id + '/' + qty + '/',
            cache: false,
            context: this,
            beforeSend: function() {
                disable_children($quantity);
            },
            success: function(data) {
                $el.val(data['item_qty']);
				$good.find('#item_qty_'+good_id).val(data['item_qty']);
				$popup.find('#item_qty_popup_'+good_id).val(data['item_qty']);
                $good.find('div.link').html(CONFIG['good_in_cart_html']);
                $popup.find('div.link').html(CONFIG['good_popup_in_cart_html']);
                update_block_cart(data);
            },
            complete: function() {
                enable_children($quantity);
            },
            error: function() {
                alert('Не удалось связаться с сервером. Повторите попытку позже.');
            }
        });
    }
    else
        alert('Введите корректное количество.');
}


function init_loaded_goods() {
    var $goods = $('div.good2');

    $goods.find('a.add_cart').not('.inited').each(function() {
        var $el = $(this);
        $el.click(good_add_cart_click);
        $el.addClass('inited');
    });

    $goods.find('.item-qty-inc, .item-qty-dec').not('.inited').each(function() {
        var $el = $(this);
        $el.click(good_quantity_inc_or_dec_click);
        $el.addClass('inited');
    });

    $goods.find('input[id^=item_qty_]').not('.inited').each(function() {
        var $el = $(this);
        $el.change(good_quantity_change);
        $el.addClass('inited');
    });

    $goods.find('a.good-popup-trigger').not('.inited').each(function() {
        var $el = $(this);
        $el.click(good_popup_trigger_click);
        $el.addClass('inited');
    });
}


$(function() {
    init_loaded_goods();

    // pagination
    $.endlessPaginate({
        paginateOnScroll: true,
        paginateOnScrollMargin: 150,
        onCompleted: function(context, fragment) {
            init_loaded_goods();
        }
    });
});
