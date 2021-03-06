from django.conf.urls import  url
from django.contrib import admin
from django.urls import path , re_path ,include
from qa import views

app_name = "qa"

urlpatterns = [

	url(r'^markdown/', include("django_markdown.urls")),
	re_path(r'^accueil', views.index1, name='index1'),
    path('', views.index2, name='index2'),
	# path('index2', views.index1, name='index1'),
	re_path(r'^add/$', views.add, name='ajouter'),
	re_path(r'^q/(?P<question_id>\d+)/$', views.detail, name='detail'),
    re_path(r'^answer/$', views.add_answer, name='add_answer'),
    re_path(r'^comment/(?P<answer_id>\d+)/$', views.comment, name='comment'),
    re_path(r'^vote/(?P<user_id>\d+)/(?P<answer_id>\d+)/(?P<question_id>\d+)/(?P<op_code>\d+)/$', views.vote, name='vote'),
    re_path(r'^search/$', views.search, name='search'),
    re_path(r'^thumb/(?P<user_id>\d+)/(?P<question_id>\d+)/(?P<op_code>\d+)', views.thumb, name='thumb'),
    re_path(r'^updateq/(?P<question_id>\d+)/$', views.updateq, name='updateq'),
    re_path(r'^profil/$', views.profil, name='profil'),
    re_path(r'^closequestion/$', views.closequestion, name='closequestion'),
    re_path(r'^updateprofil/$', views.updateprofil, name='updateprofil'),
    re_path(r'^tag/(?P<tag>\w+)/$', views.tag, name='tag'),
 #    re_path(r'^categorie/$', views.categorie, name='categorie'),
 	re_path(r'^change_img/$', views.changeimage, name='changeimage'),
    re_path(r'^list_tags', views.list_tags, name='list_tags'),
    re_path(r'^my_question', views.myquestion, name='myquestion'),
    
]