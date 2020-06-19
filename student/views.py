from django.shortcuts import render
from django.conf import settings

def home(request):
    name = request.session['userdata'].get('name')
    return render(request,"studhome.html",{"name":name})

def askquestion(request):    
    con = settings.CONNECTION()
    cr = con.cursor()
    id = request.session['userdata'].get('id')
    if request.method=='POST':
        qus = request.POST.get('qus')
        query = "insert into question(qus,ask_by) value('{0}',{1})".format(qus,id)                
        cr.execute(query)
        con.commit()        
    # get all question ..        
    query = "select * from question where ask_by={0} order by qid DESC".format(id)
    cr.execute(query)
    questions = cr.fetchall()

    finaldata = []
    for qus in questions:
        lst = list(qus)
        qid = lst[0]
        qu = "select ans,ans_date,name from answer,user where qus={0} and answer.ans_by=user.uid".format(qid)
        cr.execute(qu)
        a = cr.fetchall()
        lst.append(a)
        finaldata.append(lst)

    print(finaldata)        


    con.close()
    return render(request,"ask.html",{"questions":finaldata})