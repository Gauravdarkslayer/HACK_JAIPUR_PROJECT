from django.urls import path

from . import views

urlpatterns = [
    path("home/", views.home),
    path('login/',views.login),
    path('verify',views.verify),
    path("about", views.about),
    path("contact", views.contact),
    path("savecontact",views.saveContact),
    path('register',views.register),
    path("loginuser",views.loginuser),
    path('logout',views.logout)
]
