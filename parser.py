#!/usr/bin/env python
#-*- coding:utf-8 -*-

import mechanize
import re
from bs4 import BeautifulSoup as bs
import hashlib
from model import Quest
from traceback import print_exc
from urllib import urlopen
import json
from datetime import datetime, date
import logging
FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT, filename="./logs/missing.log")

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

class Parser(object):
    QUESTTYPE = {"1":{"showSerialNum":"一","viewTypeName":u"单选题","relOrder":1},"2":{"showSerialNum":"二","viewTypeName":u"多选题","relOrder":2},"4":{"showSerialNum":"三","viewTypeName":u"解答题","relOrder":4},"3":{"showSerialNum":"四","viewTypeName":u"判断题","relOrder":3},"5":{"showSerialNum":"五","viewTypeName":u"阅读理解","relOrder":5}}
    QUESTION_LIST = [{"questionID":11070411,"serialNum":1,"childQuesIDs":"","relOrder":2}]

    def courses_ids(self):
        return [272, 274, 273, 275, 276, 262]

    def courses(self):
        return {
                272: u"会计",
                274 : u"审计",
                273 : u"税法",
                275 : u"经济法",
                276: u"财务成本管理",
                262: u"公司战略与风险管理",
                }

    def url(self, courseid, data):
        if isinstance(data, str):
            questDay = data
        else:
            questDay = data.strftime("%Y-%m-%d")
        return "http://member.chinaacc.com/qzm/create/daytest/getQues4NoCache.shtm?Forum_id=%d&method=1&d=%s"%(courseid, questDay)


    def url_builder(self, courseid, data):
        base_url = self.url(courseid, data)
        try:
            page = bs(urlopen(base_url))
        except:
            logging.warn(base_url)
        return page

    def get_answer(self,page):
        # 正确的答案
        question_id_str = str(self.get_question_id(page))
        return json.loads(page.select("#qzUserAnsMapStr")[0].text)[question_id_str]["rightAnswer"]
    
    def get_answer_ary(self, page):
        return [i for i in self.get_answer(page)]

    def get_question_type(self, page):
        question_id_str = str(self.get_question_id(page))
        return json.loads(page.select("#qzUserAnsMapStr")[0].text)[question_id_str]["quesType"]

    def get_question_type_display(self, page):
        return self.QUESTTYPE[str(self.get_question_type(page))]["viewTypeName"]

    def get_jiexi(self, page):
        return page.select("#JX%s"%self.get_question_id(page))[0].text.strip().split('\r',1)[-1].strip()

    def get_question_content(self, page):
        return page.select("#fcontent_%d"%(self.get_question_id(page)))[0].text

    def get_question_map(self, page):
        all_options = {}
        if self.get_question_type(page) == 2: # multiselect
            choose_type = "checkbox"
        elif self.get_question_type(page) == 1:
            choose_type = "radio"
        options = page.select("[type=%s]"%choose_type)
        for option in options:
            labels = page.select("[for=%s]"%option.attrs["id"])
            all_options[option.attrs["value"]] =  labels[1].text.strip()
        return all_options

    def get_question_id(self, page):
        question_list = json.loads(page.select("#questionListStr")[0].text)
        return question_list[0]["questionID"]

    def __init__(self, date):
        self.date = date

    def get_each_question(self, start_index=0):
        for index, cid in enumerate(self.courses_ids()):
            if index >= start_index:
                self.load_page(cid)
                yield [self.to_json(self.page), index]


    def load_page(self, course_id):

        self.course_id = course_id

        self.base_url = self.url(course_id, self.date)
        self.page = self.url_builder(course_id, self.date)
        #self.inspect(self.page)


    def inspect(self,page):
        print self.get_question_type_display(page)
        print self.get_question_content(page)
        for name, value in self.get_question_map(page).iteritems():
            print "%s %s"%(name, value)

        print self.get_answer(page)
        print self.get_jiexi(page)

        print self.to_json(page)

    def to_json(self, page):
        if isinstance(self.date, date):
            day = self.date
        else:
            day = self.date.date()
        return {
                "uid": self.get_question_id(page),
                "title": self.courses()[self.course_id],
                "question":self.get_question_content(page),
                "answer" : self.get_answer_ary(page),
                "reason":self.get_jiexi(page),
                "link": self.base_url,
                "date": day,
                "type":self.get_question_type_display(page),
                "options" : self.get_question_map(page),
                }


        #self.br = mechanize.Browser()


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

    def get_missing_day_entrance(self):
        from datetime import date, timedelta
        today = date.today()
        latest_day = Quest.select().order_by(Quest.date.desc()).limit(1).get().date
        missing_dates = map(lambda d: d.strftime("%Y_%m_%d"), [latest_day + timedelta(i) for i in xrange(0, (today - latest_day).days)])
        print "missing_dates from %s to %s"%(latest_day, today)
        self.br.open(ROOT_URL)
        print missing_dates
        
        while missing_dates:
            for link in self.br.links(url_regex=r'^/zhucekuaijishi/mryl\S+.shtml$'):
                results = re.findall(ur"\w{2}(\d{4})(\d{2})(\d{2})",link.url)
                #results = re.findall(ur'^(\d{4}).+（(\d+).(\d+)）$', link.text.decode("gb2312"))
                if results:
                    year, month, day = results[0]
                    this_day = date(int(year), int(month), int(day))
                    print this_day
                    if this_day.strftime("%Y_%m_%d") in missing_dates:
                        print "got missing day %s"%this_day
                        quests = self.get_day_quests(link.absolute_url)
                        for l in quests:
                            self.get_quest_content(l, this_day)
                        missing_dates.remove(this_day.strftime("%Y_%m_%d"))
            # not found move to next page
            self._follow_next(self.br)

    def _follow_next(self, br):
        try:
            br.follow_link(text_regex=(u"下一页").encode("gb2312"))
        except:
            raise 

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

    def get_quest_content(self, link, date):
        info = self._get_quest_content(link, date)
        try:
            Quest.get(uid=info['uid'])
        except Quest.DoesNotExist:
            Quest.create(**info)

    def _get_quest_content(self, link, date):
        md5 = hashlib.md5(link).hexdigest()
        single = u"单选题"
        multip = u"多选题"
        date = date
        try:
            info = {'options': {}}
            info['link'] = link
            info['date'] = date
            info['uid'] = md5
            page = bs(urlopen(link))
            info['title'] = page.select(".news_content")[0].findChild().text
            print info['title']
            show_button = page.select('#fontzoom p input[type=button]')[0]
            all_node = show_button.parent.find_previous_siblings('p')
            all_node.reverse()
            # try to find the position of question type
            type_index = 0
            question_index = 0
            for index, node in enumerate(all_node):
                if re.match(ur'[\u3000]*[%s|%s][\u3000]*'%(single, multip), node.text):
                    type_index = index
                elif re.match(ur'[\u3000|\xa0|\s]*A[\u3001]([^\xa0]+)$', node.text):
                    question_index = index
                    break
            info['type'] = all_node[type_index].text.replace(u'\u3000', '')
            info['question'] = '\n'.join([node.text for node in all_node[type_index + 1:question_index]])
            for q in all_node[question_index:]:
                match = re.match(ur'[\u3000|\xa0|\s]*([A-Z]+)[\u3001]([^\xa0]+)[\xa0]*$', q.text)
                if match:
                    info['options'][match.groups()[0]] = match.groups()[1]
                    continue
            for p in page.select('#message p'):
                if u"答案解析" in p.text:
                    info['reason'] = p.text
                elif u"正确答案" in p.text:
                    info['answer'] = re.findall(r'[A-Za-z]', p.text)
            
            self.get_quest_type(info) # update correct quest type
            return info
        except Exception, e:
            print_exc()
            print e, link
            return info

            
            #info['date'] = info['date'].date()

if __name__ == "__main__":
    today = datetime.today()
    for question in Parser(today).get_each_question():
        print question

