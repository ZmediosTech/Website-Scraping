from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='scraped-data'),
    path('get_filter_data/', views.get_filter_data, name='get_filter_data'),
    path('scrape_view_franchises/', views.scrape_view_franchises, name='scrape_view_franchises'),
    path('scrape_view_bta/', views.scrape_view_bta, name='scrape_view_bta'),
    path('scrape_view_bfs_franchises/', views.scrape_view_bfs_franchises, name='scrape_view_bfs_franchises'),
    path('scrape_view_bfs_bta/', views.scrape_view_bfs_bta, name='scrape_view_bfs_bta'),
]