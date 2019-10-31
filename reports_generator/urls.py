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
from django.contrib import admin
from django.urls import path, reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView

from report.views import SendReportView

urlpatterns = [
    path('', SendReportView.as_view(), name='send_report'),
    path('report/<int:rid>/', SendReportView.as_view(), name='report'),
    path('approved/', SendReportView.as_view(), name='approved'),
    path('rejected/', SendReportView.as_view(), name='rejected'),
    path('verification/', SendReportView.as_view(), name='verification'),
    path('admin/', admin.site.urls),
    path('login/', LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page=reverse_lazy('login')), name='logout'),
]
