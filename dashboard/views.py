import json
import pandas as pd
import simplejson
from django.db import connection
from django.db.models import Max
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render

import datetime
from datetime import datetime
from django.utils.dateparse import parse_date

# Create your views here.
from dashboard.models import Teams
from dashboard.models import ActivityLog, User
from datetime import date
from collections import namedtuple


def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def dash(request):
    if request.is_ajax():
        max_id = ""
        graph_data = ""
        list1 = []
        list2 = []
        list3 = []
        list4 = []
        team_data = Teams.objects.filter(status=1)[:10].values_list('title', flat=True)
        activity_detail = ActivityLog.objects.filter(created_at__gt=date.today()).aggregate(Max('id')).values()
        activity_deta = ActivityLog.objects.filter(created_at__gt=date.today()).values('entity_id')
        with connection.cursor() as c:
            c.execute(
                " SELECT title, IFNULL(username,'TL') username,team_id,updated_by,count(*)                                                                "
            " team_count FROM( SELECT                                                                                                                 "
            " t.title,ur.username,al.entity_id,al.created_at,IF((al.action REGEXP 'Submitted'),1,                                                     "
            " NULL) AS submission,al.updated_by,al.data,tem.team_id FROM activity_log al JOIN team_employee_map                                       "
            " tem  JOIN teams t on t.id = tem.team_id AND t.status=1 JOIN user ur ON ur.id=tem.user_id and ur.status !=2 WHERE                        "
            " al.entity_type='resume' AND al.is_status_updated=0 AND al.status=1 AND al.updated_by=tem.user_id  AND tem.status=1                      "
            " )sub WHERE  DATE_FORMAT(created_at,'%m/%e/%Y') = DATE_FORMAT(curdate(),'%m/%e/%Y')GROUP BY team_id                                    "
            " UNION SELECT title, '' username,team_id,'' updated_by ,sum(0) team_count FROM( SELECT t.title,                                          "
            " ur.username,al.entity_id,al.created_at,IF((al.action REGEXP 'Submitted'),                                                               "
            " 1, NULL) AS submission,al.updated_by,al.data,tem.team_id FROM activity_log al JOIN team_employee_map                                    "
            " tem  JOIN teams t on t.id = tem.team_id AND t.status=1 JOIN user ur ON ur.id=tem.user_id and ur.status !=2 AND tem.status=1  )sub1 where"
            " team_id NOT IN(SELECT                                                                                                                   "
            " team_id FROM( SELECT t.title,ur.username,al.entity_id,al.created_at,IF((al.action REGEXP                                                "
            " 'Submitted'),1, NULL) AS submission,al.updated_by,al.data,                                                                              "
            " tem.team_id FROM activity_log al JOIN team_employee_map tem  JOIN teams t on t.id = tem.team_id AND t.status=1                          "
            " JOIN user ur ON ur.id=tem.user_id and ur.status !=2 WHERE                                                                               "
            " al.entity_type='resume' AND al.is_status_updated=0 AND al.status=1 AND al.updated_by=tem.user_id AND                                    "
            " DATE_FORMAT(al.created_at,'%m/%e/%Y') = DATE_FORMAT(curdate(),'%m/%e/%Y') AND tem.status=1  )sub GROUP BY                             "
            " team_id)GROUP BY team_id order by team_id                                                                                               ")

            graph_data = dictfetchall(c)
        for emp in graph_data:
            list1.append(emp.get("title"))
            list2.append(emp.get("team_count"))
        list2 = simplejson.dumps(list2, use_decimal=True)
        with connection.cursor() as c1:
            c1.execute("SELECT title, IFNULL(username,'TL') username,team_id,updated_by,count(*) team_count FROM( "
                       "SELECT t.title,ur.username,al.entity_id,al.created_at,IF((al.action REGEXP 'Submitted'),1, "
                       "NULL) AS submission,al.updated_by,al.data, "
                       "tem.team_id FROM activity_log al JOIN team_employee_map tem "
                       "LEFT JOIN teams t on t.id = tem.team_id LEFT JOIN user ur ON ur.id=tem.user_id WHERE "
                       "al.entity_type='resume' AND al.is_status_updated=0 "
                       "AND al.status=1 AND al.updated_by=tem.user_id )sub WHERE DATE_FORMAT(created_at,'%m/%e/%Y') = DATE_FORMAT(curdate(),'%m/%e/%Y')"
                       "GROUP BY username,team_id")
            graph_data1 = dictfetchall(c1)
            for emp1 in graph_data1:
                list3.append(emp1.get("username"))
                list4.append(emp1.get("team_count"))
            res = dict(zip(list3, list4))
            with connection.cursor() as c2:
                c2.execute(
                    "select distinct (team_id) from (SELECT title, IFNULL(username,'TL') username,team_id,updated_by,"
                    "count(*) team_count FROM( "
                    " SELECT t.title,ur.username,al.entity_id,al.created_at,IF((al.action REGEXP 'Submitted'),1, "
                    " NULL) AS submission,al.updated_by,al.data, "
                    " tem.team_id FROM activity_log al JOIN team_employee_map tem "
                    " LEFT JOIN teams t on t.id = tem.team_id LEFT JOIN user ur ON ur.id=tem.user_id WHERE "
                    " al.entity_type='resume' AND al.is_status_updated=0 "
                    " AND al.status=1 AND al.updated_by=tem.user_id )sub WHERE DATE_FORMAT(created_at,'%m/%e/%Y') = DATE_FORMAT(curdate(),'%m/%e/%Y')"
                    " GROUP BY username,team_id order by team_id)s1")
                pie_data = dictfetchall(c2)
                print("pie data", pie_data)
                with connection.cursor() as c3:
                    c3.execute(
                        "SELECT title, IFNULL(username,'TL') username,team_id,updated_by,"
                        "count(*) team_count FROM( "
                        " SELECT t.title,ur.username,al.entity_id,al.created_at,IF((al.action REGEXP 'Submitted'),1, "
                        " NULL) AS submission,al.updated_by,al.data, "
                        " tem.team_id FROM activity_log al JOIN team_employee_map tem "
                        " LEFT JOIN teams t on t.id = tem.team_id LEFT JOIN user ur ON ur.id=tem.user_id WHERE "
                        " al.entity_type='resume' AND al.is_status_updated=0 "
                        " AND al.status=1 AND al.updated_by=tem.user_id )sub WHERE DATE_FORMAT(created_at,'%m/%e/%Y') = DATE_FORMAT(curdate(),'%m/%e/%Y')"
                        " GROUP BY username,team_id order by team_id")
                    pie_data1 = dictfetchall(c3)
                with connection.cursor() as c4:
                    c4.execute(
                        " SELECT t.title,ur.username, "
                        " tem.team_id from team_employee_map tem "
                        " LEFT JOIN teams t on t.id = tem.team_id "
                        " LEFT JOIN user ur ON ur.id=tem.user_id group by title,username,team_id order by tem.team_id ")
                    legend_data = dictfetchall(c4)
                    print("legend_data", legend_data)
                    # for pie in pie_data1:
                    #     list5.append(pie.get("title"))
                    #     list6.append(pie.get("username"))
                    print("pie data1", pie_data1)
            list4 = simplejson.dumps(list4, use_decimal=True)
            table_data = {'submitted_by': list3, 'count': list4}
        data = {'name': list1, 'data': list2, 't_data': res, 'pie_data': pie_data, 'pie_data1': pie_data1,
                'legend_data': legend_data}
        return HttpResponse(json.dumps(data))
    list1 = []
    list2 = []
    list3 = []
    list4 = []
    list5 = []
    list6 = []
    with connection.cursor() as c:
        c.execute(
            " SELECT title, IFNULL(username,'TL') username,team_id,updated_by,count(*)                                                                "
            " team_count FROM( SELECT                                                                                                                 "
            " t.title,ur.username,al.entity_id,al.created_at,IF((al.action REGEXP 'Submitted'),1,                                                     "
            " NULL) AS submission,al.updated_by,al.data,tem.team_id FROM activity_log al JOIN team_employee_map                                       "
            " tem  JOIN teams t on t.id = tem.team_id AND t.status=1 JOIN user ur ON ur.id=tem.user_id and ur.status !=2 WHERE                        "
            " al.entity_type='resume' AND al.is_status_updated=0 AND al.status=1 AND al.updated_by=tem.user_id  AND tem.status=1                      "
            " )sub WHERE  DATE_FORMAT(created_at,'%m/%e/%Y') = DATE_FORMAT(curdate(),'%m/%e/%Y')GROUP BY team_id                                    "
            " UNION SELECT title, '' username,team_id,'' updated_by ,sum(0) team_count FROM( SELECT t.title,                                          "
            " ur.username,al.entity_id,al.created_at,IF((al.action REGEXP 'Submitted'),                                                               "
            " 1, NULL) AS submission,al.updated_by,al.data,tem.team_id FROM activity_log al JOIN team_employee_map                                    "
            " tem  JOIN teams t on t.id = tem.team_id AND t.status=1 JOIN user ur ON ur.id=tem.user_id and ur.status !=2 AND tem.status=1  )sub1 where"
            " DATE_FORMAT(created_at,'%m/%e/%Y') = DATE_FORMAT(curdate(),'%m/%e/%Y') and team_id NOT IN(SELECT                                                                                                                   "
            " team_id FROM( SELECT t.title,ur.username,al.entity_id,al.created_at,IF((al.action REGEXP                                                "
            " 'Submitted'),1, NULL) AS submission,al.updated_by,al.data,                                                                              "
            " tem.team_id FROM activity_log al JOIN team_employee_map tem  JOIN teams t on t.id = tem.team_id AND t.status=1                          "
            " JOIN user ur ON ur.id=tem.user_id and ur.status !=2 WHERE                                                                               "
            " al.entity_type='resume' AND al.is_status_updated=0 AND al.status=1 AND al.updated_by=tem.user_id AND                                    "
            " DATE_FORMAT(al.created_at,'%m/%e/%Y') = DATE_FORMAT(curdate(),'%m/%e/%Y') AND tem.status=1  )sub GROUP BY                             "
            " team_id)GROUP BY team_id order by team_id                                                                                              ")

        graph_data = dictfetchall(c)
    print(graph_data)

    for emp in graph_data:
        list1.append(emp.get("title"))
        list2.append(emp.get("team_count"))
    print(list1)

    return render(request, 'html/dash.html',
                  { 'name': list1, 'data': list2,})


def high(request):
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
              "AND al.status=1 AND al.updated_by=tem.user_id and tem.status=1 )sub WHERE DATE_FORMAT(created_at,'%m/%e/%Y') = DATE_FORMAT(curdate(),'%m/%e/%Y') "
              "GROUP BY username,team_id order by team_id)s2 order by updated_by)ORDER BY team_id)s2")
        pie_data = dictfetchall(c2)
        print("pie data ajax", pie_data)
    with connection.cursor() as c3:
        c3.execute(
                 "SELECT title, IFNULL(username,'TL') username,team_id,updated_by,count(*) team_count FROM(                                                          "
                  "SELECT t.title,ur.username,al.entity_id,al.created_at,IF((al.action REGEXP 'Submitted'),1,                                                        "
                  "NULL) AS submission,al.updated_by,al.data,                                                                                                        "
                  "tem.team_id FROM activity_log al JOIN team_employee_map tem                                                                                       "
                  "JOIN teams t on t.id = tem.team_id and t.status=1                                                                                                 "
                  "JOIN user ur ON ur.id=tem.user_id and ur.status !=2 WHERE                                                                                         "
                  "al.entity_type='resume' AND al.is_status_updated=0                                                                                                "
                  "AND al.status=1 AND al.updated_by=tem.user_id and tem.status=1 )sub WHERE DATE_FORMAT(created_at,'%m/%e/%Y') = DATE_FORMAT(curdate(),'%m/%e/%Y')"
                  "GROUP BY username,team_id                                                                                                                         "
                  "UNION                                                                                                                                             "
                  "select title,username,team_id,updated_by,team_count from (SELECT t.title,ur.username,                                                             "
                  "tem.team_id,ur.id updated_by,0 team_count from team_employee_map tem                                                                              "
                  "JOIN teams t on t.id = tem.team_id and t.status=1                                                                                                 "
                  "JOIN user ur ON ur.id=tem.user_id and ur.status !=2 and tem.status=1 group by title,username,team_id order by tem.team_id )dl                     "
                  "WHERE updated_by NOT IN (select updated_by from(SELECT title, IFNULL(username,'TL') username,team_id,updated_by,                                  "
                  "count(*) team_count FROM(                                                                                                                         "
                  "SELECT t.title,ur.username,al.entity_id,al.created_at,IF((al.action REGEXP 'Submitted'),1,                                                        "
                  "NULL) AS submission,al.updated_by,al.data,                                                                                                        "
                  "tem.team_id FROM activity_log al JOIN team_employee_map tem                                                                                       "
                  "JOIN teams t on t.id = tem.team_id and t.status=1                                                                                                 "
                  "JOIN user ur ON ur.id=tem.user_id and ur.status !=2 WHERE                                                                                         "
                  "al.entity_type='resume' AND al.is_status_updated=0                                                                                                "
                  "AND al.status=1 AND al.updated_by=tem.user_id and tem.status=1 )sub WHERE DATE_FORMAT(created_at,'%m/%e/%Y') = DATE_FORMAT(curdate(),'%m/%e/%Y')"
                  "GROUP BY username,team_id order by team_id)s2 order by updated_by)ORDER BY team_id                                                                ")
        pie_data1 = dictfetchall(c3)
        print("pie data 1", pie_data1)
    with connection.cursor() as c3:
        c3.execute("SELECT * FROM (SELECT ur.username,AL.entity_id, AL.updated_by,AL.action, AL.created_at, DATE_FORMAT(AL.created_at,'%u') AS week, "
                    "DATE_FORMAT(AL.created_at,'%m')AS month, "
                    "IF((AL.action REGEXP 'Interviewed|Interview Requested|Interview Accepted|Interview Rescheduled|Interview Completed|Phone Interview Requested|Phone Interview Accepted|Video Conference Interview Requested|Video Conference Interview Accepted|Onsite Interview Requested|Second Round Interview Requested|Second Round Interview Accepted' ),1, 0) AS interview, "
                    "IF((AL.action REGEXP 'Submitted'),1, 0) AS submission, "
                    "IF((AL.action REGEXP 'Rejected|Rejected by MSP|Rejected by Manager|Offer Declined|Onboarding terminated|Backed Out|Offer Cancelled|Rejected After Interview|Removed'),1, NULL) AS backed, "
                    "IF((AL.action LIKE '%Offer Accepted from requirement%'),1, NULL) AS offers "
                    "FROM activity_log AL  "
                    "left join user ur on AL.updated_by = ur.id "
                    "WHERE ((AL.entity_type='resume') "
                    "AND (AL.company_id=1)  "
                    "AND (AL.status=1) "
                    "AND (AL.is_status_updated=1)) "
                    "and AL.data != '' "
                    "AND (AL.created_at between curdate() - INTERVAL DAYOFWEEK(curdate())+5 DAY "
                    "AND  curdate() - INTERVAL DAYOFWEEK(curdate()) DAY))s1 WHERE offers=1 LIMIT 1 ")
        weak_topper = dictfetchall(c3)
        print("performer of the week", weak_topper)
    return render(request, 'html/dash1.html', {'pie_data1': pie_data1, 'pie_data': pie_data,'weak_topper':weak_topper})

