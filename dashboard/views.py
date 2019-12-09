import json
import simplejson
from django.db import connection
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render


def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def dash(request):
    if request.is_ajax():
        print('------------------------------------ajax----------------------------------')
        list1 = []
        list2 = []
        graph_data = graph_data_fun()
        for emp in graph_data:
            list1.append(emp.get("title"))
            list2.append(emp.get("team_count"))
        for i in list2:
            if (i > 0):
                flag = 1
                break
            else:
                flag = 0
        if (flag == 0):
            dataall = manage_data(3)
            list1 = []
            list2 = []
            for emp in dataall:
                list1.append(emp.get("title"))
                list2.append(emp.get("team_count"))
            list2 = simplejson.dumps(list2, use_decimal=True)
            print('ajax', list1)
            print('ajax', list2)
            data1 = {'name': list1, 'data': list2}
            return HttpResponse(json.dumps(data1))
        else:
            data1 = {'name': list1, 'data': list2}
            return HttpResponse(json.dumps(data1))
    else:
        print('------------------------------------normal----------------------------------')
        list1 = []
        list2 = []
        graph_data = graph_data_fun()
        for emp in graph_data:
            list1.append(emp.get("title"))
            list2.append(emp.get("team_count"))
        for i in list2:
            if (i > 0):
                flag = 1
                break
            else:
                flag = 0
        if (flag == 0):
            dataall = manage_data(3)
            list1 = []
            list2 = []
            for emp in dataall:
                list1.append(emp.get("title"))
                list2.append(emp.get("team_count"))
            return render(request, 'html/dash.html', {'name': list1, 'data': list2})
        else:
            return render(request, 'html/dash.html', {'name': list1, 'data': list2})


def high(request):
    list3 = []
    with connection.cursor() as c2:
        c2.execute(
            "select distinct (team_id) from( select title,username,team_id,updated_by,team_count from (SELECT t.title,ur.username, 							  "
            "tem.team_id,ur.id updated_by,0 team_count from team_employee_map tem                                                                               "
            "JOIN teams t on t.id = tem.team_id and t.status=1                                                                                                  "
            "JOIN user ur ON ur.id=tem.user_id and ur.status !=2 and tem.status=1 group by title,username,team_id order by tem.team_id )dl                      "
            "WHERE updated_by NOT IN (select updated_by from(SELECT title, IFNULL(username,'TL') username,team_id,updated_by,                                   "
            "count(*) team_count FROM(                                                                                                                          "
            "SELECT t.title,ur.username,al.entity_id,al.created_at,IF((al.action REGEXP 'Submitted'),1,                                                         "
            "NULL) AS submission,al.updated_by,al.data,                                                                                                         "
            "tem.team_id FROM activity_log al JOIN team_employee_map tem                                                                                        "
            "JOIN teams t on t.id = tem.team_id and t.status=1                                                                                                  "
            "JOIN user ur ON ur.id=tem.user_id and ur.status !=2 WHERE                                                                                          "
            "al.entity_type='resume' AND al.is_status_updated=0                                                                                                 "
            "AND al.status=1 AND al.updated_by=tem.user_id and tem.status=1 )sub WHERE DATE_FORMAT(created_at,'%m/%e/%Y') = DATE_FORMAT(SYSDATE(),'%m/%e/%Y') "
            "GROUP BY username,team_id order by team_id)s2 order by updated_by)ORDER BY team_id)s2")
        pie_data = dictfetchall(c2)
    with connection.cursor() as c3:
        c3.execute(
            "SELECT title, IFNULL(username,'TL') username,avatar,team_id,updated_by,count(*) team_count FROM(                                                 "
            "SELECT t.title,ur.username,ur.avatar,al.entity_id,al.created_at,IF((al.action REGEXP 'Submitted'),1,                                              "
            "NULL) AS submission,al.updated_by,al.data,                                                                                                        "
            "tem.team_id FROM activity_log al JOIN team_employee_map tem                                                                                       "
            "JOIN teams t on t.id = tem.team_id and t.status=1                                                                                                 "
            "JOIN user ur ON ur.id=tem.user_id and ur.status !=2 WHERE                                                                                         "
            "al.entity_type='resume' AND al.is_status_updated=0                                                                                                "
            "AND al.status=1 AND al.updated_by=tem.user_id and tem.status=1 )sub WHERE submission=1 and  DATE_FORMAT(created_at,'%m/%e/%Y') = DATE_FORMAT(SYSDATE(),'%m/%e/%Y')  "
            "GROUP BY username,team_id                                                                                                                         "
            "UNION                                                                                                                                             "
            "select title,username,avatar,team_id,updated_by,team_count from (SELECT t.title,ur.username,ur.avatar,                                            "
            "tem.team_id,ur.id updated_by,0 team_count from team_employee_map tem                                                                              "
            "JOIN teams t on t.id = tem.team_id and t.status=1                                                                                                 "
            "JOIN user ur ON ur.id=tem.user_id and ur.status !=2 and tem.status=1 group by title,username,team_id order by tem.team_id )dl                     "
            "WHERE updated_by NOT IN (select updated_by from(SELECT title, IFNULL(username,'TL') username,avatar,team_id,updated_by,                           "
            "count(*) team_count FROM(                                                                                                                         "
            "SELECT t.title,ur.username,ur.avatar,al.entity_id,al.created_at,IF((al.action REGEXP 'Submitted'),1,                                              "
            "NULL) AS submission,al.updated_by,al.data,                                                                                                        "
            "tem.team_id FROM activity_log al JOIN team_employee_map tem                                                                                       "
            "JOIN teams t on t.id = tem.team_id and t.status=1                                                                                                 "
            "JOIN user ur ON ur.id=tem.user_id and ur.status !=2 WHERE                                                                                         "
            "al.entity_type='resume' AND al.is_status_updated=0                                                                                                "
            "AND al.status=1 AND al.updated_by=tem.user_id and tem.status=1 )sub WHERE submission=1 and DATE_FORMAT(created_at,'%m/%e/%Y') = DATE_FORMAT(SYSDATE(),'%m/%e/%Y')  "
            "GROUP BY username,team_id order by team_id)s2 order by updated_by)ORDER BY team_id                                                                ")
        pie_data1 = dictfetchall(c3)
        for emp in pie_data1:
            if (emp.get("team_count") > 0):
                flag = 1
                break;
            else:
                flag = 0
        print(flag)
        if (flag == 0):
            pie_data1 = ""
            pie_data1 = team_member_data(3)
    with connection.cursor() as c4:
        c4.execute(
            """SELECT username,avatar,updated_by,count(interview) AS interview,count(offers) AS offers,count(submission) AS submission,created_at FROM 
                (SELECT ur.username,ur.avatar,AL.entity_id, AL.updated_by,AL.action, AL.created_at, DATE_FORMAT(AL.created_at,'%u') AS week,
                DATE_FORMAT(AL.created_at,'%m')AS month,
                JSON_UNQUOTE(JSON_EXTRACT(AL.data,"$.resume_requirement_map_id")) AS entity_class,
                IF((AL.action REGEXP 'Interviewed|Interview Requested|Interview Accepted|Interview Rescheduled|Interview Completed|Phone Interview Requested|Phone Interview Accepted|Video Conference Interview Requested|Video Conference Interview Accepted|Onsite Interview Requested|Second Round Interview Requested|Second Round Interview Accepted' ),1, 0) AS interview,
                IF((AL.action REGEXP 'Submitted'),1, NULL) AS submission,
                IF((AL.action REGEXP 'Rejected|Rejected by MSP|Rejected by Manager|Offer Declined|Onboarding terminated|Backed Out|Offer Cancelled|Rejected After Interview|Removed'),1, NULL) AS backed,
                IF((AL.action LIKE "%Offer Requested%"),1, NULL) AS offers
                FROM activity_log AL 
                left join user ur on AL.updated_by = ur.id
                WHERE ((AL.entity_type='resume')
                AND (AL.company_id=1) 
                AND (AL.status=1) 
                AND (AL.is_status_updated=1))
                and AL.data != ''
                AND (AL.created_at between curdate() - INTERVAL DAYOFWEEK(curdate())+5 DAY
                AND  curdate() - INTERVAL DAYOFWEEK(curdate()) DAY))s1 WHERE offers>=1 GROUP BY updated_by LIMIT 1"""
            )
        weak_topper = dictfetchall(c4)
    return render(request, 'html/dash1.html',
                  {'pie_data1': pie_data1, 'pie_data': pie_data, 'weak_topper': weak_topper})


def manage_data(timeslot1):
    dataall = ""
    graph_data = ""
    list1 = []
    list2 = []
    with connection.cursor() as c:
        qry = """ SELECT title, IFNULL(username,'TL') username,team_id,updated_by,count(*)                                                               
             team_count FROM( SELECT                                                                                                                 
             t.title,ur.username,al.entity_id,al.created_at,IF((al.action REGEXP 'Submitted'),1,                                                     
             NULL) AS submission,al.updated_by,al.data,tem.team_id FROM activity_log al JOIN team_employee_map                                       
             tem  JOIN teams t on t.id = tem.team_id AND t.status=1 JOIN user ur ON ur.id=tem.user_id and ur.status !=2 WHERE                        
             al.entity_type='resume' AND al.is_status_updated=0 AND al.status=1 AND al.updated_by=tem.user_id  AND tem.status=1                      
             )sub WHERE submission=1 and  DATE_FORMAT(created_at,'%m/%e/%Y') = DATE_FORMAT(SYSDATE() - INTERVAL {timeslot} DAY,'%m/%e/%Y')GROUP BY team_id                           
             UNION SELECT title, '' username,team_id,'' updated_by ,sum(0) team_count FROM( SELECT t.title,                                          
             ur.username,al.entity_id,al.created_at,IF((al.action REGEXP 'Submitted'),                                                               
             1, NULL) AS submission,al.updated_by,al.data,tem.team_id FROM activity_log al JOIN team_employee_map                                    
             tem  JOIN teams t on t.id = tem.team_id AND t.status=1 JOIN user ur ON ur.id=tem.user_id and ur.status !=2 AND tem.status=1  )sub1 where submission=1 and 
             team_id NOT IN(SELECT                                                                                                                   
             team_id FROM( SELECT t.title,ur.username,al.entity_id,al.created_at,IF((al.action REGEXP                                                
             'Submitted'),1, NULL) AS submission,al.updated_by,al.data,                                                                              
             tem.team_id FROM activity_log al JOIN team_employee_map tem  JOIN teams t on t.id = tem.team_id AND t.status=1                          
             JOIN user ur ON ur.id=tem.user_id and ur.status !=2 WHERE                                                                               
             al.entity_type='resume' AND al.is_status_updated=0 AND al.status=1 AND al.updated_by=tem.user_id AND                                    
             DATE_FORMAT(al.created_at,'%m/%e/%Y') = DATE_FORMAT(SYSDATE() - INTERVAL {timeslot} DAY,'%m/%e/%Y') AND tem.status=1  )sub where submission=1  GROUP BY                    
             team_id)GROUP BY team_id order by team_id  """
        qry = qry.format(timeslot=timeslot1)
        c.execute(qry)
        graph_data = dictfetchall(c)
        for emp in graph_data:
            list1.append(emp.get("title"))
            list2.append(emp.get("team_count"))
        for i in list2:
            if (i > 0):
                flag = 1
                break
            else:
                flag = 0
        if (flag == 0):
            return manage_data(timeslot1 + 1)
        else:
            return graph_data


def graph_data_fun():
    graph_data = ""
    list1 = []
    list2 = []
    with connection.cursor() as c:
        c.execute(
            " SELECT title, IFNULL(username,'TL') username,team_id,updated_by,count(*)                                                                "
            " team_count FROM( SELECT                                                                                                                 "
            " t.title,ur.username,al.entity_id,al.created_at,IF((al.action REGEXP 'Submitted'),1,                                                     "
            " NULL) AS submission,al.updated_by,al.data,tem.team_id FROM activity_log al JOIN team_employee_map                                       "
            " tem  JOIN teams t on t.id = tem.team_id AND t.status=1 JOIN user ur ON ur.id=tem.user_id and ur.status !=2 WHERE                        "
            " al.entity_type='resume' AND al.is_status_updated=0 AND al.status=1 AND al.updated_by=tem.user_id  AND tem.status=1                      "
            " )sub WHERE submission=1 and  DATE_FORMAT(created_at,'%m/%e/%Y') = DATE_FORMAT(SYSDATE(),'%m/%e/%Y')GROUP BY team_id                                    "
            " UNION SELECT title, '' username,team_id,'' updated_by ,sum(0) team_count FROM( SELECT t.title,                                          "
            " ur.username,al.entity_id,al.created_at,IF((al.action REGEXP 'Submitted'),                                                               "
            " 1, NULL) AS submission,al.updated_by,al.data,tem.team_id FROM activity_log al JOIN team_employee_map                                    "
            " tem  JOIN teams t on t.id = tem.team_id AND t.status=1 JOIN user ur ON ur.id=tem.user_id and ur.status !=2 AND tem.status=1  )sub1 where submission=1 and "
            " team_id NOT IN(SELECT                                                                                                                   "
            " team_id FROM( SELECT t.title,ur.username,al.entity_id,al.created_at,IF((al.action REGEXP                                                "
            " 'Submitted'),1, NULL) AS submission,al.updated_by,al.data,                                                                              "
            " tem.team_id FROM activity_log al JOIN team_employee_map tem  JOIN teams t on t.id = tem.team_id AND t.status=1                          "
            " JOIN user ur ON ur.id=tem.user_id and ur.status !=2 WHERE                                                                               "
            " al.entity_type='resume' AND al.is_status_updated=0 AND al.status=1 AND al.updated_by=tem.user_id AND                                    "
            " DATE_FORMAT(al.created_at,'%m/%e/%Y') = DATE_FORMAT(SYSDATE(),'%m/%e/%Y') AND tem.status=1  )sub where submission=1  GROUP BY                             "
            " team_id)GROUP BY team_id order by team_id                                                                                               ")
        graph_data = dictfetchall(c)
    print(graph_data, 'graph function---------------------')
    return graph_data


def team_member_data(timeslot1):
    dataall = ""
    graph_data = ""
    list1 = []
    list2 = []
    with connection.cursor() as c:
        qry = """  SELECT title, IFNULL(username,'TL') username,avatar,team_id,updated_by,count(*) team_count FROM(                                                 
                 SELECT t.title,ur.username,ur.avatar,al.entity_id,al.created_at,IF((al.action REGEXP 'Submitted'),1,                                                      
                 NULL) AS submission,al.updated_by,al.data,                                                                                                        
                 tem.team_id FROM activity_log al JOIN team_employee_map tem                                                                                       
                 JOIN teams t on t.id = tem.team_id and t.status=1                                                                                                 
                 JOIN user ur ON ur.id=tem.user_id and ur.status !=2 WHERE                                                                                         
                 al.entity_type='resume' AND al.is_status_updated=0                                                                                                
                 AND al.status=1 AND al.updated_by=tem.user_id and tem.status=1 )sub WHERE submission=1 and  DATE_FORMAT(created_at,'%m/%e/%Y') = DATE_FORMAT(SYSDATE()- INTERVAL {timeslot} DAY,'%m/%e/%Y')  
                 GROUP BY username,team_id                                                                                                                         
                 UNION                                                                                                                                             
                 select title,username,avatar,team_id,updated_by,team_count from (SELECT t.title,ur.username,ur.avatar,                                                          
                 tem.team_id,ur.id updated_by,0 team_count from team_employee_map tem                                                                              
                 JOIN teams t on t.id = tem.team_id and t.status=1                                                                                                 
                 JOIN user ur ON ur.id=tem.user_id and ur.status !=2 and tem.status=1 group by title,username,team_id order by tem.team_id )dl                     
                 WHERE updated_by NOT IN (select updated_by from(SELECT title, IFNULL(username,'TL') username,avatar,team_id,updated_by,                                
                 count(*) team_count FROM(                                                                                                                         
                 SELECT t.title,ur.username,ur.avatar,al.entity_id,al.created_at,IF((al.action REGEXP 'Submitted'),1,                                                      
                 NULL) AS submission,al.updated_by,al.data,                                                                                                        
                 tem.team_id FROM activity_log al JOIN team_employee_map tem                                                                                       
                 JOIN teams t on t.id = tem.team_id and t.status=1                                                                                                 
                 JOIN user ur ON ur.id=tem.user_id and ur.status !=2 WHERE                                                                                         
                 al.entity_type='resume' AND al.is_status_updated=0                                                                                                
                 AND al.status=1 AND al.updated_by=tem.user_id and tem.status=1 )sub WHERE submission=1 and DATE_FORMAT(created_at,'%m/%e/%Y') = DATE_FORMAT(SYSDATE()- INTERVAL {timeslot} DAY,'%m/%e/%Y')  
                 GROUP BY username,team_id order by team_id)s2 order by updated_by)ORDER BY team_id                                                                 """
        qry = qry.format(timeslot=timeslot1)
        c.execute(qry)
        graph_data = dictfetchall(c)
        for emp in graph_data:
            if (emp.get("team_count") > 0):
                flag = 1
                break
            else:
                flag = 0
        if (flag == 0):
            return manage_data(timeslot1 + 1)
        else:
            return graph_data
