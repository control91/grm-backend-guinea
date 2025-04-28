from datetime import datetime

from django import forms
from django.utils.translation import gettext_lazy as _

from client import get_db
from grm.utils import get_month_range


class CommuneSelectForm(forms.Form):
    commune = forms.ChoiceField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        view_result = get_db().get_view_result('communes', 'updated_tasks', group=True)
        communes = [(c['key'][0], c['key'][1]) for c in view_result]
        self.fields['commune'].widget.choices = [('', '')] + communes
        self.fields['commune'].widget.attrs['class'] = 'form-control'


class MonthSelectForm(forms.Form):
    month = forms.ChoiceField(label=_("Show:"))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        phases = get_db().get_view_result('phases', 'tasks_by_month', group=True)[0]
        if phases:
            older_phase = phases[0]['key']
            start_date = datetime.strptime(f'{older_phase[0]}-{older_phase[1]}', '%Y-%m')
            month_range = get_month_range(start_date)
            current_month = month_range[0]
            default_option = [(current_month[0], _("This month"))]
            self.fields['month'].widget.choices = default_option + month_range[1:]
