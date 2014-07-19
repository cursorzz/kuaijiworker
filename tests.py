#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
"""
import unittest

from parser import Updater, JsonDict
import datetime

class ParseTest(unittest.TestCase):

    def setUp(self):
        self.U = Updater()

    def test_title_date_match(self):
        date  =datetime.date(2014, 07, 19)
        text = u'2014年注册会计师考试每日一练免费测试（07.19）'.encode('gb2312')
        self.assertEqual(self.U.is_right_quests_entrance(date, text), True)

    def test_get_right_quests_for_day(self):
        url = "http://www.chinaacc.com/zhucekuaijishi/mryl/wa2014071817063775440928.shtml"
        quests = self.U.get_day_quests(url)
        self.assertEqual(len(quests), 6)

    def test_json_dict_works(self):
        d = {
                'uid': '123123',
                'title': u'sfdasdfsdf'
                }
        json_dict = JsonDict(d)
        self.assertTrue(isinstance(json_dict, JsonDict))
        self.assertEqual(json_dict.uid, '123123')
        json_dict.content = 'sdfasdfsadf'
        self.assertEqual(json_dict.content, 'sdfasdfsadf')
        self.assertEqual(d['content'], 'sdfasdfsadf')



if __name__ == '__main__':
    unittest.main()


