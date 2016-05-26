# coding:utf-8
# 爬虫分类与jimu 分类的匹配

import xlrd

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

# debug
try:
    from aragog.settings import CATEGORY_MATCH_XLS_FILE
    category_xls_file = CATEGORY_MATCH_XLS_FILE
except Exception:
    print 'cant get settings xls file'
    if True:
        category_xls_file = "/home/yzy/learn/lscrapy/aragog/tools/category/category_match_all_0.1.xls"
    else:
        raise Exception


def _get_list_2_category(sheet_name):
    # 两级原始的 category
    dp = xlrd.open_workbook(category_xls_file)
    table = dp.sheet_by_name(sheet_name)
    nrow = table.nrows

    dp_cate_one = []
    dp_cate_two = []
    yt_cate_first = []
    yt_cate_second = []
    yt_cate_third = []

    for i in range(1, nrow):
        dp_cate_one.append(table.cell(i, 0).value)
        dp_cate_two.append(table.cell(i, 1).value)
        yt_cate_first.append(table.cell(i, 2).value)
        yt_cate_second.append(table.cell(i, 3).value)
        yt_cate_third.append(table.cell(i, 4).value)
    res = [
        dp_cate_one,
        dp_cate_two,
        yt_cate_first,
        yt_cate_second,
        yt_cate_third,
        ]
    return res


def _get_list_3_category(sheet_name):
    # 3级原始的 category
    wb = xlrd.open_workbook(category_xls_file)
    table = wb.sheet_by_name(sheet_name)
    nrow = table.nrows

    wb_cate_one = []
    wb_cate_two = []
    wb_cate_three = []
    yt_cate_first = []
    yt_cate_second = []
    yt_cate_third = []

    for i in range(1, nrow):
        wb_cate_one.append(table.cell(i, 0).value)
        wb_cate_two.append(table.cell(i, 1).value)
        wb_cate_three.append(table.cell(i, 2).value)
        yt_cate_first.append(table.cell(i, 3).value)
        yt_cate_second.append(table.cell(i, 4).value)
        yt_cate_third.append(table.cell(i, 5).value)
    res = [
        wb_cate_one,
        wb_cate_two,
        wb_cate_three,
        yt_cate_first,
        yt_cate_second,
        yt_cate_third,
        ]
    return res


def _get_dianping_list():
    # 把xls 表中的每一列为一个list
    # 查找时根据爬到的second_cate_name 确定所在list的index
    # 若index 存在且唯一 则找到
    return _get_list_2_category('dianping')


def _get_wuba_list():
    return _get_list_3_category('wuba')


def _get_baixing_list():
    return _get_list_3_category('baixing')


def get_category_by_dianping(first_cate_name, second_cate_name, third_cate_name=''):
    # third_cate_name 不需要 此处仅为统一格式

    dp_cate_one = dianping_list[0]
    dp_cate_two = dianping_list[1]
    yt_cate_first = dianping_list[2]
    yt_cate_second = dianping_list[3]
    yt_cate_third = dianping_list[4]

    if first_cate_name is None or second_cate_name is None:
        return ['', '', '']
    if first_cate_name == '' or second_cate_name is '':
        return ['', '', '']

    second_indexs = []

    for i in range(len(dp_cate_two)):
        if dp_cate_two[i] == second_cate_name and dp_cate_one[i] == first_cate_name:
            second_indexs.append(i)

    if len(second_indexs) == 1:
        return [
            yt_cate_first[second_indexs[0]],
            yt_cate_second[second_indexs[0]],
            yt_cate_third[second_indexs[0]],
            ]
    else:
        return ['', '', '']



def get_category_by_wuba(first_cate_name, second_cate_name, third_cate_name):
    # 
    if first_cate_name is None or second_cate_name is None:
        return ['', '', '']
    if first_cate_name == '' or second_cate_name == '':
        return ['', '', '']

    wb_cate_one = wuba_list[0]
    wb_cate_two = wuba_list[1]
    wb_cate_three = wuba_list[2]
    yt_cate_first = wuba_list[3]
    yt_cate_second = wuba_list[4]
    yt_cate_third = wuba_list[5]

    third_indexes = []
    second_indexs = []
    first_indexs = []

    # 特殊情况 原分类没有第三级
    if third_cate_name is None or third_cate_name == "":
        for i in range(len(wb_cate_two)):
            r = wb_cate_two[i]
            if r == second_cate_name:
                second_indexs.append(i)
        for i in second_indexs:
            r = wb_cate_one[i]
            if r == first_cate_name:
                first_indexs.append(i)
        if len(first_indexs) == 1:
            return [
                yt_cate_first[first_indexs[0]],
                yt_cate_second[first_indexs[0]],
                yt_cate_third[first_indexs[0]],
            ]
        else:
            return ['', '', '']

    # 三个完全匹配
    for i in range(len(wb_cate_three)):
        if wb_cate_three[i] == third_cate_name and wb_cate_two[i] == second_cate_name and wb_cate_one[i] == first_cate_name:
            third_indexes.append(i)

    if len(third_indexes) == 1:
        return [
            yt_cate_first[third_indexes[0]],
            yt_cate_second[third_indexes[0]],
            yt_cate_third[third_indexes[0]],
            ]

    else:
        return ['', '', '']


def get_category_by_baixing(first_cate_name, second_cate_name, third_cate_name=''):
    #
    cate_one = baixing_list[0]
    cate_two = baixing_list[1]
    cate_three = baixing_list[2]

    yt_cate_first = baixing_list[3]
    yt_cate_second = baixing_list[4]
    yt_cate_third = baixing_list[5]

    if first_cate_name is None or second_cate_name is None:
        return ['', '', '']

    if first_cate_name == "" or second_cate_name == "":
        return ['', '', '']

    first_indexs = []

    if third_cate_name is None or third_cate_name == '':
        for i in range(len(cate_two)):
            if cate_two[i] == second_cate_name and cate_one == first_cate_name:
                first_indexs.append(i)
        if len(first_indexs) == 1:
            return [
                yt_cate_first[first_indexs[0]],
                yt_cate_second[first_indexs[0]],
                yt_cate_third[first_indexs[0]],
            ]
        else:
            return ['', '', '']

    else:
        # 匹配全部
        for i in range(len(cate_one)):
            if cate_one[i] == first_cate_name and cate_two[i] == second_cate_name and cate_three[i] == third_cate_name:
                first_indexs.append(i)
        if len(first_indexs) == 1:
            return [
                yt_cate_first[first_indexs[0]],
                yt_cate_second[first_indexs[0]],
                yt_cate_third[first_indexs[0]],
            ]
        else:
            return ['', '', '']


def test_wuba():
    res = get_category_by_wuba(u'休闲娱乐', u'运动健身', u'篮球场')
    assert(res == [u'休闲娱乐', u'运动健身', u'篮球场'])

    res = get_category_by_wuba(u'休闲娱乐', u'运动健身', u'篮球场123')
    assert(res == ['', '', ''])

    #res = get_category_by_wuba(u'休闲娱乐', u'运动健身', u'')
    #assert(res == [u'休闲娱乐', u'运动健身', ''])

    res = get_category_by_wuba(u'休闲娱乐', u'KTV', u'')
    assert(res == [u'休闲娱乐', u'KTV', ''])

    print 'wuba ok'


def test_dianping():
    res = get_category_by_dianping(u'亲子', u'幼儿教育')
    assert(res == [u'教育培训', u'婴幼儿教育', u''])

    res = get_category_by_dianping(u'亲子', u'')
    assert(res == [u'', u'', u''])

    print 'dianping ok'


def test_baixing():
    res = get_category_by_baixing(u'服务', u'婚庆服务', u'婚宴酒店')
    assert(res == [u'婚庆服务', u'婚庆', u'婚宴酒店'])

    res = get_category_by_baixing(u'服务', u'管道维修', u'管道疏通')
    assert(res == [u'家政服务', u'管道疏通', u''])

    print 'baixing ok'

dianping_list = _get_dianping_list()
wuba_list = _get_wuba_list()
baixing_list = _get_baixing_list()


if __name__ == '__main__':
    test_wuba()
    test_dianping()
    test_baixing()
