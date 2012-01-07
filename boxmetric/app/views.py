import logging
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import Http404, HttpResponseRedirect, HttpResponse
from pymongo import DESCENDING, ASCENDING
from django.utils import simplejson
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.core.urlresolvers import reverse
from boxmetric.app.models import Contact, UserEvent
from django.forms import model_to_dict
from celery.decorators import task
from boxmetric.app.query_services import EmailQueryServices
from boxmetric.app.tasks import load_contacts
from boxmetric.app.forms import SignupForm


def index(request):
    return render_to_response('index.html', context_instance=RequestContext(request))


def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            # use gmail user name as our django user name (both are max 30 chars)
            # 1. create password, profile. 
            # (2. Email link with one-time auth token)
            # 3. hand off to gmail authorize
            return render_to_response('index.html', context_instance=RequestContext(request))
    else:
        form = SignupForm(initial={'gmail':'example@gmail.com'})
    return render_to_response('registration/signup.html', {'form': form, }, context_instance=RequestContext(request))


@login_required
def dashboard(request):
    if request.is_ajax and request.method == 'POST':
        if 'cid' in request.POST: 
            cid = int(request.POST.get('cid'))
            try:
                contact = Contact.objects.get(id=cid, user=request.user)
                cdict = model_to_dict(contact)
                answer = simplejson.dumps({'content': cdict,})
                return HttpResponse(answer, mimetype='application/json')
            except contact.DoesNotExist:
                raise Http404
        else:
            raise Http404
    else:       
        L = []
        for e in Contact.objects.filter(user=request.user).values('id', 'email'):
            e['value'] = e.pop('email')        
            L.append(e)
        for e in Contact.objects.filter(user=request.user).exclude(name='').values('id', 'name'):
            e['value'] = e.pop('name')
            L.append(e)
        csdata = simplejson.dumps(L)
        return render_to_response('dashboard.html', {'user': request.user, 'csdata': csdata,}, context_instance=RequestContext(request))


def login(request):
    from django.contrib.auth.views import login as auth_login
    login = auth_login(request)
    if request.user.is_authenticated():
        # testing celery, delete this:
        load_contacts.delay('some@example.com')
        user_event(request, u'LI')
    return login


def logout_page(request):
    user_event(request, u'LO')
    logout(request)
    return HttpResponseRedirect(reverse('boxmetric.app.views.index'))


def user_event(request, type):
    ip = request.META.get('REMOTE_ADDR', '')
    referer = request.META.get('HTTP_REFERER', '')[:128]
    agent = request.META.get('HTTP_USER_AGENT', '')[:256]
    user_event = UserEvent(user=request.user, type=type, ip=ip, referer=referer, agent=agent)
    user_event.save()
    return


def api(request, command):
    email_services = EmailQueryServices()

    flist = []
    aflist = []
    #total = '0'
    
    if command == 'most_received':
        result = email_services.most_received_emails()
        
        for doc in result.find().sort(u'value', DESCENDING).limit(5):
            flist.append(doc)
            
        return HttpResponse(simplejson.dumps(flist), mimetype='application/json')
        
    if command == 'most_sent':
        result = email_services.most_sent()
        
        for doc in result.find().sort(u'value', DESCENDING).limit(5):
            flist.append(doc)
        
        return HttpResponse(simplejson.dumps(flist), mimetype='application/json')
        
    if command == 'most_domains':
        aflist = email_services.most_domains()
        for doc in aflist[0:5]:
            flist.append(doc)
        
        return HttpResponse(simplejson.dumps(flist), mimetype='application/json')
    
    if command == 'dayofweek':
        result = email_services.dayofweek() 
        for doc in result.find().sort(u'_id', ASCENDING):
            flist.append(doc)
            
        return HttpResponse(simplejson.dumps(flist), mimetype='application/json')
    
    if command == 'month':
        result = email_services.month()
        for doc in result.find().sort(u'_id', ASCENDING):
            flist.append(doc)
        
        return HttpResponse(simplejson.dumps(flist), mimetype='application/json')
    
    if command == 'year':
        result = email_services.year()
        for doc in result.find().sort(u'_id', ASCENDING):
            flist.append(doc)
    
        return HttpResponse(simplejson.dumps(flist), mimetype='application/json')
    
    if command == 'monthyear':
        result = email_services.monthyear()
        for doc in result.find().sort(u'_id', ASCENDING):
            flist.append(doc)
    
        return HttpResponse(simplejson.dumps(flist), mimetype='application/json')
        
    if command == 'total':
        #total = email_services.get_total_emails()
        total_received = email_services.total_received()
        total_sent = email_services.total_sent()
        num_contacts = 0
        start_date = ''
        end_date = ''
        maxdate = email_services.get_max_date()
        mindate = email_services.get_min_date()
        
        start_date = str(mindate)
        end_date = str(maxdate)
        
        num_contacts = email_services.number_of_contacts()
        
        totalj = simplejson.dumps([{'total_received':total_received, 'total_sent':total_sent, 'num_contacts':num_contacts, 'start_date':start_date, 'end_date':end_date}])
        return HttpResponse(totalj, mimetype='application/json')
    
    # doesn't work, returns empty
    if command == 'hour':
        result = email_services.hour()
        for doc in result.find():
            flist.append(doc)
    
        return HttpResponse(simplejson.dumps(flist), mimetype='application/json')

    
    if command == 'contacts':
        flist = email_services.contacts()
        return HttpResponse(simplejson.dumps(flist), mimetype='application/json')
        
    if command == 'activity':
        result = email_services.activity()
        for doc in result.find():
            flist.append(doc)
    
        return HttpResponse(simplejson.dumps(flist), mimetype='application/json')
    
    
    return render_to_response('index.html', {'flist': flist}, context_instance=RequestContext(request))
    


