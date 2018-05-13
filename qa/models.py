from django.db import models
from django.contrib.auth.models import User
from django_markdown.models import MarkdownField
from main_app.models import *
from ckeditor.fields import RichTextField  
from ckeditor_uploader.fields import RichTextUploadingField

# Create your models here.
class Tag(models.Model):
    slug = models.SlugField(max_length=100, unique=True)

    def __str__(self):
        return self.slug

    class Meta:
        ordering = ('slug',)


###################################################################################

# class Profil(models.Model):
#     user = models.OneToOneField(User, on_delete=True)
#     points = models.IntegerField(default=0)

#     website = models.URLField(blank=True)
#     picture = models.ImageField(upload_to='qa/static/profile_images', blank=True)
#     date_naissance = models.DateField()
#     # entreprise = models.ForeignKey(Entreprise,blank=True,null=True,  on_delete=models.CASCADE)
#     # photo_profil = models.OneToOneField(Image, blank=True,null=True, on_delete=models.CASCADE, related_name="profil_photo")
#     # photo_couverture = models.OneToOneField(Image, blank=True,null=True, on_delete=models.CASCADE, related_name="photo_cover")
#     facebook = models.CharField(max_length=300, blank=True, null=True, default="")
#     youtube = models.CharField(max_length=300, blank=True, null=True, default="")
#     instagram = models.CharField(max_length=300, blank=True, null=True, default="")
#     linkedin = models.CharField(max_length=300, blank=True, null=True, default="")
#     tel = models.CharField(max_length=300, blank=True, null=True, default="")
#     ville = models.CharField(max_length=300, blank=True, null=True, default="")
#     pays = models.CharField(max_length=300, blank=True, null=True, default="")
#     fonction = models.CharField(max_length=300, blank=True, null=True, default="")
#     service = models.CharField(max_length=300, blank=True, null=True, default="")

#     def __str__(self):
#         return self.user.username


###################################################################################


class Categorie(models.Model):
    title_categorie = models.CharField(max_length=100)
    description_categorie = models.CharField(max_length=200)


    def __str__(self):
        return self.title_categorie


###################################################################################

class Question(models.Model):
    # question_text = models.CharField(max_length=200)
    question_text = RichTextUploadingField ()
    question_title = models.CharField(max_length=200)
    # question_text = MarkdownField()
    pub_date = models.DateTimeField('date published')
    tags = models.ManyToManyField(Tag)
    reward = models.IntegerField(default=0)
    views = models.IntegerField(default=0)
    user_data = models.ForeignKey('main_app.Profil', on_delete=True)
    closed = models.BooleanField(default=False)
    categorie = models.ForeignKey(Categorie, on_delete=True,null=True,blank=True)
    type_pub = models.CharField(max_length=200 , default='question')


    def __str__(self):
        return self.question_text


###################################################################################

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=True ,null=True,blank=True)
    answer_text = RichTextUploadingField()
    votes = models.IntegerField(default=0)
    pub_date = models.DateTimeField('date published')
    user_data = models.ForeignKey('main_app.Profil', on_delete=True)

    def __str__(self):
        return self.answer_text


###################################################################################

class Voter(models.Model):
    user = models.ForeignKey('main_app.Profil', on_delete=True)
    answer = models.ForeignKey(Answer, on_delete=True)


###################################################################################

class QVoter(models.Model):
    user = models.ForeignKey('main_app.Profil', on_delete=True)
    question = models.ForeignKey(Question, on_delete=True)


###################################################################################

class Comment(models.Model):
    answer = models.ForeignKey(Answer, on_delete=True)
    comment_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    user_data = models.ForeignKey('main_app.Profil', on_delete=True)

    def __str__(self):
        return self.comment_text

###################################################################################
