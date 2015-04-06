#!/usr/bin/env python
#-*- coding:utf-8 -*-
from peewee import *
try:
	import cPickle as pickle
except ImportError:
	import pickle
import datetime

#mysql_db = MySQLDatabase('XKhiXoNMpPmlvClmUico', user='aBv5vhN9Lggo58zURGFsHE56', passwd="FOnYOKWYnT92fT7VMcVWUfY6MGMfm1Su", host="sqld.duapp.com", port=4050)
mysql_db = MySQLDatabase('quest2', user='root', passwd="root")


class PickledObjectField(TextField):

    def replace_odd_string(self, picked):
        odds = '\xd7'
        return picked.replace(odds, 'x')

    def db_value(self, value):
        return str(self.replace_odd_string(pickle.dumps(value)))

    def python_value(self, value):
        return pickle.loads(str(value))

class Quest(Model):
    QUEST_TYPES = (
            (0, "未分类题目"),
            (1, u"会计"),
            (2, u"审计"),
            (3, u"税法"),
            (4, u"经济法"),
            (5, u"财务成本管理"),
            (6, u"公司战略与风险管理")
            )
    date = DateField()
    link = CharField(max_length=500)
    uid = CharField(max_length=200)
    title = TextField()
    type = CharField(max_length=200)
    question = TextField()
    options = PickledObjectField()
    answer = PickledObjectField()
    reason = TextField()
    q_type = IntegerField(default=0)

    class Meta:
        database = mysql_db
        db_table = 'index_quest'

    def __unicode__(self):
        return u"{date}<>{title}".format(date=self.date, title=self.title)
if __name__ == '__main__':
    a = {'uid': '879e5810ab446c349561143ff0f454e9', 'title': u'2014\u5e74\u6ce8\u518c\u4f1a\u8ba1\u5e08\u8003\u8bd5\u300a\u4f1a\u8ba1\u300b\u6bcf\u65e5\u4e00\u7ec3\uff1a\u4f1a\u8ba1\u4f30\u8ba1\u53ca\u5176\u53d8\u66f4', 'question': u'\u4e0b\u5217\u9879\u76ee\u4e2d\uff0c\u5c5e\u4e8e\u4f1a\u8ba1\u4f30\u8ba1\u53d8\u66f4\u7684\u662f\uff08\u3000\u3000\uff09\u3002', 'answer': [u'A'], 'reason': u'\u3000\u3000\u3010\u7b54\u6848\u89e3\u6790\u3011\u672c\u9898\u8003\u67e5\u7684\u77e5\u8bc6\u70b9\u662f\uff1a\u4f1a\u8ba1\u4f30\u8ba1\u53ca\u4f1a\u8ba1\u4f30\u8ba1\u53d8\u66f4\u3002', 'link': u'http://www.chinaacc.com/zhucekuaijishi/mryl/wa2014071508400750905235.shtml', 'date': datetime.date(2014, 7, 15), 'type': u'\u5355\u9009\u9898', 'options': {u'A': u'\u56fa\u5b9a\u8d44\u4ea7\u7684\u4f7f\u7528\u5e74\u9650\u548c\u51c0\u6b8b\u503c\u7684\u6539\u53d8', u'C': u'\u574f\u8d26\u635f\u5931\u7684\u6838\u7b97\u65b9\u6cd5\u7531\u76f4\u63a5\u8f6c\u9500\u6cd5\u6539\u4e3a\u5907\u62b5\u6cd5', u'B': u'\u4f01\u4e1a\u5916\u8d2d\u7684\u623f\u5c4b\u5efa\u7b51\u7269\u4e0d\u518d\u4e00\u5f8b\u786e\u5b9a\u4e3a\u56fa\u5b9a\u8d44\u4ea7\uff0c\u800c\u662f\u5bf9\u652f\u4ed8\u7684\u4ef7\u6b3e\u6309\u7167\u5408\u7406\u7684\u65b9\u6cd5\u5728\u571f\u5730\u548c\u5730\u4e0a\u5efa\u7b51\u7269\u4e4b\u95f4\u8fdb\u884c\u5206\u914d\uff0c\u5206\u522b\u786e\u5b9a\u65e0\u5f62\u8d44\u4ea7\u548c\u56fa\u5b9a\u8d44\u4ea7'}}
    print Quest.get_or_create(**a).id
