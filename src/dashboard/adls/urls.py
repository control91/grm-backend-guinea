from django.urls import path

from dashboard.adls import views

app_name = 'adls'
urlpatterns = [
    path('', views.AdlListView.as_view(), name='list'),
    path('<slug:id>/', views.AdlDetailView.as_view(), name='detail'),
    path('toggle-status/<slug:id>/', views.ToggleAdlStatusView.as_view(), name='toggle_status'),
    path('edit-profile/<slug:id>/', views.EditAdlProfileFormView.as_view(), name='edit_profile'),
]
