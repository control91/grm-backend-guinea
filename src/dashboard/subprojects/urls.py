from django.urls import path

from dashboard.subprojects import views

app_name = 'subprojects'
urlpatterns = [
    path('', views.DashboardTemplateView.as_view(), name='dashboard'),
]
