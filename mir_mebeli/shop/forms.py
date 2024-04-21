# -*- coding: utf-8 -*-
from django import forms
from django.forms.util import ErrorList
from django.contrib.auth import authenticate
from django.conf import settings

from captcha.fields import ReCaptchaField
from tinymce.widgets import TinyMCE

from .models import Buyer, Category, Good, Order, OrderedItem, City
from .fields import TreeNodeChoiceField


PASSWORD_MIN_LEN = getattr(settings, 'PASSWORD_MIN_LEN ', 7)


def set_field_error(form, field, msg=u'Обязательное поле.'):
    """Добавить сообщение об ошибке поля и убрать это поле из списка успешно прошедших валидацию.
    Полезно, если нужно инвалидировать поле из метода clean() и добавить ему ошибку.
    В этом случае исключение forms.ValidationError() не подходит, т.к. оно добавит сообщение об ошибке в ошибки формы.
    """
    form._errors[field] = form.error_class([msg])
    if field in form.cleaned_data:
        del form.cleaned_data[field]


class DivErrorList(ErrorList):
    def __unicode__(self):
        return self.as_divs()
    def as_divs(self):
        if not self: return u''
        return u'<div class="errorlist">%s</div>' % ''.join([u"""<div class="ui-widget">
            <div class="ui-state-error ui-corner-all" style="padding: 0 .7em;">
                    <p><span class="ui-icon ui-icon-alert" style="float: left; margin-right: .3em;"></span> %s</p>
                </div>
            </div>""" % e for e in self])


class MessageForm(forms.Form):
    fio = forms.CharField(label=u"Имя", widget=forms.TextInput(attrs={'maxlength':'100'}))
    email = forms.CharField(label=u"E-mail", widget=forms.TextInput(attrs={'maxlength':'30'}))
    text = forms.CharField(label=u"Текст сообщения", widget=forms.Textarea())
    phone = forms.CharField(required=False, label=u'',
                            widget=forms.TextInput(attrs={'placeholder': u'Ваш телефон )'}))
    captcha = ReCaptchaField(label=u'', attrs={
        'theme': 'white',
        'lang': 'ru',
    })


class ReqPriceForm(forms.Form):
    """Форма запроса срока доставки товара."""
    phone = forms.CharField(label=u'Номер телефона', max_length=20,
        error_messages={'required': u'Укажите номер телефона.',})

    email = forms.EmailField(label=u'Электронная почта', max_length=75,
        error_messages={'invalid': u'Неверный формат почтового адреса.',})

    subscribe = forms.BooleanField(label=u'Присылать мне предложения', initial=True, required=False)

    def clean(self):
        if not self.cleaned_data.get('phone') or not self.cleaned_data.get('email'):
            raise forms.ValidationError(u'Введите контактную информацию')
        return self.cleaned_data


class ReqPhoneCallForm(forms.Form):
    """Форма запроса обратного звонка."""
    phone = forms.CharField(label=u'Номер телефона', max_length=20,
        error_messages={'required': u'Укажите номер телефона.',})


class SearchForm(forms.Form):
    """Поисковая форма."""
    q = forms.CharField(label=u"Поиск:")
    cat = forms.ModelChoiceField(label=u'Рубрика', empty_label=u'По всему каталогу', required=False,
        #queryset=Category.objects.filter(basic=True, count_all__gt=0, hidden=False).order_by('order', 'name'),
        queryset=Category.objects.filter(basic=True, hidden=False).order_by('order', 'name'),
        widget=forms.RadioSelect())


class RegistrationForm(forms.Form):
    """Форма регистрации нового покупателя."""
    email = forms.EmailField(label=u'Электронная почта', max_length=75,
        error_messages={'invalid': u'Неверный формат почтового адреса.',})

    password1 = forms.CharField(label=u'Пароль', min_length=PASSWORD_MIN_LEN, widget=forms.PasswordInput,
        error_messages={
            'min_length': u'Не менее %s символов.' % PASSWORD_MIN_LEN,
            'required': u'Придумайте и укажите пароль.',},
        help_text = u'Не менее %s символов.' % PASSWORD_MIN_LEN)
    password2 = forms.CharField(label=u'Повтор пароля', widget=forms.PasswordInput)

    subscribe = forms.BooleanField(label=u'Присылать мне предложения', initial=True, required=False)
    tos = forms.BooleanField(label=u'Я принимаю условия Договора продажи', initial=True,
        error_messages={'required': u'Необходимо согласиться с условиями Договора.',})

    def clean_email(self):
        """Проверить не занят ли email."""
        email = self.cleaned_data['email']
        if not email:
            return email
        buyers = Buyer.objects.filter(email__iexact = email)
        if buyers:
            raise forms.ValidationError(u'Такой адрес уже зарегистрирован. Используйте форму "Вход".')
        return email

    def clean(self):
        super(RegistrationForm, self).clean()
        # проверить чтобы оба пароля совпадали
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2:
            if password1 != password2:
                set_field_error(self, 'password2', u'Пароли не совпадают.')
        return self.cleaned_data


class ProfileForm(forms.Form):
    """Форма редактирования реквизитов покупателя."""
    email = forms.EmailField(label=u'Электронная почта', max_length=75,
        error_messages={'invalid': u'Неверный формат почтового адреса.',})
    phone = forms.CharField(label=u'Телефон', required=False)
    last_name = forms.CharField(label=u'Фамилия', max_length=30, required=False)
    first_name = forms.CharField(label=u'Имя', max_length=30, required=False)
    mid_name = forms.CharField(label=u'Отчество', max_length=30, required=False)
    city = forms.ModelChoiceField(label=u'Город', queryset=City.objects.all(), required=False)
    address = forms.CharField(label=u'Улица, дом, корпус, квартира', max_length=100, required=False)
    subscribe = forms.BooleanField(label=u'Я хочу получать новости и предложения магазина по электронной почте',
        initial=True, required=False)

    def __init__(self, user, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self._user = user

    def clean_email(self):
        """Проверить не занят ли email."""
        email = self.cleaned_data['email']
        if email == self._user.email:
            return email
        buyers = Buyer.objects.filter(email__iexact = email)
        if buyers:
            raise forms.ValidationError(u'Такой адрес уже зарегистрирован.')
        return email


class ChangePasswordForm(forms.Form):
    """Форма изменения пароля покупателя."""
    old_password = forms.CharField(label=u'Действующий пароль', widget=forms.PasswordInput)
    password1 = forms.CharField(label=u'Новый пароль', min_length=PASSWORD_MIN_LEN, widget=forms.PasswordInput,
        error_messages={
            'min_length': u'Не менее %s символов.' % PASSWORD_MIN_LEN,
            'required': u'Придумайте и укажите новый пароль.',},
        help_text=u'Не менее %s символов.' % PASSWORD_MIN_LEN)
    password2 = forms.CharField(label=u'Повтор нового пароля', widget=forms.PasswordInput)
    # captcha = CaptchaField(label=u'Код с картинки')

    def __init__(self, user, *args, **kwargs):
        super(ChangePasswordForm, self).__init__(*args, **kwargs)
        self._user = user

    def clean_old_password(self):
        """Проверить старый пароль."""
        old_password = self.cleaned_data.get('old_password')
        if old_password and not self._user.check_password(old_password):
            raise forms.ValidationError(u'Неверный пароль.')
        return old_password

    def clean(self):
        super(ChangePasswordForm, self).clean()
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        # проверить чтобы оба новых пароля совпадали
        if password1 and password2:
            if password1 != password2:
                set_field_error(self, 'password2', u'Пароли не совпадают.')
        return self.cleaned_data


class LoginForm(forms.Form):
    """Форма входа покупателя."""
    email = forms.EmailField(label=u'Электронная почта', max_length=75,
        error_messages={'invalid': u'Неверный формат почтового адреса.',})
    password = forms.CharField(label=u'Пароль', widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.user_cache = None # кешировать юзера в форме, чтобы повторно не лазить в базу из вьюхи

    def clean(self):
        super(LoginForm, self).clean()
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        auth_err = u'Неправильный адрес электронной почты или пароль.'

        if email:
            try:
                # попробовать войти по email
                username = Buyer.objects.get(email__iexact = email).username
                self.user_cache = authenticate(username = username, password = password)
            except Buyer.DoesNotExist, Buyer.MultipleObjectsReturned:
                raise forms.ValidationError(auth_err)

        if not self.user_cache:
            raise forms.ValidationError(auth_err)
        elif self.user_cache and not self.user_cache.is_active:
            raise forms.ValidationError(u'Пользователь заблокирован.')

        return self.cleaned_data

    def get_user(self):
        return self.user_cache


class ResetPasswordForm(forms.Form):
    """Форма сброса пароля."""
    email = forms.EmailField(label=u'Электронная почта', max_length=75,
        error_messages={'invalid': u'Неверный формат почтового адреса.',})
    # captcha = CaptchaField(label=u'Код с картинки')

    def __init__(self, *args, **kwargs):
        super(ResetPasswordForm, self).__init__(*args, **kwargs)
        self.user_cache = None # кешировать юзера в форме, чтобы повторно не лазить в базу из вьюхи

    def clean(self):
        super(ResetPasswordForm, self).clean()
        email = self.cleaned_data.get('email')

        if email:
            try:
                # попробовать найти покупателя по email
                self.user_cache = Buyer.objects.get(email__iexact = email)
            except Buyer.DoesNotExist, Buyer.MultipleObjectsReturned:
                raise forms.ValidationError(u'Неправильный адрес электронной почты.')

        return self.cleaned_data

    def get_user(self):
        return self.user_cache


class OrderCheckoutForm(forms.Form):
    """Форма оформления заказа."""
    last_name = forms.CharField(label=u'Фамилия', max_length=30)
    first_name = forms.CharField(label=u'Имя', max_length=30)
    mid_name = forms.CharField(label=u'Отчество', max_length=30)
    city = forms.ModelChoiceField(label=u'Город', queryset=City.objects.all())
    address = forms.CharField(label=u'Улица, дом, корпус, квартира', max_length=100)
    phone = forms.CharField(label=u'Телефон', max_length=20)
    payment_method = forms.ChoiceField(label=u'Способ оплаты', choices=Order._BUYER_PAYMENT_METHOD_CHOICES,
        widget=forms.RadioSelect)


class OrderConfirmForm(forms.Form):
    """Форма подтверждения заказа."""
    tos = forms.BooleanField(label = u'Я принимаю условия продажи', widget = forms.CheckboxInput(),
        error_messages = {'required': u'Нужно согласиться с условиями продажи.',})


class OrderAdminForm(forms.ModelForm):
    class Meta:
        model = Order

    def __init__(self, *args, **kwargs):
        super(OrderAdminForm, self).__init__(*args, **kwargs)
        try:
            self.fields['status'].choices = self.instance.get_status_choices()
        except AttributeError:
            pass


class OrderedItemAdminForm(forms.ModelForm):
    class Meta:
        model = OrderedItem

    def __init__(self, *args, **kwargs):
        super(OrderedItemAdminForm, self).__init__(*args, **kwargs)
        try:
            self.fields['good'].queryset = Good.objects.all().order_by('name')
        except AttributeError:
            pass


class OrderCancelForm(forms.Form):
    """Форма отмены заказа."""
    reason = forms.CharField(max_length=256, widget=forms.Textarea(attrs={'cols': '40', 'rows': '5'}), required=False)


class OrderNoRegForm(forms.Form):
    """Форма заказа без регистрации."""
    name = forms.CharField(label=u'Ваше имя', max_length=50)
    phone = forms.CharField(label=u'Ваш телефон', max_length=30)


class CategoryAdminForm(forms.ModelForm):
    parent = TreeNodeChoiceField(label=u'Родительская категория', required=False,
        queryset=Category.objects.all().order_by('tree_id', 'lft', 'order', 'name'))

    class Meta:
        model = Category
        widgets = {
            'search_text': TinyMCE,
        }


class GoodAdminForm(forms.ModelForm):
    category = TreeNodeChoiceField(label=u'Категория', required=False,
        queryset=Category.objects.all().order_by('tree_id', 'lft', 'order', 'name'),
        widget=forms.Select(attrs={'size': '20'})
    )

    class Meta:
        model = Good
