from django.conf.urls.static import static
from django.urls import path

from app import views
from askme_rasulov import settings

urlpatterns = [
    path('like_question/', views.like_question, name='like_question'),
    path('member/<str:member_nickname>', views.member, name='member'),
    path('logout', views.logout, name='logout'),
    path('profile/edit', views.edit_profile, name='edit-profile'),
    path('ask', views.ask, name='ask'),
    path('signup', views.signup, name='signup'),
    path('login', views.login, name='login'),
    path('tag/<str:tag_id>', views.tag, name='tag'),
    path('', views.index, name='index'),
    path('hot', views.hot, name='hot'),
    path('question/<int:question_id>', views.question, name='question')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
