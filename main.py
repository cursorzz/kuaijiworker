import time
from parser import Updater
from parser import Parser
from model import mysql_db, Quest
import datetime
u = Updater()

with open("save_point", "rw") as f:
    save_point = f.read()
if save_point:
    day, index = save_point.split()
    start_day = datetime.datetime.strptime( day, "%Y-%m-%d")
    index = int(index)
else:
    start_day = datetime.datetime.today()
    index = 0

for question in Parser(start_day).get_each_question(start_index=index):
    Quest.create(**question[0])
    with open("save_point", "w") as f:
        f.write("%s %s"%(start_day.strftime("%Y-%m-%d"), question[-1]))
start_day -= datetime.timedelta(days=1)
while True:
    print "start parse %s"%start_day
    for question in Parser(start_day).get_each_question():
        Quest.create(**question[0])
        with open("save_point", "w") as f:
            f.write("%s %s"%(start_day.strftime("%Y-%m-%d"), question[-1]))
    start_day -= datetime.timedelta(days=1)



if save_point_file.exist():
    start_day = datetime.str

datetime.datetime(2015, )
#while True:
    #today = datetime.date.today() - datetime.timedelta(days=0)
    #print "start todays job ", today
    #mysql_db.connect()
    ##u.get_today_quests(today)
    #u.get_missing_day_entrance()
    #mysql_db.close()
    #print 'get quest finish'
    #time.sleep(60 * 60)
        
