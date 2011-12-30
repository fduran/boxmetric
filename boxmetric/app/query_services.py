import os
from bson.code import Code
from pymongo import Connection, DESCENDING, ASCENDING

class EmailQueryServices(object):

    def __init__(self):
        mhost = os.environ.get('MONGO_SERVER')
        mport = int(os.environ.get('MONGO_PORT'))
        muser = os.environ.get('MONGO_USER')
        mpass = os.environ.get('MONGO_PASS')

        c = Connection(host = mhost, port = mport)
        db = c.gbox_1
        db.authenticate(muser,mpass)
    
        self.m = db.messages
        
    @staticmethod
    def teststaticmethod():
        return_val = "test"
        return return_val
    
    def testclassmethod(self):
        return self.member_val
        
    def most_received_emails(self):
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

        result = self.m.map_reduce(toAddrMap, addrReduce, "myresults")
        return result
        
    def most_sent(self):
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

        result = self.m.map_reduce(toAddrMap, addrReduce, "myresults")
        return result;
        
    def most_domains(self):
        aflist = self.m.group(key=["domainfrom",],condition=None,initial={"sum":0},reduce='function(doc,prev) { prev.sum++}')
        return aflist
        
    def dayofweek(self):
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

        result = self.m.map_reduce(map, reduce, "myresults")
        return result
        
    def month(self):
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

        result = self.m.map_reduce(map, reduce, "myresults")
        return result
        
    def year(self):
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

        result = self.m.map_reduce(map, reduce, "myresults")
        return result
        
    def monthyear(self):
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
        
        result = self.m.map_reduce(map, reduce, "myresults")
        return result
        
    def get_total_emails(self):
        total_emails = self.m.count()
        return total_emails
        
    def total_received(self):
        total_received = self.m.find( {"folders" : "\\Inbox" } ).count()
        return total_received
    
    def total_sent(self):
        total_sent = self.m.find( {"folders" : "\\Sent" } ).count()
        return total_sent
        
    def number_of_contacts(self):
        num_contacts = len(self.m.distinct('addresses.from.email'))
        return num_contacts
        
    def get_min_date(self):
        mindate = -1
        
        for doc in self.m.find().sort( "{date : -1}" ):
            if(doc['date'] < mindate or mindate == -1):
                mindate = doc['date']

        return mindate
        
    def get_max_date(self):
        maxdate = 0
        
        for doc in self.m.find().sort( "{date : -1}" ):
            if(doc['date'] > maxdate):
                maxdate = doc['date']

        return maxdate
        
    def hour(self):
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

        result = self.m.map_reduce(map, reduce, "myresults")
        return result;
        
    def contacts(self):
        flist = ['barack@whitehouse.gov', 'paul@ycombinator.com', 'angelina@jolie.com', 'jessica@alba.com', 'billgates@microsoft.com']
        return flist
        
    def activity(self):
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
    
        result = self.m.map_reduce(toAddrMap, addrReduce, "myresults", finalize=finalize )
        return result