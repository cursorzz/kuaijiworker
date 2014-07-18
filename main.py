import time
from parser import Updater
from model import mysql_db
import datetime
u = Updater()

while True:
    today = datetime.date.today()
    mysql_db.connect()
    u.get_today_quests(today)
    mysql_db.close()
    print 'get quest finish'
    time.sleep(60 * 60)
        
