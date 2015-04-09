#!/usr/bin/env python
# encoding: utf-8

from parser import Parser
from model import mysql_db, Quest
import datetime
import sys

def is_needs_update_for(date):
    return Quest.select().where(Quest.date==date).count() <= 0 

try:
    date = datetime.datetime.strptime(sys.argv[-1], "%Y_%m_%d").date()
except:
    date = datetime.date.today()

if is_needs_update_for(date):
    print 'ready to generate for %s'%date
    for result in Parser(date).get_each_question():
        print result[0]["title"]
        Quest.create(**result[0])

