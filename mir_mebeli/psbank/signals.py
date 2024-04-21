# -*- coding: utf-8 -*-
from django.dispatch import Signal

pay_received = Signal(providing_args=['operation',])
