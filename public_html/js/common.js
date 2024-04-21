// Dependencies:
// CONFIG.user_logged
// CONFIG.cart_url
// CONFIG.cart_orders_url


function update_block_cart(cart) {
    function _update(cart) {
        var $block_cart = $('div.block-cart');
        var $block_cart_goods = $('#block_cart_goods', $block_cart);

        if ($block_cart_goods.length > 0) {
            if (cart.hasOwnProperty('items_count')) {
                if (cart['items_count'] > 0) {
                    // show cart link if user isn't logged in
                    if (!CONFIG['user_logged'])
                        $('span#my_cart_link', $block_cart)
                            .replaceWith('<a id="my_cart_link" href="' + CONFIG['cart_url'] + '">Моя корзина</a>');

                    $block_cart_goods.html(
                        '<a href="' + CONFIG['cart_url'] + '">' + cart['items_count'] + ' ' +
                            choose_plural(cart['items_count'], ['товар', 'товара', 'товаров']) + '</a> на ' +
                        format_price(cart['price']) + ' руб.'
                    );
                }
                else {
                    // hide cart link if user isn't logged in
                    if (!CONFIG['user_logged'])
                        $('a#my_cart_link', $block_cart)
                            .replaceWith('<span id="my_cart_link" href="' + CONFIG['cart_url'] + '">Моя корзина</a>');

                    $block_cart_goods.text('В корзине ничего нет');
                }
            }
            // do nothing if no attr `items_count`
        }

        var $block_cart_orders = $('#block_cart_orders', $block_cart);
        if ($block_cart_orders.length > 0) {
            if (cart.hasOwnProperty('unpaid_orders_count')) {
                if (cart['unpaid_orders_count'] > 0)
                    $block_cart_orders.html(
                        '<a href="' + CONFIG['cart_orders_url'] + '">' + cart['unpaid_orders_count'] + ' ' +
                            choose_plural(cart['unpaid_orders_count'],
                                ['неоплаченный заказ', 'неоплаченных заказа', 'неоплаченных заказов']) +
                        '</a>'
                    ).show();
                else
                    $block_cart_orders.hide();
            }
            // do nothing if no attr `unpaid_orders_count`
        }
    }

    if (cart)
        _update(cart);
    else
        $.ajax({
            url: CONFIG['cart_url'],
            cache: false,
            success: function(data) {
                _update(data);
            }
        });
}


// catalog popup

$(function() {
    var $popup_trigger = $('.category-popup-trigger');
    var $popup = $('.category-popup');

    if (!$popup_trigger.length || !$popup.length)
        return;

    var popup_trigger_top = $popup_trigger.offset().top;
    var popup_trigger_left = $popup_trigger.offset().left;
    var popup_trigger_right = $popup_trigger.offset().left + $popup_trigger.outerWidth();

    $popup.css('top', popup_trigger_top + $popup_trigger.outerHeight());

    $popup_trigger.mouseenter(function() {
        $popup.show();
    });

    $popup_trigger.mouseleave(function(e) {
        var mouse_x = e.pageX;
        var mouse_y = e.pageY;
        if (mouse_y < popup_trigger_top || mouse_x <= popup_trigger_left || mouse_x >= popup_trigger_right)
            $popup.hide();
    });

    $popup.mouseleave(function() {
        $popup.hide();
    });
});
