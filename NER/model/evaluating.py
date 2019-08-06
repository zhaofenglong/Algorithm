#-*- coding:utf-8 -*-
"""
@file: evaluating.py
@version:v1.0
@software:PyCharm

@author: fenglong.zhao
@contact: fenglong.zhao@irootech.com
@time:2019-7-16
"""
from utils import flatten_lists
from collections import *


class Metrics:
    """
    用于评价模型，计算每个标签的精确率，召回率，F1分数
    """
    def __init__(self,golden_tags,predict_tags,remove_O=False):
        self.golden_tags = flatten_lists(golden_tags)
        self.predict_tags = flatten_lists(predict_tags)

        if remove_O:
            self._remove_Otags()

        #辅助计算的变量
        self.tagset = set(self.golden_tags)
        self.correct_tags_number = self.count_correct_tags()
        self.predict_tags_counter = Counter(self.predict_tags)
        self.golden_tags_counter = Counter(self.golden_tags)

        #计算精确率
        self.precision_scores = self.cal_precision()

        #计算召回率
        self.recall_scores = self.cal_recall()

        #计算F1分数
        self.f1_scores = self.cal_f1()

    def cal_f1(self):
        f1_scores = {}
        for tag in self.tagset:
            p,r = self.precision_scores[tag],self.recall_scores[tag]
            f1_scores[tag] = 2*p*r / (p+r+1e-10)
        return f1_scores

    def cal_recall(self):
        recall_scores = {}
        for tag in self.tagset:
            recall_scores[tag] = self.correct_tags_number.get(tag,0) / \
                self.golden_tags_counter[tag]
        return recall_scores

    def cal_precision(self):
        precision_scores = {}
        for tag in self.tagset:
            precision_scores[tag] = self.correct_tags_number.get(tag,0) / \
                self.predict_tags_counter[tag]

        return precision_scores

    def count_correct_tags(self):
        """计算每种标签预测正确的个数(对应精确率、召回率计算公式上的tp)，用于后面精确率以及召回率的计算"""
        correct_dict = {}
        for gold_tag,predict_tag in zip(self.golden_tags,self.predict_tags):
            if gold_tag == predict_tag:
                if gold_tag not in correct_dict:
                    correct_dict[gold_tag] = 1
                else:
                    correct_dict[gold_tag] += 1
        return correct_dict

    def _remove_Otags(self):
        length = len(self.golden_tags)
        O_tag_indices = [i for i in range(length)
                         if self.golden_tags[i] == 'O']

        self.golden_tags = [tag for i,tag in enumerate(self.golden_tags)
                            if i not in O_tag_indices]
        self.predict_tags = [tag for i,tag in enumerate(self.predict_tags)
                             if i not in O_tag_indices]
        print("原总标记数为{0}，移除了{1}个O标记，占比{2:.2f}%".format(
            length,
            len(O_tag_indices),
            len(O_tag_indices) / length * 100
        ))

    def report_scores(self):
        """将结果用表格的形式打印出来，像这个样子：

                              precision    recall  f1-score   support
                      B-LOC      0.775     0.757     0.766      1084
                      I-LOC      0.601     0.631     0.616       325
                     B-MISC      0.698     0.499     0.582       339
                     I-MISC      0.644     0.567     0.603       557
                      B-ORG      0.795     0.801     0.798      1400
                      I-ORG      0.831     0.773     0.801      1104
                      B-PER      0.812     0.876     0.843       735
                      I-PER      0.873     0.931     0.901       634

                  avg/total      0.779     0.764     0.770      6178
                """
        #打印表头
        header_format = '{:>9s}  {:>9} {:>9} {:>9} {:>9}'
        header = ['precision', 'recall', 'f1-score', 'support']
        print(header_format.format('',*header))

        row_format = '{:>9s}  {:>9.4f} {:>9.4f} {:>9.4f} {:>9}'
        # 打印每个标签的 精确率、召回率、f1分数
        for tag in self.tagset:
            print(row_format.format(
                tag,
                self.precision_scores[tag],
                self.recall_scores[tag],
                self.f1_scores[tag],
                self.golden_tags_counter[tag]
            ))

        #计算并打印平均值
        avg_metrics = self._cal_weighted_average()
        print(row_format.format(
            'avg/total',
            avg_metrics['precision'],
            avg_metrics['recall'],
            avg_metrics['f1_score'],
            len(self.golden_tags)
        ))

    def _cal_weighted_average(self):
        weighted_average = {}
        total = len(self.golden_tags)
        #计算weighted precision
        weighted_average['precision'] = 0.
        weighted_average['recall'] = 0.
        weighted_average['f1_score'] = 0.
        for tag in self.tagset:
            size = self.golden_tags_counter[tag]
            weighted_average['precision'] += self.precision_scores[tag] * size
            weighted_average['recall'] += self.recall_scores[tag] * size
            weighted_average['f1_score'] += self.f1_scores[tag] * size

        for metric in weighted_average.keys():
            weighted_average[metric] /= total

        return weighted_average

    def report_confusion_matrix(self):
        """计算混淆矩阵"""
        print("\nConfusion Matrix:")
        tag_list = list(self.tagset)
        #初始化混淆矩阵
        #matrix[i][j]表示第i个tag被模型预测成第j个tag的次数
        tag_size = len(tag_list)
        matrix = []
        for i in range(tag_size):
            matrix.append([0]*tag_size)

        #遍历tags列表
        for golden_tag,predict_tag in zip(self.golden_tags,self.predict_tags):
            try:
                row = tag_list.index(golden_tag)
                col = tag_list.index(predict_tag)
                matrix[row][col] += 1
            except ValueError:
                continue

        #输出矩阵
        row_format_ = '{:>7} ' * (tag_size + 1)
        print(row_format_.format('',*tag_list))
        for i, row in enumerate(matrix):
            print(row_format_.format(tag_list[i],*row))



