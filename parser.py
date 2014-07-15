#!/usr/bin/env python
#-*- coding:utf-8 -*-

import mechanize
import re
from bs4 import BeautifulSoup as bs
import datetime
import hashlib
from model import Quest
from traceback import print_exc
#from multiprocessing import Process, Pool

ROOT_URL = 'http://www.chinaacc.com/zhucekuaijishi/mryl/qk/'
day_pattern = r'^http://.*/\D+(\d{8}).*'
date_fmt = "%Y%m%d"


prefix = 'parse:'
#HTTP Error 404: Not Found http://www.chinaacc.com/zhucekuaijishi/mryl/tu2014030108515426479505.shtml

class Updater(object):
    def __init__(self):
        self.br = mechanize.Browser()

    def get_today_quests(self, date):
        self.br.open(ROOT_URL)
        for link in self.br.links(url_regex=r'^/zhucekuaijishi/mryl\S+.shtml$'):
            date_match = re.match(day_pattern, link.absolute_url).groups()[0]
            if date_match == date.strftime('%Y%m%d'):
                self.get_day_quests(link)

    def get_day_quests(self, link):
        url, absolute_url = link.url, link.absolute_url
        date_match = re.match(day_pattern, absolute_url).groups()[0]
        self.br.open(absolute_url) 
        quests = []
        for l in self.br.links(url_regex=r"^.+zhucekuaijishi/mryl/\w\w%s\d+.shtml$"%(date_match)):
            if 'target' in dict(l.attrs) and re.match(day_pattern, l.absolute_url).groups()[0] == date_match:
                quests.append(l.absolute_url)
        for link in quests:
            self.get_quest_content(link)
        return

    def get_quest_content(self, link, force=False):
        md5 = hashlib.md5(link).hexdigest()
        date_match = re.match(day_pattern, link).groups()[0]
        date = datetime.datetime.strptime(date_match, date_fmt)
        try:
            info = {'options': {}}
            info['link'] = link
            info['date'] = date
            info['uid'] = md5
            self.br.open(link)
            page = bs(self.br.response().read())
            info['title'] = page.select(".news_content")[0].findChild().text
            show_button = page.select('#fontzoom p input[type=button]')[0]
            quest = show_button.parent.find_previous_siblings('p')
            quest.reverse()
            for q in quest:
                if q.select('script'):
                    quest.remove(q)
            info['type'] = quest[0].text
            info['question'] = quest[1].text
            for q in quest[2:]:
                match = re.match(ur'[\u3000|\xa0|\s]*([A-Z]+)[\u3001]([^\xa0]+)$', q.text)
                if match:
                    info['options'][match.groups()[0]] = match.groups()[1]
                    continue
            for p in page.select('#message p'):
                if u"正确答案" in p.text:
                    info['answer'] = re.findall(r'[A-Za-z]', p.text)
                elif u"答案解析" in p.text:
                    info['reason'] = p.text
            
            info['date'] = info['date'].date()
            try:
                Quest.get(uid=info['uid'])
            except Quest.DoesNotExist:
                Quest.create(**info)
        except Exception, e:
            print_exc()
            print e, link

