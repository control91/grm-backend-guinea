from django.urls import path

from dashboard.diagnostics import views

app_name = 'diagnostics'
urlpatterns = [
    path('', views.HomeFormView.as_view(), name='home'),
    path('issues-statistics/', views.IssuesStatisticsView.as_view(), name='issues_statistics'),
    path('get-prefecture-by-region-id/', views.GetPrefectureByRegionId.as_view(), name='get_prefecture_by_region_id'),
]
