"""askme URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.contrib import admin, auth
from django.urls import path
from app import views
from django.conf.urls.static import static
from askme import settings

urlpatterns = [
    path('index/', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('hot/', views.hot, name='hot'),
    path('register/', views.register, name='register'),
    path('settings/', views.settings, name='settings'),
    path('ask/', views.ask, name='ask'),
    path('admin/', admin.site.urls),
    path('question/<int:qid>/', views.question, name='question'),
    path('question2/<int:qid>/#<int:anchor>', views.question, name='question2'),
    path('tag/<str:tag_name>/', views.tag, name='tag'),
    path('like/', views.like, name='like'),
    path('dislike/', views.dislike, name='dislike'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
