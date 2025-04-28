from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext_lazy as _
from django.views import generic

from client import get_db
from dashboard.mixins import AJAXRequestMixin, PageMixin
from dashboard.participatory_budget.forms import CommuneSelectForm, MonthSelectForm
from grm.utils import sort_dictionary_list_by_field


class DashboardTemplateView(PageMixin, LoginRequiredMixin, generic.TemplateView):
    template_name = 'participatory_budget/dashboard.html'
    title = _('Participatory Budget')
    active_level1 = 'participatory_budget'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        eadl_db = get_db()
        communes_served = eadl_db.get_view_result('communes', 'served')[0]
        context['communes_served'] = communes_served[0]['value'] if communes_served else 0
        context['total_communes'] = eadl_db.get_view_result('communes', 'total_count')[0][0]['value']
        context['commune_select_form'] = CommuneSelectForm()
        context['month_select_form'] = MonthSelectForm()
        return context


class UpdatedTaskListView(AJAXRequestMixin, LoginRequiredMixin, generic.ListView):
    template_name = 'participatory_budget/task_list.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        eadl_db = get_db()
        index = int(self.request.GET.get('index'))
        offset = int(self.request.GET.get('offset'))
        commune = self.request.GET.get('commune', None)
        if commune:
            startkey = [commune, {}]
            endkey = [commune, None]
            tasks = eadl_db.get_view_result(
                'tasks', 'updated_by_administrative_region', descending=True, startkey=startkey, endkey=endkey)
        else:
            tasks = eadl_db.get_view_result('tasks', 'updated', descending=True)
        return tasks[index:index + offset]


class StatementListView(AJAXRequestMixin, LoginRequiredMixin, generic.ListView):
    template_name = 'participatory_budget/statement.html'
    context_object_name = 'phases'

    @staticmethod
    def process_result(result):
        phases = []
        for data in result:
            performance = 0
            completed_tasks = int(data['value'][0])
            tasks = int(data['value'][1])
            if tasks:
                performance = round(completed_tasks * 100 / tasks)
            phase = {
                "title": data['key'][2],
                "performance": performance,
                "completed_tasks": completed_tasks
            }
            phases.append(phase)
        return sort_dictionary_list_by_field(phases, 'performance', True)

    def get_queryset(self):
        month = self.request.GET.get('month', None).split('-')
        year = int(month[0])
        month = int(month[1])
        startkey = [year, month, None, None]
        endkey = [year, month, {}, {}]
        phases = get_db().get_view_result(
            'phases', 'tasks_by_month', group=True, startkey=startkey, endkey=endkey)
        phases = [doc for doc in phases]
        return self.process_result(phases)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['colors'] = [
            'gray', 'lightgray', 'mediumpurple', 'plum', 'mediumslateblue', 'warning', 'primary', 'danger']
        return context
