import pickle as pkl
from collections import defaultdict
import numpy as np
from random import shuffle
import os, gc
import sys
import time
import math
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)

from Utils.utils_siamese import read_pairs

att_folder = "E:/githubWorkSpace/KnowledgeAlignment/dataset/0_3/attr/"
data_folder = "E:/githubWorkSpace/KnowledgeAlignment/dataset/0_3/"
experiment_folder = "E:/githubWorkSpace/KnowledgeAlignment/dataset/"


def read_attr_triples(file_path, max_length):
    """ 读三元组, file_path = {[a, b, c] ...} 返回的是 [[a, int(b), c[:max_length]]]
        :param file_path : 路径
        :param max_length : 最大长度
        :return triples : 返回的三元组
    """
    triples = []
    with open(file_path, 'r', encoding='utf8') as f:
        for line in f.readlines():
            params = line.strip().split('\t')
            if len(params) != 3:
                print("wrong line" + line)
            # assert len(params) == 3
            h = params[0]
            a = int(params[1])
            v = params[2][:max_length]
            triples.append([h, a, v])
    return triples


def get_char_dict(trip1, trip2, w=False):
    """ 输入两个三元组，返回一个 dict, 如果 w = True 则写入文件里
        : prarams trip1, trip2 : 输入的三元组
        : param w : 是否写文件
        : return cd : 返回每个字符的排序，比如出现的字符数 {[a,12], [b,7], [c,10]} 返回就是 {[a, 0], [b, 2], [c, 1]}
    """
    char_dict = defaultdict(int)
    # 累加 trip.value 出现的字符数
    for t in trip1:
        for c in t[2]:
            char_dict[c] = char_dict[c] + 1
    for t in trip2:
        for c in t[2]:
            char_dict[c] = char_dict[c] + 1
    print(char_dict)
    print(len(char_dict))
    # 根据 dict 的 value 倒序
    l = sorted(char_dict.items(), key=lambda d: d[1], reverse=True)
    print(l)
    cd = {}
    for i in range(len(l)):
        cd[l[i][0]] = i
    print(cd)
    if w:
        with open(att_folder + "char_ids", 'w', encoding="utf-8")as f:
            for i in range(len(l)):
                f.write(l[i][0]+"\t"+str(i)+"\n")
    return cd


def _change_char_ids(trip, cd):
    """ 把 triples 的 value 换成 cd 里的下标
    """
    new_trip = []
    for item in trip:
        new_c = []
        for c in item[2]:
            new_c.append(cd[c])
        new_trip.append([item[0], item[1], new_c])
    return new_trip

def _display_dict_dis(d):
    """ 传进来一个 dict 然后打印 x y
        # x 表示 dict 的所有 key，且有序
        # y 表示 dict 的 value 累加，比如:
        # dict = {[5, 1], [6,10], [7, 7]}
        # x = [5, 6, 7], y = [1, 11, 18]
    """
    x, y = [], []
    keys = d.keys()
    keys = sorted(keys)
    for k in keys:
        last = 0
        if len(x) > 0:
            last = y[len(x) - 1]
        x.append(k)
        y.append(d[k] + last)
    paint_xy(x, y)


def read_attr_input(attr_folder, trip1, trip2, attr_value_length):
    """ 转换成新的 triples 返回
    """
    # 读两个文件
    triples_list1 = read_attr_triples(attr_folder + trip1, attr_value_length)
    triples_list2 = read_attr_triples(attr_folder + trip2, attr_value_length)
    # 拿到 cd
    cd = get_char_dict(triples_list1, triples_list2)
    # the number of char is 51

    # 通过 cd 转换成新的三元组
    triples_list1 = _change_char_ids(triples_list1, cd)
    triples_list2 = _change_char_ids(triples_list2, cd)

    # 两个实体计数 dict {[name, cnt]}
    ent_att_count1, ent_att_count2 = defaultdict(int), defaultdict(int)
    # XXX(zdh) 上面那个数量的数量，比如上面 {[a, 5], [b, 4], [c, 4]} => {[4, 2], [5, 1]}
    count_fre1, count_fre2 = defaultdict(int), defaultdict(int)
    for item in triples_list1:
        ent_att_count1[item[0]] += 1
    for item in triples_list2:
        ent_att_count2[item[0]] += 1
    for item in ent_att_count1.values():
        count_fre1[item] += 1
    for item in ent_att_count2.values():
        count_fre2[item] += 1
    # 打印
    _display_dict_dis(count_fre1)
    # KB1 att number per ent is 9
    # 长尾效应，有一些实体有大量属性，后续可以考虑预处理一下，将这些ent中重复的属性删除
    _display_dict_dis(count_fre2)
    # KB2 att number per ent is 54
    # 长尾效应，有一些实体有大量属性，后续可以考虑预处理一下，将这些ent中重复的属性删除
    return triples_list1, triples_list2

def _get_tdata(att_folder, attr_value_length):
    """ 传进来路径和 value 的限制最大长度
    """
    # 转换好的 triples
    trip1, trip2 = read_attr_input(att_folder, trip1="clean_new_filtered_att_triples_1", trip2="clean_new_filtered_att_triples_2", attr_value_length=attr_value_length)
    # 构造一个三元组 dict {[name, [(r1, v1), (r2, v2) ...]] ...}
    t1_dict, t2_dict = {}, {}
    for item in trip1:
        if item[0] in t1_dict:
            t1_dict[item[0]].append((item[1], item[2]))
        else:
            t1_dict[item[0]] = [(item[1], item[2])]
    for item in trip2:
        if item[0] in t2_dict:
            t2_dict[item[0]].append((item[1], item[2]))
        else:
            t2_dict[item[0]] = [(item[1], item[2])]

    # 字面意思，读出一个 pair
    # XXX(zdh) 数据是什么不知道 看下免得代码是个 name
    ref_ents = read_pairs(att_folder + "ref_ent_ids")
    sup_ents = read_pairs(att_folder + "sup_ent_ids")
    print(len(ref_ents))
    print(len(sup_ents))
    print(len(t1_dict), len(t2_dict))

    # 训练数据
    train_data, test_data = [], []
    neg_train_data = []
    for item_idx, item in enumerate(sup_ents):
        if item[0] in t1_dict and item[1] in t2_dict:
            # 各种填值
            train_data.append([t1_dict[item[0]], t2_dict[item[1]]])
            # 看不懂
            neg_kb2_item_ent = (item_idx + 1) % len(sup_ents)
            while(sup_ents[neg_kb2_item_ent][1] not in t2_dict):
                neg_kb2_item_ent = (neg_kb2_item_ent + 1) % len(sup_ents)
            neg_train_data.append([t1_dict[item[0]], t2_dict[sup_ents[neg_kb2_item_ent][1]]])
        else:
            print(item[0], item[1])
    for item in ref_ents:
        if item[0] in t1_dict and item[1] in t2_dict:
            test_data.append([t1_dict[item[0]], t2_dict[item[1]]])
        else:
            test_data.append([])
    print(len(train_data))
    print(len(test_data))
    print(train_data[:3])

    with open(att_folder + "cleaned_new_filtered_dbp_yago_att_sup_train_correct_test.pkl", "wb") as f:
        pkl.dump(train_data, f)
        pkl.dump(test_data, f)
        pkl.dump(neg_train_data, f)
    return train_data, test_data, neg_train_data


from Utils.utils_siamese import paint_xy
from collections import Counter


def check_att_num_length(att_folder, file_name="clean_new_filtered_att_triples_1"):
    dp_att_trip_file = att_folder + file_name
    with open(dp_att_trip_file, 'r', encoding="utf-8") as f:
        ent_att_count = defaultdict(int)
        att_val_len_count = defaultdict(int)
        for line_num, trip in enumerate(f.readlines()):
            att_sp = trip.split("\t")
            ent_att_count[att_sp[0].strip()] += 1
            att_val_len_count[len(att_sp[2].strip())] += 1
    att_num_dict = defaultdict(int)
    for k in ent_att_count.keys():
        att_num_dict[ent_att_count[k]] += 1

    # write_counter_2file(att_val_count, os.path.dirname(curPath) + "\dataset\dp_att_value_count.csv")
    def pxy(d):
        x, y = [], []
        keys = d.keys()
        keys = sorted(keys)
        print(keys)
        for k in keys:
            last = 0
            if len(x) > 0:
                last = y[len(x)-1]
            # print('k', last)
            x.append(k)
            y.append(d[k] + last)
        paint_xy(x, y)
    print("painting...")
    pxy(att_num_dict)
    pxy(att_val_len_count)

# step 2 : get the attr_num for each entity in knowledge graph and the att_kind_num is checked from the attr_id file.
# read_attr_input("E:/githubWorkSpace/KnowledgeAlignmentDataset/15kdata/db-wiki_V2/attrs/", "clean_new_filtered_att_triples_1", "clean_filtered_wiki_attr_triples", attr_value_length=40)

# step 3: get the input pickle for the attribution information.
_get_tdata(att_folder="E:/githubWorkSpace/KnowledgeAlignmentDataset/15kdata/db-wiki_V2/attrs/", attr_value_length=40)
