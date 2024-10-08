"""
URL configuration for netconnect project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.urls import path, include
from company import views as companyViews
from event import views as eventViews
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', eventViews.home, name='home'),
    path('events/', eventViews.displayEvents, name='events'),
    path('accounts/', include('accounts.urls')),
    path('companies/', companyViews.companyDashboard, name='companies'),
    path('events/subscribe/<int:event_id>/', eventViews.subscribe_event, name='subscribe_event'),
    path('mis-eventos/', eventViews.my_events, name='my_events'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)