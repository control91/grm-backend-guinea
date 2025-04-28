from django.urls import path

from dashboard.participatory_budget import views

app_name = 'participatory_budget'
urlpatterns = [
    path('', views.DashboardTemplateView.as_view(), name='dashboard'),
    path('updated-task-list', views.UpdatedTaskListView.as_view(), name='updated_task_list'),
    path('statement', views.StatementListView.as_view(), name='statement'),
]
