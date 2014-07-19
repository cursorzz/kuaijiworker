#!/usr/bin/env python
#-*- coding:utf-8 -*-

import mechanize
import re
from bs4 import BeautifulSoup as bs
import datetime
import hashlib
from model import Quest
from traceback import print_exc
from urllib import urlopen
#from multiprocessing import Process, Pool

ROOT_URL = 'http://www.chinaacc.com/zhucekuaijishi/mryl/qk/'
day_pattern = r'^http://.*/\D+(\d{8}).*'
date_fmt = "%Y%m%d"
class JsonDict(dict):
    def __init__(self, old_dict):
        self.old_dict = old_dict
        for key in old_dict:
            setattr(self, key, old_dict[key])

    def __setattr__(self, key, value):
        self[key] = value
        self.old_dict[key] = value

    def __getattr__(self, key):
        try:
            return self[key]
        except ValueError:
            return ''

prefix = 'parse:'
#HTTP Error 404: Not Found http://www.chinaacc.com/zhucekuaijishi/mryl/tu2014030108515426479505.shtml

class Updater(object):
    def __init__(self):
        self.br = mechanize.Browser()

    def get_today_quests(self, date):
        self.br.open(ROOT_URL)
        for link in self.br.links(url_regex=r'^/zhucekuaijishi/mryl\S+.shtml$'):
            if self.is_right_quests_entrance(date, link.text):
                print "the entrance is ", link.absolute_url
                quests = self.get_day_quests(link.absolute_url)
                for l in quests:
                    self.get_quest_content(l, date)
            #date_match = re.match(day_pattern, link.absolute_url).groups()[0] # 这种方法已经不能用了

            #if date_match == date.strftime('%Y%m%d'):
                #print link
                #self.get_day_quests(link)

    def is_right_quests_entrance(self, date, html_text):
        str_date = date.strftime('%m.%d')
        year = date.year
        try:
            html_text = html_text.decode('gb2312')
        except Exception:
            print_exc()
            return False
        result = re.match(ur'^%s.+（%s）$'%(year, str_date), html_text)
        if result:
            return True
        return False

    def old_get_day_quests(self, link):
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

    def get_day_quests(self, url):
        page = bs(urlopen(url))
        rough_result = page.select('#fontzoom p span a')
        result = []
        for r in rough_result:
            if u'《' in r.text and u'》' in r.text:
                result.append(r.attrs['href'])
        if len(result) > 6:
            print "this is wrong, get more than 6 quests"
            return []
        return result

    def get_quest_type(self, quest):
        if isinstance(quest, dict):
            quest = JsonDict(quest)
        title = quest.title
        quest.q_type = 0
        result = re.findall(ur'《(.+)》', title)
        if result:
            for key, value in Quest.QUEST_TYPES:
                if value == result[0]:
                    quest.q_type = key
        if quest.q_type == 0:
            print "[ERROR] cant find correct type for quest %s"%quest.uid
        if not isinstance(quest, JsonDict):
            quest.save()

    def get_quest_content(self, link, date, force=False):
        md5 = hashlib.md5(link).hexdigest()
        #date_match = re.match(day_pattern, link).groups()[0]
        #date = datetime.datetime.strptime(date_match, date_fmt)
        date = date
        try:
            info = {'options': {}}
            info['link'] = link
            info['date'] = date
            info['uid'] = md5
            page = bs(urlopen(link))
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
            
            self.get_quest_type(info) # update correct quest type
            
            #info['date'] = info['date'].date()
            try:
                Quest.get(uid=info['uid'])
            except Quest.DoesNotExist:
                Quest.create(**info)
        except Exception, e:
            print_exc()
            print e, link

