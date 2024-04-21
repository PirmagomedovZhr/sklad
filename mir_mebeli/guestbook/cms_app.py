from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool
from django.utils.translation import ugettext_lazy as _

class GuestbookApphook(CMSApp):
    name = _("Guestbook")
    urls = ["guestbook.urls"]

apphook_pool.register(GuestbookApphook)
