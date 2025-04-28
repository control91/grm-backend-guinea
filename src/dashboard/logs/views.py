from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext_lazy as _
from django.views import generic

from dashboard.mixins import PageMixin


class DashboardTemplateView(PageMixin, LoginRequiredMixin, generic.TemplateView):
    template_name = 'common/under_construction.html'
    title = _('Logs')
    active_level1 = 'logs'
