from django.urls import path , include

urlpatterns = [
    path('college/', include('web.urls')),
    path('student/', include('student.urls')),
    path('faculty/', include('faculty.urls')),
    path('',include('auth0login.urls')),
    path('', include('django.contrib.auth.urls')),


    path('', include('social_django.urls')),
]
