# -*- coding: utf-8 -*-
from django import forms

import conf


class HiddenPayForm(forms.Form):
    """Платежная форма, все поля скрыты."""

    AMOUNT = forms.CharField(widget=forms.HiddenInput)
    CURRENCY = forms.CharField(widget=forms.HiddenInput)
    ORDER = forms.CharField(widget=forms.HiddenInput)
    DESC = forms.CharField(widget=forms.HiddenInput)
    TERMINAL = forms.CharField(widget=forms.HiddenInput)
    TRTYPE = forms.CharField(widget=forms.HiddenInput)
    MERCH_NAME = forms.CharField(widget=forms.HiddenInput)
    MERCHANT = forms.CharField(widget=forms.HiddenInput)
    EMAIL = forms.CharField(widget=forms.HiddenInput)
    TIMESTAMP = forms.CharField(widget=forms.HiddenInput)
    NONCE = forms.CharField(widget=forms.HiddenInput)
    BACKREF = forms.CharField(widget=forms.HiddenInput)
    P_SIGN = forms.CharField(widget=forms.HiddenInput)

    def get_action_url(self):
        return conf.PAYMENT_URL
