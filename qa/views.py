from django.shortcuts import render ,redirect
from django.core.mail import send_mail
from django.conf import settings
from qa.models import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template import RequestContext, loader
from django.http import HttpResponseRedirect, HttpResponse
import datetime
from django.contrib.auth.decorators import login_required
from .forms import UserProfileForm , QuestionForm , AnswerForm
from main_app.forms import userProfile , userform ,PhotoForm
from main_app.models import *
from django.shortcuts import get_object_or_404 , render_to_response, render
from django.core import serializers
from django.db.models import Q
# Create your views here.

def mySession(request):
        # ***************** session ***********************
    # count_q = Question.objects.count()
    # count_a = Answer.objects.count()    
    # # if 'count_q' not in request.session:
    # request.session["count_q"] = count_q
    # # if 'count_a' not in request.session:
    # request.session["count_a"] = count_a
   
    # # if 'top_questions' not in request.session:
    # request.session['top_questions']= list(Question.objects.order_by('-views','reward')[:5].values("id","categorie","closed","user_data","views","reward","tags","question_title","question_text"))
   
    # # if 'dernier_null_list' not in request.session:
    # request.session['dernier_null_list']= list(Question.objects.order_by('-pub_date').filter(answer__isnull=True)[:5].values("id","categorie","closed","user_data","views","reward","tags","question_title","question_text"))
   
    # # if 'categories' not in request.session:
    # request.session['categories']= list(Categorie.objects.all().values("id","title_categorie"))
    
    # # if 'tags' not in request.session:    
    # request.session['tags']= list(Tag.objects.all().values("id","slug"))

    if request.user.is_anonymous == False:
        user_id = request.user.id
        user_ob = User.objects.get(id=user_id)
        profil = Profil.objects.get(user=user_ob) 
        request.session['id_profil'] =profil.id
        try:
            request.session['img_profil'] =profil.photo_profil.image.url
        except Exception as e:
            pass
                   
    # ***************** end session ***********************


def variableGlobal(request):
    context = {
        'count_q':Question.objects.count(),
        'count_a':Answer.objects.count(),
        'top_questions':Question.objects.order_by('-views','reward')[:5],
        'dernier_null_list':Question.objects.order_by('-pub_date').filter(answer__isnull=True)[:5],
        'categories':Categorie.objects.all(),
        'tags':Tag.objects.all(),
    }

    return context 

def index1(request):

    contextGlobal = variableGlobal(request)

    dernier_question_list = Question.objects.order_by('-pub_date')
    dernier_null_list = Question.objects.order_by('-pub_date').filter(answer__isnull=True)[:10]
    top_questions_null = Question.objects.order_by('-reward').filter(answer__isnull=True,reward__gte=1)[:10]
    top_questions = Question.objects.order_by('-views').filter(reward__gte=1)[:10]

    mySession(request)
    # food_list = [f for f in Question.objects.order_by('-pub_date')]
    # data = serializers.serialize("xml", Question.objects.order_by('-pub_date'))
    # food_list.append()

    # request.session['data']= list(Question.objects.all().values("question_title","question_text"))
    

    paginator = Paginator(dernier_question_list, 10)
    page = request.GET.get('page')
    try:
        questions = paginator.page(page)
    except PageNotAnInteger:
        questions = paginator.page(1)
    except EmptyPage:
        questions = paginator.page(paginator.num_pages)


    context = {
        'questions': questions,
        'question_null': dernier_null_list,
        'question_top': top_questions,
    }

    context.update(contextGlobal)
    
    if request.user.is_anonymous:
        return render(request,'qa/index1.html', context)
    
    user_id = request.user.id
    user_ob = User.objects.get(id=user_id)
    profil = Profil.objects.get(user=user_ob) 
    context['profil'] =profil
    context['mu'] =settings.MEDIA_URL
    context['mr'] =settings.MEDIA_ROOT    
    # return render(request,'qa/index2.html', context)
    # return render_to_response('qa/index1.html', context, context_instance=RequestContext(request))
    # template = loader.get_template('qa/index2.html')
    # return HttpResponse(template.render(context))
    # return HttpResponse(template.render(context, request))
    return render(request,'qa/index2.html', context)

def index2(request):
    return render(request,'qa/index2.html', {})    

@login_required(login_url='/main/login/') 
def add(request):

    contextGlobal = variableGlobal(request)

    dernier_question_list = Question.objects.order_by('-pub_date')
    dernier_null_list = Question.objects.order_by('-pub_date').filter(answer__isnull=True)[:10]
    top_questions_null = Question.objects.order_by('-reward').filter(answer__isnull=True,reward__gte=1)[:10]
    top_questions = Question.objects.order_by('-views').filter(reward__gte=1)[:10]

    context = {}
    context.update(contextGlobal)
    form = QuestionForm()
    context['form'] = form
    if request.user.is_anonymous == True:
        return HttpResponseRedirect("/main/login/")
        # return render(request, 'qa/login.html', locals())

    mySession(request)
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            # question_text = request.POST['question']
            question_title = request.POST['titre']
            categorie = request.POST['categorie']
            tags_text = request.POST['tags']
            user_id = request.POST['user']
            user_ob = User.objects.get(id=user_id)
            user = Profil.objects.get(user=user_ob)

            # if question_text.strip() == '':
            #     return render(request, 'qa/add.html', {'message': 'Empty'})

            pub_date = datetime.datetime.now()
            # q = Question()
            # q.question_text = question_text
            post.question_title = question_title
            post.pub_date = pub_date
            post.user_data = user
            post.categorie = Categorie.objects.get(id = categorie)
            post.save()

            if '' != tags_text:
                tags = tags_text.split(',')
                for tag in tags:
                    try:
                        t = Tag.objects.get(slug=tag)
                        post.tags.add(t)
                    except Tag.DoesNotExist:
                        t=Tag()
                        t.slug = tag
                        t.save()
                        post.tags.add(t)
            return HttpResponseRedirect('/')            

        #send_mail('QA: Your Question has been Posted.', 'Thank you for posting the question, '+question_text+'. We will notify you once someone posts an answer.', 'admin@test.com', [request.user.email], fail_silently=False)

        return HttpResponseRedirect('/qa')
    # return HttpResponse(template.render(context))
    # return render(request, 'qa/add.html', locals())
    context['form'] = form
    return render(request, 'qa/add.html', context)


def detail(request, question_id):

    contextGlobal = variableGlobal(request)
    dernier_question_list = Question.objects.order_by('-pub_date')
    dernier_null_list = Question.objects.order_by('-pub_date').filter(answer__isnull=True)[:10]
    top_questions_null = Question.objects.order_by('-reward').filter(answer__isnull=True,reward__gte=1)[:10]
    top_questions = Question.objects.order_by('-views').filter(reward__gte=1)[:10]

    mySession(request)

    form_a = AnswerForm(None)
   
    if request.user.is_authenticated:

        user_id = request.user.id
        user_ob = User.objects.get(id=user_id)
        profil = Profil.objects.get(user=user_ob)
        nbQusetion = profil.question_set.count
        nbAnswer = profil.answer_set.count 
        # id_img = profil.photo_profil.image


    try:
        question = Question.objects.get(pk=question_id)
        question.views += 1
        question.save()
        answer_list = question.answer_set.order_by('-votes')

        paginator = Paginator(answer_list, 10)
        page = request.GET.get('page')
        try:
            answers = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            answers = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            answers = paginator.page(paginator.num_pages)

    except Question.DoesNotExist:
        raise Http404("Question does not exist")

    context = {
        'question_null': dernier_null_list,
        'question_top': top_questions,
        'form_a':form_a,
        'answers': answers, 
        'question': question 
    }

    context.update(contextGlobal)
    return render(request, 'qa/detail.html', context )

@login_required(login_url='/main/login/') 
def add_answer(request):

    contextGlobal = variableGlobal(request)
    dernier_question_list = Question.objects.order_by('-pub_date')
    dernier_null_list = Question.objects.order_by('-pub_date').filter(answer__isnull=True)[:10]
    top_questions_null = Question.objects.order_by('-reward').filter(answer__isnull=True,reward__gte=1)[:10]
    top_questions = Question.objects.order_by('-views').filter(reward__gte=1)[:10]


    mySession(request)

    context = {}
    context.update(contextGlobal)

    if request.method == 'POST':

        form_a = AnswerForm(request.POST)
        a = form_a.save(commit=False)
        # answer_text = request.POST['answer']
        question_id = request.POST['question']
        user_id = request.POST['user']

        question = Question.objects.get(pk=question_id)
        user_ob = User.objects.get(id=user_id)
        user = Profil.objects.get(user=user_ob)
        user.points += 5
        user.save()

        # if answer_text.strip() == '':
        #     return render(request, 'qa/answer.html', {'question': question, 'message': 'Empty'})

        # a = Answer()
        pub_date = datetime.datetime.now()
        # a.answer_text = answer_text
        a.question = question
        a.user_data = user
        a.pub_date = pub_date
        a.save()

        answer_list = question.answer_set.order_by('-votes')

        paginator = Paginator(answer_list, 10)
        page = request.GET.get('page')
        try:
            answers = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            answers = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            answers = paginator.page(paginator.num_pages)

        # return render(request, 'qa/detail.html', {'question': question, 'answers': answers})
        return redirect('qa:detail', question_id=question.id)

    # return render(request, 'qa/detail.html', {'question': question})
    return redirect('qa:detail', question_id=question.id)

@login_required(login_url='/main/login/') 
def thumb(request, user_id, question_id, op_code):

    contextGlobal = variableGlobal(request)

    user_ob = User.objects.get(id=user_id)
    user = Profil.objects.get(user=user_ob)
    question = Question.objects.get(pk=question_id)

    answer_list = question.answer_set.order_by('-votes')

    mySession(request)


    paginator = Paginator(answer_list, 10)
    page = request.GET.get('page')
    try:
        answers = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        answers = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        answers = paginator.page(paginator.num_pages)


    form_a = AnswerForm(None)

    context = {'question': question, 'answers': answers , 'form_a':form_a}
    context.update(contextGlobal)

    if QVoter.objects.filter(question_id=question_id, user=user).exists():
        context['message'] = "Vous avez déjà voté sur cette question!"
        return render(request, 'qa/detail.html', context)

    if op_code == '0':
        question.reward += 5
        u = question.user_data
        u.points += 5
        u.save()
    if op_code == '1':
        question.reward -= 5
        u = question.user_data
        u.points -= 5
        u.save()
    question.save()

    v = QVoter()
    v.user = user
    v.question = question
    v.save()

    

    return render(request, 'qa/detail.html', context)

@login_required(login_url='/main/login/') 
def vote(request, user_id, answer_id, question_id, op_code):

    contextGlobal = variableGlobal(request)
    user_ob = User.objects.get(id=user_id)
    user = Profil.objects.get(user=user_ob)
    answer = Answer.objects.get(pk=answer_id)
    question = Question.objects.get(pk=question_id)

    answer_list = question.answer_set.order_by('-votes')

    mySession(request)

    paginator = Paginator(answer_list, 10)
    page = request.GET.get('page')
    try:
        answers = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        answers = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        answers = paginator.page(paginator.num_pages)

    form_a = AnswerForm(None)

    context = {'question': question, 'answers': answers , 'form_a':form_a}
    context.update(contextGlobal)

    if Answer.objects.filter(id=answer_id, user_data=user).exists():
        context['message']="You cannot vote on your answer!"
        return render(request, 'qa/detail.html',context )

    if Voter.objects.filter(answer_id=answer_id, user=user).exists():
        context['message']="You've already cast vote on this answer!"
        return render(request, 'qa/detail.html', context)

    if op_code == '0':
        answer.votes += 1
        u = answer.user_data
        u.points += 10
        u.points += question.reward
        u.save()
    if op_code == '1':
        answer.votes -= 1
        u = answer.user_data
        u.points -= 10
        u.save()
    answer.save()

    v = Voter()
    v.user = user
    v.answer = answer
    v.save()

    return render(request, 'qa/detail.html', context)


@login_required(login_url='/main/login/') 
def comment(request, answer_id):

    contextGlobal = variableGlobal(request)


    mySession(request)

    context =  {'answer_id': answer_id, 'message': 'Empty'}
    context.update(contextGlobal)

    if request.user.is_anonymous:
        return HttpResponseRedirect("/accounts/login//")

    if request.method == 'POST':
        comment_text = request.POST['comment']
        user_id = request.POST['user']
        user_ob = User.objects.get(id=user_id)
        user = Profil.objects.get(user=user_ob)
        user.points += 1
        user.save()

        if comment_text.strip() == '':
            return render(request, 'qa/comment.html',context)

        pub_date = datetime.datetime.now()
        a = Answer.objects.get(pk=answer_id)
        q_id = a.question_id
        c = Comment()
        c.answer = a
        c.comment_text = comment_text
        c.pub_date = pub_date
        c.user_data = user
        c.save()

        try:
            question = Question.objects.get(pk=q_id)
            question.views += 1
            question.save()
            answer_list = question.answer_set.order_by('-votes')

            paginator = Paginator(answer_list, 10)
            page = request.GET.get('page')
            try:
                answers = paginator.page(page)
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                answers = paginator.page(1)
            except EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of results.
                answers = paginator.page(paginator.num_pages)

        except Question.DoesNotExist:
            raise Http404("Question does not exist")
        form_a = AnswerForm(None)  
        context['answers'] = answers
        context['question'] = question
        context['form_a'] = form_a  
        return render(request, 'qa/detail.html', context )

    template = loader.get_template('qa/detail.html')
    context ['answer_id']= answer_id
    # return HttpResponse(template.render(context))
    return HttpResponse(template.render(context, request))



def search(request):

    contextGlobal = variableGlobal(request)

    mySession(request)

    context = {}
    context.update(contextGlobal)
    if request.method == 'POST':
        word = request.POST['query']
        question_list = Question.objects.filter(Q(question_text__contains=word) | Q(question_title__contains=word))
        paginator = Paginator(question_list, 10)
        page = request.GET.get('page')
        try:
            questions = paginator.page(page)
        except PageNotAnInteger:
        # If page is not an integer, deliver first page.
            questions = paginator.page(1)
        except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
            questions = paginator.page(paginator.num_pages)

        dernier_null_list = Question.objects.order_by('-pub_date').filter(tags__slug__contains=word,answer__isnull=True)[:10]
        top_questions = Question.objects.order_by('-reward').filter(tags__slug__contains=word,answer__isnull=True,reward__gte=1)[:10]

        template = loader.get_template('qa/index.html')


        context = {
        'questions': questions,
        'question_null': dernier_null_list,
        'question_top': top_questions,
        }
        context.update(contextGlobal)
        return render(request , 'qa/index2.html' , context)
    # return HttpResponse(template.render(context))
    # return HttpResponse(template.render(context, request))
    return render(request , 'qa/index2.html' , context)




@login_required
def updateq(request , question_id):
    contextGlobal = variableGlobal(request)

    # template = loader.get_template('qa/add.html')
    mySession(request)

    question = Question.objects.get(pk=question_id)
    dernier_null_list = Question.objects.order_by('-pub_date').filter(answer__isnull=True)[:10]

    list_tags = question.tags.all()
    form = QuestionForm(instance= question )
    if request.user.is_anonymous == True:
        return HttpResponseRedirect("/main/login/")
        # return render(request, 'qa/login.html', locals())

    if request.method == 'POST':
        form = QuestionForm(request.POST or None)
        q = form.save(commit=False)
        question_text = q.question_text
        question_title = request.POST['titre']
        categorie = request.POST['categorie']
        tags_text = request.POST['tags']
        user_id = request.POST['user']
        user_ob = User.objects.get(id=user_id)
        user = Profil.objects.get(user=user_ob)

        if question_text.strip() == '':
            return render(request, 'qa/updateq.html', {'message': 'Empty'})

        pub_date = datetime.datetime.now()
        question.question_text = question_text
        question.question_title = question_title
        question.pub_date = pub_date
        question.user_data = user
        question.categorie = Categorie.objects.get(id = categorie)
        question.save()

        if '' != tags_text:
            tags = tags_text.split(',')
            for tag in tags:
                if '' != tag:
                    try:
                        t = Tag.objects.get(slug=tag)
                        question.tags.add(t)
                    except Tag.DoesNotExist:
                        t=Tag()
                        t.slug = tag
                        t.save()
                        question.tags.add(t)

        #send_mail('QA: Your Question has been Posted.', 'Thank you for posting the question, '+question_text+'. We will notify you once someone posts an answer.', 'admin@test.com', [request.user.email], fail_silently=False)

        return HttpResponseRedirect('/q/'+question_id+'/')
    # return HttpResponse(template.render(context))
    # return render(request, 'qa/add.html', locals())
    context = {
        'question': question,
        'question_null': dernier_null_list,
        'list_tags':list_tags,
        }
    context.update(contextGlobal)
    context['form'] = form
    return render(request, 'qa/updateq.html', context)



@login_required(login_url='/main/login/') 
def profil(request):

    contextGlobal = variableGlobal(request)

    # user_id = request.POST['user']
    mySession(request)

    user_id = request.user.id
    user_ob = get_object_or_404(User, pk=user_id)
    profil = Profil.objects.get(user=user_ob)
    nbQusetion = profil.question_set.count
    nbAnswer = profil.answer_set.count 
    questions = profil.question_set.all()
    form = userProfile(instance=profil)
    formuser = userform(instance = user_ob)
    formimg = PhotoForm()
    # id_img = profil.photo_profil.image
    paginator = Paginator(questions, 10)
    page = request.GET.get('page')
    try:
        mesQusetion = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        mesQusetion = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        mesQusetion = paginator.page(paginator.num_pages)


    context = {
        'nbQusetion': nbQusetion,
        'nbAnswer': nbAnswer ,
        'profil' : profil ,
        'mesQusetion':mesQusetion,
        'form':form,
        'formuser':formuser,
        'formimg':formimg ,
        # 'id_img':id_img,
    }
    context.update(contextGlobal)
    return render(request,'qa/profil.html', context)

@login_required(login_url='/main/login/') 
def updateprofil(request):

    contextGlobal = variableGlobal(request)

    mySession(request)

    if request.method == 'POST':
        user_id = request.POST['user']
        # user_id = request.user.id
        user_ob = User.objects.get(id=user_id)
        profil = Profil.objects.get(user=user_ob)
        nbQusetion = profil.question_set.count
        nbAnswer = profil.answer_set.count 
        mesQusetion = profil.question_set.all()

        profil.website = request.POST['website']
        profil.facebook = request.POST['facebook']
        profil.youtube = request.POST['youtube']
        profil.instagram = request.POST['instagram']
        profil.linkedin = request.POST['linkedin']
        profil.tel = request.POST['tel']
        profil.ville = request.POST['ville']
        profil.pays = request.POST['pays']
        profil.fonction = request.POST['fonction']
        profil.service = request.POST['service']
        profil.save()

        user_ob.username =request.POST['username']
        user_ob.last_name =request.POST['last_name']
        user_ob.first_name =request.POST['first_name']
        user_ob.email =request.POST['email']
        user_ob.save()



        form = userProfile(instance=profil)
        formuser = userform(instance = user_ob)
        formimg = PhotoForm()
        # id_img = profil.photo_profil.image
        context = {
            'nbQusetion': nbQusetion,
            'nbAnswer': nbAnswer ,
            'profil' : profil ,
            'mesQusetion':mesQusetion,
            'form':form,
            'formuser':formuser,
            'formimg':formimg ,
            # 'id_img':id_img,
        }
        context.update(contextGlobal)
        return render(request,'qa/profil.html', context)
        
    return redirect('qa:profil')


def changeimage(request):
    contextGlobal = variableGlobal(request)
    mySession(request)

    if request.method == 'POST':
        img = Image()
        formimg = PhotoForm(request.POST)
        img.image = formimg.image
        img.save()
        user_id = request.POST['user']
        # user_id = request.user.id
        user_ob = User.objects.get(id=user_id)
        profil = Profil.objects.get(user=user_ob)
        profil.photo_profil = img 
        return redirect('qa:profil')
    return redirect('qa:profil')
    



def tag(request, tag):
    contextGlobal = variableGlobal(request)
    word = tag
    latest_question_list = Question.objects.filter(tags__slug__contains=word)
    paginator = Paginator(latest_question_list, 10)
    page = request.GET.get('page')
    try:
        questions = paginator.page(page)
    except PageNotAnInteger:
    # If page is not an integer, deliver first page.
        questions = paginator.page(1)
    except EmptyPage:
    # If page is out of range (e.g. 9999), deliver last page of results.
        questions = paginator.page(paginator.num_pages)

    latest_noans_list = Question.objects.order_by('-pub_date').filter(tags__slug__contains=word,answer__isnull=True)[:10]
    top_questions = Question.objects.order_by('-reward').filter(tags__slug__contains=word,answer__isnull=True,reward__gte=1)[:10]

    template = loader.get_template('qa/index2.html')
    context = {
    'questions': questions,
    'noans': latest_noans_list,
    'reward': top_questions,
    }
    context.update(contextGlobal)
    # return HttpResponse(template.render(context))
    return render(request, 'qa/index2.html' , context)


@login_required(login_url='/main/login/') 
def closequestion(request):
    contextGlobal = variableGlobal(request)
    if request.method == 'POST':
        action = request.POST['closequestion']
        question_id = request.POST['question_id']
        question = Question.objects.get(pk=question_id)
        question.closed = action
        question.save()

        context = {
            'question':question,
            'close':question.closed
        }
    return redirect('qa:profil')    
    return render(request, 'qa/profil.html', context)  







# def index(request):

    

#     if request.user.is_staff :
#         return HttpResponseRedirect("/admin/")

#     dernier_question_list = Question.objects.order_by('-pub_date')
#     dernier_noans_list = Question.objects.order_by('-pub_date').filter(answer__isnull=True)[:10]
#     top_questions_noans = Question.objects.order_by('-reward').filter(answer__isnull=True,reward__gte=1)[:10]
#     top_questions = Question.objects.order_by('-views').filter(reward__gte=1)[:10]

#     categories = Categorie.objects.all()

#     count = Question.objects.count
#     count_a = Answer.objects.count

#     request.session['count_q'] = str(count)
#     paginator = Paginator(dernier_question_list, 10)
#     page = request.GET.get('page')
#     try:
#         questions = paginator.page(page)
#     except PageNotAnInteger:
#         # If page is not an integer, deliver first page.
#         questions = paginator.page(1)
#     except EmptyPage:
#         # If page is out of range (e.g. 9999), deliver last page of results.
#         questions = paginator.page(paginator.num_pages)

#     template = loader.get_template('qa/index.html')
#     tags = Tag.objects.all()
#     context = {
#         'questions': questions,
#         'count': count,
#         'count_a': count_a,
#         'noans': dernier_noans_list,
#         'reward': top_questions,
#         'tags' : tags,
#         'categories':categories,
#     }
#     # return HttpResponse(template.render(context))
#     return render(request,'qa/index.html',context)

# def tag(request, tag):
#     word = tag
#     latest_question_list = Question.objects.filter(tags__slug__contains=word)
#     paginator = Paginator(latest_question_list, 10)
#     page = request.GET.get('page')
#     try:
#         questions = paginator.page(page)
#     except PageNotAnInteger:
#     # If page is not an integer, deliver first page.
#         questions = paginator.page(1)
#     except EmptyPage:
#     # If page is out of range (e.g. 9999), deliver last page of results.
#         questions = paginator.page(paginator.num_pages)

#     latest_noans_list = Question.objects.order_by('-pub_date').filter(tags__slug__contains=word,answer__isnull=True)[:10]
#     top_questions = Question.objects.order_by('-reward').filter(tags__slug__contains=word,answer__isnull=True,reward__gte=1)[:10]
#     count = Question.objects.count
#     count_a = Answer.objects.count

#     template = loader.get_template('qa/index.html')
#     context = {
#     'questions': questions,
#     'totalcount': count,
#     'anscount': count_a,
#     'noans': latest_noans_list,
#     'reward': top_questions,
#     }
#     # return HttpResponse(template.render(context))
#     return render(request, 'qa/index.html' , context)

    
# @login_required(login_url='/main/login/') 
# def add(request):
#     # template = loader.get_template('qa/add.html')
#     categories = Categorie.objects.all()

#     count = Question.objects.count
#     count_a = Answer.objects.count

#     dernier_noans_list = Question.objects.order_by('-pub_date').filter(answer__isnull=True)[:10]
#     tags = Tag.objects.all()
#     context = {'request':RequestContext(request),
#         'count': count,
#         'count_a': count_a,
#         'tags' : tags,
#         'categories':categories,
#         'noans': dernier_noans_list,
#     }
#     form = QuestionForm()
#     context['form'] = form
#     if request.user.is_anonymous == True:
#         return HttpResponseRedirect("/main/login/")
#         # return render(request, 'qa/login.html', locals())

#     if request.method == 'POST':
#         form = QuestionForm(request.method or None)
#         question_text = request.POST['question']
#         question_title = request.POST['titre']
#         categorie = request.POST['categorie']
#         tags_text = request.POST['tags']
#         user_id = request.POST['user']
#         user_ob = User.objects.get(id=user_id)
#         user = Profil.objects.get(user=user_ob)

#         if question_text.strip() == '':
#             return render(request, 'qa/add.html', {'message': 'Empty'})

#         pub_date = datetime.datetime.now()
#         q = Question()
#         q.question_text = question_text
#         q.question_title = question_title
#         q.pub_date = pub_date
#         q.user_data = user
#         q.categorie = Categorie.objects.get(id = categorie)
#         q.save()

#         if '' != tags_text:
#             tags = tags_text.split(',')
#             for tag in tags:
#                 try:
#                     t = Tag.objects.get(slug=tag)
#                     q.tags.add(t)
#                 except Tag.DoesNotExist:
#                     t=Tag()
#                     t.slug = tag
#                     t.save()
#                     q.tags.add(t)

#         #send_mail('QA: Your Question has been Posted.', 'Thank you for posting the question, '+question_text+'. We will notify you once someone posts an answer.', 'admin@test.com', [request.user.email], fail_silently=False)

#         return HttpResponseRedirect('/qa')
#     # return HttpResponse(template.render(context))
#     # return render(request, 'qa/add.html', locals())
#     context['form'] = form
#     return render(request, 'qa/add.html', context)


# def detail(request, question_id):

#     categories = Categorie.objects.all()
#     tags = Tag.objects.all()
#     count = Question.objects.count
#     count_a = Answer.objects.count
#     dernier_noans_list = Question.objects.order_by('-pub_date').filter(answer__isnull=True)[:10]
   

#     if request.user.is_authenticated:

#         user_id = request.user.id
#         user_ob = User.objects.get(id=user_id)
#         profil = Profil.objects.get(user=user_ob)
#         nbQusetion = profil.question_set.count
#         nbAnswer = profil.answer_set.count 
#         id_img = profil.photo_profil.image


#     try:
#         question = Question.objects.get(pk=question_id)
#         question.views += 1
#         question.save()
#         answer_list = question.answer_set.order_by('-votes')

#         paginator = Paginator(answer_list, 10)
#         page = request.GET.get('page')
#         try:
#             answers = paginator.page(page)
#         except PageNotAnInteger:
#             # If page is not an integer, deliver first page.
#             answers = paginator.page(1)
#         except EmptyPage:
#             # If page is out of range (e.g. 9999), deliver last page of results.
#             answers = paginator.page(paginator.num_pages)

#     except Question.DoesNotExist:
#         raise Http404("Question does not exist")

#     context = {'answers': answers, 'question': question }

#     context['categories']=categories
#     context['tags']=tags
#     context['count']=count
#     context['count_a']=count_a
#     context['noans']=dernier_noans_list
#     return render(request, 'qa/detail.html', context )


# def add_answer(request):

#     categories = Categorie.objects.all()
#     tags = Tag.objects.all()
#     count = Question.objects.count
#     count_a = Answer.objects.count
#     dernier_noans_list = Question.objects.order_by('-pub_date').filter(answer__isnull=True)[:10]

#     context = {}
#     context['categories']=categories
#     context['tags']=tags
#     context['count']=count
#     context['count_a']=count_a

#     if request.method == 'POST':
#         answer_text = request.POST['answer']
#         question_id = request.POST['question']
#         user_id = request.POST['user']

#         question = Question.objects.get(pk=question_id)
#         user_ob = User.objects.get(id=user_id)
#         user = Profil.objects.get(user=user_ob)
#         user.points += 5
#         user.save()

#         if answer_text.strip() == '':
#             return render(request, 'qa/answer.html', {'question': question, 'message': 'Empty'})

#         a = Answer()
#         pub_date = datetime.datetime.now()
#         a.answer_text = answer_text
#         a.question = question
#         a.user_data = user
#         a.pub_date = pub_date
#         a.save()

#         answer_list = question.answer_set.order_by('-votes')

#         paginator = Paginator(answer_list, 10)
#         page = request.GET.get('page')
#         try:
#             answers = paginator.page(page)
#         except PageNotAnInteger:
#             # If page is not an integer, deliver first page.
#             answers = paginator.page(1)
#         except EmptyPage:
#             # If page is out of range (e.g. 9999), deliver last page of results.
#             answers = paginator.page(paginator.num_pages)

#         # return render(request, 'qa/detail.html', {'question': question, 'answers': answers})
#         return redirect('qa:detail', question_id=question.id)

#     # return render(request, 'qa/detail.html', {'question': question})
#     return redirect('qa:detail', question_id=question.id)

# def comment(request, answer_id):

#     categories = Categorie.objects.all()
#     tags = Tag.objects.all()
#     count = Question.objects.count
#     count_a = Answer.objects.count

#     context = {}

#     context['categories']=categories
#     context['tags']=tags
#     context['count']=count
#     context['count_a']=count_a

#     if request.user.is_anonymous:
#         return HttpResponseRedirect("/accounts/login//")

#     if request.method == 'POST':
#         comment_text = request.POST['comment']
#         user_id = request.POST['user']
#         user_ob = User.objects.get(id=user_id)
#         user = Profil.objects.get(user=user_ob)
#         user.points += 1
#         user.save()

#         if comment_text.strip() == '':
#             return render(request, 'qa/comment.html', {'answer_id': answer_id, 'message': 'Empty'})

#         pub_date = datetime.datetime.now()
#         a = Answer.objects.get(pk=answer_id)
#         q_id = a.question_id
#         c = Comment()
#         c.answer = a
#         c.comment_text = comment_text
#         c.pub_date = pub_date
#         c.user_data = user
#         c.save()

#         try:
#             question = Question.objects.get(pk=q_id)
#             question.views += 1
#             question.save()
#             answer_list = question.answer_set.order_by('-votes')

#             paginator = Paginator(answer_list, 10)
#             page = request.GET.get('page')
#             try:
#                 answers = paginator.page(page)
#             except PageNotAnInteger:
#                 # If page is not an integer, deliver first page.
#                 answers = paginator.page(1)
#             except EmptyPage:
#                 # If page is out of range (e.g. 9999), deliver last page of results.
#                 answers = paginator.page(paginator.num_pages)

#         except Question.DoesNotExist:
#             raise Http404("Question does not exist")
#         return render(request, 'qa/detail.html', {'answers': answers, 'question': question}, )

#     template = loader.get_template('qa/comment.html')
#     context = {'answer_id': answer_id}
#     # return HttpResponse(template.render(context))
#     return HttpResponse(template.render(context, request))

# def vote(request, user_id, answer_id, question_id, op_code):

#     user_ob = User.objects.get(id=user_id)
#     user = Profil.objects.get(user=user_ob)
#     answer = Answer.objects.get(pk=answer_id)
#     question = Question.objects.get(pk=question_id)

#     answer_list = question.answer_set.order_by('-votes')

#     paginator = Paginator(answer_list, 10)
#     page = request.GET.get('page')
#     try:
#         answers = paginator.page(page)
#     except PageNotAnInteger:
#         # If page is not an integer, deliver first page.
#         answers = paginator.page(1)
#     except EmptyPage:
#         # If page is out of range (e.g. 9999), deliver last page of results.
#         answers = paginator.page(paginator.num_pages)

#     if Answer.objects.filter(id=answer_id, user_data=user).exists():
#         return render(request, 'qa/detail.html', {'question': question, 'answers': answers, 'message':"You cannot vote on your answer!"})

#     if Voter.objects.filter(answer_id=answer_id, user=user).exists():
#         return render(request, 'qa/detail.html', {'question': question, 'answers': answers, 'message':"You've already cast vote on this answer!"})

#     if op_code == '0':
#         answer.votes += 1
#         u = answer.user_data
#         u.points += 10
#         u.points += question.reward
#         u.save()
#     if op_code == '1':
#         answer.votes -= 1
#         u = answer.user_data
#         u.points -= 10
#         u.save()
#     answer.save()

#     answer_list = question.answer_set.order_by('-votes')

#     paginator = Paginator(answer_list, 10)
#     page = request.GET.get('page')
#     try:
#         answers = paginator.page(page)
#     except PageNotAnInteger:
#         # If page is not an integer, deliver first page.
#         answers = paginator.page(1)
#     except EmptyPage:
#         # If page is out of range (e.g. 9999), deliver last page of results.
#         answers = paginator.page(paginator.num_pages)

#     v = Voter()
#     v.user = user
#     v.answer = answer
#     v.save()

#     return render(request, 'qa/detail.html', {'question': question, 'answers': answers})


# def thumb(request, user_id, question_id, op_code):

#     user_ob = User.objects.get(id=user_id)
#     user = Profil.objects.get(user=user_ob)
#     question = Question.objects.get(pk=question_id)

#     answer_list = question.answer_set.order_by('-votes')

#     paginator = Paginator(answer_list, 10)
#     page = request.GET.get('page')
#     try:
#         answers = paginator.page(page)
#     except PageNotAnInteger:
#         # If page is not an integer, deliver first page.
#         answers = paginator.page(1)
#     except EmptyPage:
#         # If page is out of range (e.g. 9999), deliver last page of results.
#         answers = paginator.page(paginator.num_pages)

#     if QVoter.objects.filter(question_id=question_id, user=user).exists():
#         return render(request, 'qa/detail.html', {'question': question, 'answers': answers, 'message':"Vous avez déjà voté sur cette question!"})

#     if op_code == '0':
#         question.reward += 5
#         u = question.user_data
#         u.points += 5
#         u.save()
#     if op_code == '1':
#         question.reward -= 5
#         u = question.user_data
#         u.points -= 5
#         u.save()
#     question.save()

#     answer_list = question.answer_set.order_by('-votes')

#     paginator = Paginator(answer_list, 10)
#     page = request.GET.get('page')
#     try:
#         answers = paginator.page(page)
#     except PageNotAnInteger:
#         # If page is not an integer, deliver first page.
#         answers = paginator.page(1)
#     except EmptyPage:
#         # If page is out of range (e.g. 9999), deliver last page of results.
#         answers = paginator.page(paginator.num_pages)

#     v = QVoter()
#     v.user = user
#     v.question = question
#     v.save()

#     return render(request, 'qa/detail.html', {'question': question, 'answers': answers})

# def search(request):
#     if request.method == 'POST':
#         word = request.POST['query']
#         question_list = Question.objects.filter(question_text__contains=word)
#         paginator = Paginator(question_list, 10)
#         page = request.GET.get('page')
#         try:
#             questions = paginator.page(page)
#         except PageNotAnInteger:
#         # If page is not an integer, deliver first page.
#             questions = paginator.page(1)
#         except EmptyPage:
#         # If page is out of range (e.g. 9999), deliver last page of results.
#             questions = paginator.page(paginator.num_pages)

#         noans_list = Question.objects.order_by('-pub_date').filter(tags__slug__contains=word,answer__isnull=True)[:10]
#         top_questions = Question.objects.order_by('-reward').filter(tags__slug__contains=word,answer__isnull=True,reward__gte=1)[:10]
#         count = Question.objects.count
#         count_a = Answer.objects.count

#         template = loader.get_template('qa/index.html')
#         tags = Tag.objects.all()
#         context = {
#         'questions': questions,
#         'totalcount': count,
#         'anscount': count_a,
#         'noans': noans_list,
#         'reward': top_questions,
#         'tags' : tags,
#         }
#         return render(request , 'qa/index.html' , context)
#     # return HttpResponse(template.render(context))
#     # return HttpResponse(template.render(context, request))
#     return render(request , 'qa/index.html' , {})


# @login_required
# def updateq(request , question_id):
#     # template = loader.get_template('qa/add.html')
#     question = Question.objects.get(pk=question_id)
#     count = Question.objects.count
#     count_a = Answer.objects.count
#     dernier_noans_list = Question.objects.order_by('-pub_date').filter(answer__isnull=True)[:10]
#     tags = Tag.objects.all()

#     list_tags = question.tags.all()
#     form = QuestionForm(instance=question)
#     if request.user.is_anonymous == True:
#         return HttpResponseRedirect("/accounts/login/")
#         # return render(request, 'qa/login.html', locals())

#     if request.method == 'POST':
#         form = QuestionForm(request.method or None)
#         question_text = request.POST['question']
#         question_title = request.POST['titre']
#         categorie = request.POST['categorie']
#         tags_text = request.POST['tags']
#         user_id = request.POST['user']
#         user_ob = User.objects.get(id=user_id)
#         user = Profil.objects.get(user=user_ob)

#         if question_text.strip() == '':
#             return render(request, 'qa/updateq.html', {'message': 'Empty'})

#         pub_date = datetime.datetime.now()
#         question.question_text = question_text
#         question.question_title = question_title
#         question.pub_date = pub_date
#         question.user_data = user
#         question.categorie = Categorie.objects.get(id = categorie)
#         question.save()

#         if '' != tags_text:
#             tags = tags_text.split(',')
#             for tag in tags:
#                 if '' != tag:
#                     try:
#                         t = Tag.objects.get(slug=tag)
#                         question.tags.add(t)
#                     except Tag.DoesNotExist:
#                         t=Tag()
#                         t.slug = tag
#                         t.save()
#                         question.tags.add(t)

#         #send_mail('QA: Your Question has been Posted.', 'Thank you for posting the question, '+question_text+'. We will notify you once someone posts an answer.', 'admin@test.com', [request.user.email], fail_silently=False)

#         return HttpResponseRedirect('/qa')
#     # return HttpResponse(template.render(context))
#     # return render(request, 'qa/add.html', locals())
#     context = {
#         'count': count,
#         'count_a': count_a,
#         'tags' : tags,
#         'noans': dernier_noans_list,
#         'question':question,
#         'list_tags':list_tags,
#     }
#     context['form'] = form
#     return render(request, 'qa/updateq.html', context)


# def closequestion(request):
#     if request.method == 'POST':
#         action = request.POST['closequestion']
#         question_id = request.POST['question_id']
#         question = Question.objects.get(pk=question_id)
#         question.closed = action
#         question.save()

#         context = {
#             'question':question,
#             'close':question.closed
#         }
#     return render(request, 'qa/close.html', context)    



# def remplirSession():
#     categories = Categorie.objects.all()

#     count = Question.objects.count
#     count_a = Answer.objects.count

#     request.session['categories'] = categories
#     request.session['count_q'] = count
#     request.session['count_a'] = count_a


# def categorie(request):
#     # if request.method == 'POST':
#     cat = request.POST['categorie']
#     qst_categorie = Question.objects.filter(categorie =cat )
#     # latest_question_list = Question.objects.filter(tags__slug__contains=word)
#     paginator = Paginator(qst_categorie, 10)
#     page = request.GET.get('page')
#     try:
#         questions = paginator.page(page)
#     except PageNotAnInteger:
#     # If page is not an integer, deliver first page.
#         questions = paginator.page(1)
#     except EmptyPage:
#     # If page is out of range (e.g. 9999), deliver last page of results.
#         questions = paginator.page(paginator.num_pages)

#     latest_noans_list = Question.objects.order_by('-pub_date').filter(categorie =cat ,answer__isnull=True)[:10]
#     top_questions = Question.objects.order_by('-reward').filter(categorie =cat ,answer__isnull=True,reward__gte=1)[:10]
#     count = Question.objects.count
#     count_a = Answer.objects.count

#     template = loader.get_template('qa/index.html')
#     context = {
#         'questions': questions,
#         'totalcount': count,
#         'anscount': count_a,
#         'noans': latest_noans_list,
#         'reward': top_questions,
#     }    
#     # return HttpResponse(template.render(context))
#     return render(request, 'qa/index.html' , context)