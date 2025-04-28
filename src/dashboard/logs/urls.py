from django.urls import path

from dashboard.logs import views

app_name = 'logs'
urlpatterns = [
    path('', views.DashboardTemplateView.as_view(), name='dashboard'),
]
