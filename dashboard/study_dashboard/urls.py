from django.urls import path
from . import views

app_name = 'study_dashboard' # Namespace for URLs

urlpatterns = [
    # Example: / (root of the app, mapped in project urls.py)
    path('', views.study_list, name='study_list'),
    # Example: /study/some-study-key/
    path('study/<str:study_key>/', views.study_detail, name='study_detail'),
] 