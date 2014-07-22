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

    def test_get_correct_content(self):
        url = 'http://www.chinaacc.com/zhucekuaijishi/mryl/wa2014072108403364856717.shtml'
        info = self.U._get_quest_content(url, datetime.date(2014, 7, 21))
        self.assertEqual(info['type'], u'单选题')
        self.assertEqual(len(info['options']), 4)

        url = 'http://www.chinaacc.com/zhucekuaijishi/mryl/wa2014072208473756677837.shtml'
        info = self.U._get_quest_content(url, datetime.date.today())
        self.assertEqual(info['type'], u'单选题')
        self.assertEqual(len(info['options']), 4)
        self.assertEqual(info['q_type'], 1)
        #self.assertEqual(info['title'], u'''甲公司为上市公司，所得税税率为25%，按净利润的10%提取盈余公积，2012年审核2011年报表的时候发现以下事项：

        #　　（1）2011年12月15日，甲公司购入500万元股票，作为可供出售金融资产。至年末尚未出售，12月末的收盘价为650万元。甲公司按其成本列报在资产负债表中。

        #　　（2）甲公司2011年1月1日支付3000万元取得丁公司80%股权。2011年丁公司实现净利润200万元，甲公司确认了投资收益160万元。假定甲公司和丁公司均属于居民企业。

        #　　则因上述事项而影响甲公司2011年盈余公积的金额为（　）。''')



if __name__ == '__main__':
    unittest.main()


