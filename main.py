import time
from parser import Updater
import datetime

while True:
    u = Updater()
    today = datetime.date.today()
    u.get_today_quests(today)
    print 'get quest finish'
    time.sleep(60 * 30)
        
