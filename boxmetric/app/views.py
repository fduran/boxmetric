import os
import logging
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import Http404, HttpResponseRedirect, HttpResponse
from pymongo import Connection, DESCENDING, ASCENDING
from bson.code import Code
from django.utils import simplejson
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.core.urlresolvers import reverse
import getmail


def index(request):
    #getmail.init()
    return render_to_response('index.html', context_instance=RequestContext(request))


@login_required
def dashboard(request):
    if request.is_ajax and request.method == 'POST':
        cid = int(request.POST.get('cid'))
        email = 'sdf@sadf.com'
        if cid == 1:
            contact = 'Mary jones one'
        else:
            contact = 'I dont know'
        answer = simplejson.dumps({'content': {'name':contact, 'email':email },})
        return HttpResponse(answer, mimetype='application/json')
    else:
        return render_to_response('dashboard.html', {'user': request.user,} , context_instance=RequestContext(request))


def logout_page(request):
    logout(request)
    return HttpResponseRedirect(reverse('boxmetric.app.views.index'))


def api(request, command):
    #c = Connection()
    mhost = os.environ.get('MONGO_SERVER')
    mport = int(os.environ.get('MONGO_PORT'))
    muser = os.environ.get('MONGO_USER')
    mpass = os.environ.get('MONGO_PASS')

    c = Connection(host = mhost, port = mport)
    db = c.gbox_1
    db.authenticate(muser,mpass)
    
    m = db.messages
    
    flist = []
    aflist = []
    total = '0'
    
    if command == 'most_received':
        toAddrMap = Code('''
        function toAddrMap() {
            var isfromsent = false;
            for (var i in this.folders) {
                    var folderName = this.folders[i];
                    if(folderName.indexOf('Sent') != -1) { 
                        isfromsent = true;
                    }
            }
            if(isfromsent == false) {
                emit( this.addresses.from.name, {count: 1} );
            }
        }
        ''')

        addrReduce = Code('''
        function addrReduce(key, values) {
            var result = {count: 0};

            values.forEach(function(value) {
                result.count += value.count;
            });

            return result;
        }
        ''')

        result = m.map_reduce(toAddrMap, addrReduce, "myresults")
        for doc in result.find().sort(u'value', DESCENDING).limit(5):
            flist.append(doc)
            
        return HttpResponse(simplejson.dumps(flist), mimetype='application/json')
        
    if command == 'most_sent':
        toAddrMap = Code('''
        function toAddrMap() {
            var isfromsent = false;
            for (var i in this.folders) {
                    var folderName = this.folders[i];
                    if(folderName.indexOf('Sent') != -1) { 
                        isfromsent = true;
                    }
            }
            if(isfromsent == true) {
                this.addresses.to.forEach(function(value) {
                    emit( value.email, {count: 1} );
                });
            }
        }
        ''')

        addrReduce = Code('''
        function addrReduce(key, values) {
            var result = {count: 0};

            values.forEach(function(value) {
                result.count += value.count;
            });

            return result;
        }
        ''')

        result = m.map_reduce(toAddrMap, addrReduce, "myresults")
        for doc in result.find().sort(u'value', DESCENDING).limit(5):
            flist.append(doc)
        
        return HttpResponse(simplejson.dumps(flist), mimetype='application/json')
        
    if command == 'most_domains':
        aflist = m.group(key=["domainfrom",],condition=None,initial={"sum":0},reduce='function(doc,prev) { prev.sum++}')
        for doc in aflist[0:5]:
            flist.append(doc)
        
        return HttpResponse(simplejson.dumps(flist), mimetype='application/json')
    
    if command == 'dayofweek':
        #flist = m.group(key=["dayofweek",],condition=None,initial={"sum":0},reduce='function(doc,prev) { prev.sum++}')
        map = Code("function() {"
            "var dayofweek = new Date();"
            "var date = new Date(this.date*1000);"
            "var sent = 0;"
            "var received = 0;"
            "for (var i in this.folders) {"
            "    var folderName = this.folders[i];"
            "    if(folderName.indexOf('Sent') == -1) { "
            "        received = 1;"
            "    } else { "
            "        sent = 1;"
            "    }"
            "}"
            "emit( date.getDay(), {countsent: sent, countreceived: received} );"
            "}")


        reduce = Code("function (key, values) {"
            "var result = {countsent: 0, countreceived: 0};"
            "values.forEach(function(value) {"
            "    result.countsent += value.countsent;"
            "    result.countreceived += value.countreceived;"
            "});"
            "return result;"
            "}")

        result = m.map_reduce(map, reduce, "myresults") 
        for doc in result.find().sort(u'_id', ASCENDING):
            flist.append(doc)
            
        return HttpResponse(simplejson.dumps(flist), mimetype='application/json')
    
    if command == 'month':
        map = Code("function() {"
        "var dayofweek = new Date();"
        "var date = new Date(this.date*1000);"
        "var sent = 0;"
        "var received = 0;"
        "for (var i in this.folders) {"
        "    var folderName = this.folders[i];"
        "    if(folderName.indexOf('Sent') == -1) { "
        "        received = 1;"
        "    } else { "
        "        sent = 1;"
        "    }"
        "}"
        "emit( date.getMonth()+1, {countsent: sent, countreceived: received} );"
        "}")


        reduce = Code("function (key, values) {"
        "var result = {countsent: 0, countreceived: 0};"
        "values.forEach(function(value) {"
        "    result.countsent += value.countsent;"
        "    result.countreceived += value.countreceived;"
        "});"
        "return result;"
        "}")

        result = m.map_reduce(map, reduce, "myresults")
        for doc in result.find().sort(u'_id', ASCENDING):
            flist.append(doc)
        
        return HttpResponse(simplejson.dumps(flist), mimetype='application/json')
    
    if command == 'year':
        map = Code("function() {"
        "var dayofweek = new Date();"
        "var date = new Date(this.date*1000);"
        "var sent = 0;"
        "var received = 0;"
        "for (var i in this.folders) {"
        "    var folderName = this.folders[i];"
        "    if(folderName.indexOf('Sent') == -1) { "
        "        received = 1;"
        "    } else { "
        "        sent = 1;"
        "    }"
        "}"
        "emit( date.getFullYear(), {countsent: sent, countreceived: received} );"
        "}")


        reduce = Code("function (key, values) {"
            "var result = {countsent: 0, countreceived: 0};"
            "values.forEach(function(value) {"
            "    result.countsent += value.countsent;"
            "    result.countreceived += value.countreceived;"
            "});"
            "return result;"
            "}")

        result = m.map_reduce(map, reduce, "myresults")
        for doc in result.find().sort(u'_id', ASCENDING):
            flist.append(doc)
    
        return HttpResponse(simplejson.dumps(flist), mimetype='application/json')
    
    if command == 'monthyear':
        map = Code('''
        function() {
            var date = new Date(this.date*1000);
            var sent = 0;
            var received = 0;
            for (var i in this.folders) {
                var folderName = this.folders[i];
                if(folderName.indexOf('Sent') == -1) { 
                    received = 1;
                } else { 
                    sent = 1;
                }
            }
            emit( date.getMonth()+1, {year: date.getFullYear(), countsent: sent, countreceived: received} );
            }
        ''')


        reduce = Code('''
        function (key, values) {
            var result = {year:0, countsent: 0, countreceived: 0};
            values.forEach(function(value) {
                result.countsent += value.countsent;
                result.countreceived += value.countreceived;
                result.year = value.year;
            });
            return result;
            }
        ''')
        
        result = m.map_reduce(map, reduce, "myresults")
        for doc in result.find().sort(u'_id', ASCENDING):
            flist.append(doc)
    
        return HttpResponse(simplejson.dumps(flist), mimetype='application/json')
        
    if command == 'total':
        total = m.count()
        total_received = m.find( {"folders" : "\\Inbox" } ).count()
        total_sent = m.find( {"folders" : "\\Sent" } ).count()
        num_contacts = 0
        start_date = ''
        end_date = ''
        maxdate = 0
        mindate = -1
        
        for doc in m.find().sort( "{date : -1}" ):
            if(doc['date'] > maxdate):
                maxdate = doc['date']
            if(doc['date'] < mindate or mindate == -1):
                mindate = doc['date']

        start_date = str(mindate)
        end_date = str(maxdate)
        
        num_contacts = len(m.distinct('addresses.from.email'))
        
        totalj = simplejson.dumps([{'total_received':total_received, 'total_sent':total_sent, 'num_contacts':num_contacts, 'start_date':start_date, 'end_date':end_date}])
        return HttpResponse(totalj, mimetype='application/json')
    
    # doesn't work, returns empty
    if command == 'hour':
        map = Code('''
        function() {
            var dayofweek = new Date();
            var date = new Date(this.date*1000);
            var sent = 0;
            var received = 0;
            for (var i in this.folders) {
                var folderName = this.folders[i];
                if(folderName.indexOf('Sent') == -1) { 
                    received = 1;
                } else { 
                    sent = 1;
                }
            }
            
            var weekdaysent=new Array(7);
            weekdaysent[0]=0;//"Sunday";
            weekdaysent[1]=0;//"Monday";
            weekdaysent[2]=0;//"Tuesday";
            weekdaysent[3]=0;//"Wednesday";
            weekdaysent[4]=0;//"Thursday";
            weekdaysent[5]=0;//"Friday";
            weekdaysent[6]=0;//"Saturday";
            
            var weekdayreceived=new Array(7);
            weekdayreceived[0]=0;//"Sunday";
            weekdayreceived[1]=0;//"Monday";
            weekdayreceived[2]=0;//"Tuesday";
            weekdayreceived[3]=0;//"Wednesday";
            weekdayreceived[4]=0;//"Thursday";
            weekdayreceived[5]=0;//"Friday";
            weekdayreceived[6]=0;//"Saturday";
            
            weekdaysent[date.getDay()] = sent;
            weekdayreceived[date.getDay()] = received;
            
            var curr_hour = date.getHours();
            var keyLabel = "";
            
            if(curr_hour >= 0 && curr_hour <=3)
                keyLabel = "0-3";
            if(curr_hour >= 4 && curr_hour <=7)
                keyLabel = "4-7";
            if(curr_hour >= 8 && curr_hour <= 11)
                keyLabel = "8-11";
            if(curr_hour >= 12 && curr_hour <= 15)
                keyLabel = "12-15";
            if(curr_hour >= 16 && curr_hour <= 19)
                keyLabel = "16-19";
            if(curr_hour >= 0 && curr_hour <=3)
                keyLabel = "20-23";
                
            emit( keyLabel, 
                {dayofweek: date.getDay(), 
                    details:{
                    sun: {countsent:weekdaysent[0],countreceived:weekdayreceived[0]},
                    mon: {countsent:weekdaysent[1],countreceived:weekdayreceived[1]}, 
                    tue: {countsent:weekdaysent[2],countreceived:weekdayreceived[2]}, 
                    wed: {countsent:weekdaysent[3],countreceived:weekdayreceived[3]}, 
                    thur:{countsent:weekdaysent[4],countreceived:weekdayreceived[4]}, 
                    fri: {countsent:weekdaysent[5],countreceived:weekdayreceived[5]}, 
                    sat: {countsent:weekdaysent[6],countreceived:weekdayreceived[6]}
                    }
            });
        }
        ''')

        reduce = Code('''
        function (key, values) {
            var _result = {dayofweek:'', countsent: 0, countreceived: 0};
            var result = {dayofweek: '', 
                details:{
                        sun: {countsent:0,countreceived:0},
                        mon: {countsent:0,countreceived:0},
                        tue: {countsent:0,countreceived:0},
                        wed: {countsent:0,countreceived:0},
                        thur:{countsent:0,countreceived:0},
                        fri: {countsent:0,countreceived:0},
                        sat: {countsent:0,countreceived:0}
                    }
            };
            
            values.forEach(function(value) {
                //result.countsent += value.countsent;
                //result.countreceived += value.countreceived;
                result.dayofweek = value.dayofweek;
                result.details.sun.countsent += value.details.sun.countsent;
                result.details.sun.countreceived += value.details.sun.countreceived;
                
                result.details.sun.countsent += value.details.sun.countsent;
                result.details.sun.countreceived += value.details.sun.countreceived;
                
                result.details.mon.countsent += value.details.mon.countsent;
                result.details.mon.countreceived += value.details.mon.countreceived;
                
                result.details.tue.countsent += value.details.tue.countsent;
                result.details.tue.countreceived += value.details.tue.countreceived;
                
                result.details.wed.countsent += value.details.wed.countsent;
                result.details.wed.countreceived += value.details.wed.countreceived;
                
                result.details.thur.countsent += value.details.thur.countsent;
                result.details.thur.countreceived += value.details.thur.countreceived;
                
                result.details.fri.countsent += value.details.fri.countsent;
                result.details.fri.countreceived += value.details.fri.countreceived;
                
                result.details.sat.countsent += value.details.sat.countsent;
                result.details.sat.countreceived += value.details.sat.countreceived;
            });
            return result;
        }
        ''')

        result = m.map_reduce(map, reduce, "myresults")
        for doc in result.find():
            flist.append(doc)
    
        return HttpResponse(simplejson.dumps(flist), mimetype='application/json')

    
    if command == 'contacts':
        #flist = m.distinct('addresses.from.email')
        flist = ['barack@whitehouse.gov', 'paul@ycombinator.com', 'angelina@jolie.com', 'jessica@alba.com', 'billgates@microsoft.com']
        return HttpResponse(simplejson.dumps(flist), mimetype='application/json')
        
    if command == 'activity':
        toAddrMap = Code('''
        function() {
            // get the datetime object from email's date
            var dayofweek = new Date();
            var date = new Date(this.date*1000);
            
            // find out if time is morning, day or evening
            var hour = date.getHours();
            var groupName = "";
            if(hour >= 0 && hour < 12) {
                groupName = "morning";
            }
            else if(hour >= 12 && hour < 17) {
                groupName = "day";
            }
            else if(hour >= 17 && hour < 24) {
                groupName = "evening";
            }
            
            this.total_count = 1;
            
            emit( groupName, {count: 1, total_count: this.total_count, avg: 0} );
        }
        ''')

        finalize = Code('''
        function(key, value) {

            value.avg = value.count / value.total_count;

            return value;
        }
        ''')

        addrReduce = Code('''
        function(key, values) {
            var result = {count: 0, total_count:0, avg: 0};

            values.forEach(function(value) {
                result.count += value.count;
                result.total_count += value.total_count;
            });

            return result;
        }
        ''')
    
        result = m.map_reduce(toAddrMap, addrReduce, "myresults", finalize=finalize )
        for doc in result.find():
            flist.append(doc)
    
        return HttpResponse(simplejson.dumps(flist), mimetype='application/json')
    
    
    return render_to_response('index.html', {'flist': flist}, context_instance=RequestContext(request))
    


