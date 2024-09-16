"""
URL configuration for ScholarshipNexus project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls import include, path
from . import views

urlpatterns = [
    # Authentication URLs
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('', views.index, name='index'),
    path('universities/', views.university_search, name='university_search'),
    path('universities/shortlist/<int:university_id>/', views.shortlist_university, name='shortlist_university'),
    path('universities/remove_shortlist/<int:university_id>/', views.remove_shortlist_university,
         name='remove_shortlist_university'),
    path('profile/', views.profile_view, name='profile'),

    path('professors/', views.professor_search, name='professor_search'),
    path('opportunities/', views.opportunity_search, name='opportunity_search'),
    path('departments/<int:department_id>/', views.department_detail, name='department_detail'),
    path('professors/<int:professor_id>/', views.professor_detail, name='professor_detail'),
    path('universities/<int:university_id>/', views.university_detail, name='university_detail'),

    path('export-data/', views.export_data, name='export_data'),
    path('import-data/', views.import_data, name='import_data'),
    path('chatbot/', views.chatbot_interaction, name='chatbot_interaction'),
]
