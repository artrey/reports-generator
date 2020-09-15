"""reports_generator URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, reverse_lazy, include
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView

from report.urls import urls

urlpatterns = [
    path('', include(urls)),
    path('admin/', admin.site.urls),
    path('login/', LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page=reverse_lazy('login')), name='logout'),
    path('password-change/', PasswordChangeView.as_view(
        success_url=reverse_lazy('send_report'),
        template_name='report/password_change.html'
    ), name='password-change'),
    path('ckeditor/', include('ckeditor_uploader.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
