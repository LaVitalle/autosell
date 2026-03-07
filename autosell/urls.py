from django.urls import include, path
from django.contrib import admin
from django.contrib.auth import views as auth_views
from dashboard import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('admin/', admin.site.urls),
    path('products/', include('products.urls')),
    path('categories/', include('categories.urls')),
    path('contacts/', include('contacts.urls')),
    path('messages/', include('wppmessages.urls')),
    # Rotas de autenticação nativas do Django
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('accounts/password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
]