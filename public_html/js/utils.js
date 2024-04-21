function format_price(value, separator) {
    separator = separator || ' ';
    var num2 = value.toString().split('.');
    var thousands = num2[0].split('').reverse().join('').match(/.{1,3}/g).join(separator);
    var decimals = (num2[1]) ? '.'+num2[1] : '';
    return thousands.split('').reverse().join('') + decimals;
}


function choose_plural(amount, variants) {
    /* Возвращает единицу измерения с правильным окончанием в зависимости от переданного количества.
     Варианты окончаний, массив строк в формате: ['1 объект', '2 объекта', '5 объектов'].
     */
    if (amount % 10 == 1 && amount % 100 != 11)
        return variants[0];
    else if (amount % 10 >= 2 && amount % 10 <= 4 && (amount % 100 < 10 || amount % 100 >= 20))
        return variants[1];
    else
        return variants[2];
}


function disable_children(el) {
    el.find('*').attr('disabled', 'disabled');
}

function enable_children(el) {
    el.find('*').removeAttr('disabled');
}
