from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings
urlpatterns = [
    path('register/',views.register,name='register'),
    path('login/',views.login,name='login'),
    path('logout/',views.logout,name='logout'),

    path('activate/<uidb64>/<token>/',views.activate, name='activate'),
    path('forgotPassword/',views.forgotPassword, name='forgotPassword'),
    path('resetpassword_validate/<uidb64>/<token>/',views.resetpassword_validate, name='resetpassword_validate'),
    path('resetPassword/',views.resetPassword, name='resetPassword'), 

    path('dashboard/', views.dashboard, name='dashboard'), 
    path('edit_profile',views.edit_user_details, name='edit_profile'),
    path('change_password',views.change_password,name='change_password'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
