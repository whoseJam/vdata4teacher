import Util
from datetime import datetime
import pandas as pd
import numpy as np
from PySide6.QtCore import Signal

SUBJECTS = ["总分", "语文", "数学", "英语", "政治", "历史", "地理", "生物"]
GROUPS = []
PROGRESS_UPDATE = None
PROGRESS_COUNT = 0

EXAMS = []

class Manager:
    def queryIndicator(self, indicator, start, end, groups, subject):
        answer, names = {}, []
        for group in GROUPS:
            answer[group] = []
        for i in range(len(EXAMS)):
            exam = EXAMS[i]
            if exam["timestamp"] < start or exam["timestamp"] > end:
                continue
            names.append(exam["name"])
            for group in exam["tests"].keys():
                if group not in groups:
                    continue
                data = exam["tests"][group]
                value = 0
                if indicator == "max":
                    value = Util.max(data[subject].values)
                elif indicator == "min":
                    value = Util.min(data[subject].values)
                elif indicator == "average":
                    value = Util.average(data[subject].values)
                elif indicator == "rate":
                    value = Util.passRate(data[subject].values, exam["thresholds"][subject])
                answer[group].append(value)
        return answer, names
    
    def queryScore(self, studentName, start, end, group, subject):
        scores, names = [], []
        for i in range(len(EXAMS)):
            exam = EXAMS[i]
            if exam["timestamp"] < start or exam["timestamp"] > end:
                continue
            names.append(exam["name"])
            data = exam["tests"][group]
            score = data[data["姓名"] == studentName][subject]
            scores.append(score)
        return scores, names

def prepareExam(path: str):
    global readingDir
    readingDir = path

    data = pd.ExcelFile(path)
    sheetNames = data.sheet_names
    if "基础信息" not in sheetNames:
        raise Exception(f"基础信息在{path}这个excel中未找到，请检查相关文件的格式正确性")
    
    basic_, basic = pd.read_excel(path, sheet_name="基础信息", header=None), {}
    for idx, info in basic_.iterrows():
        basic[info[0]] = info[1]

    tests = []
    thresholds = { item: basic[f"{item}有效分"] for item in SUBJECTS }
    timestamp = pd.Timestamp(year=basic["考试时间Y"], month=basic["考试时间M"], day=basic["考试时间D"])
    groupNames = []
    for groupName in data.sheet_names:
        if groupName == "基础信息":
            continue
        oldGroupName = groupName
        groupName = groupName.strip()
        if "班" not in groupName:
            PROGRESS_UPDATE.emit(PROGRESS_COUNT, f"在{path}这个excel中发现了一个名为{groupName}的表格，跳过该表格")
            continue
        if groupName not in GROUPS:
            GROUPS.append(groupName)
        groupNames.append(oldGroupName)
    tests_, tests = pd.read_excel(path, sheet_name=groupNames, header=1), {}
    for k in tests_.keys():
        tests[k.strip()] = tests_[k]

    exam = {
        "name": basic["考试名称"],
        "timestamp": timestamp,
        "thresholds": thresholds,
        "tests": tests
    }

    EXAMS.append(exam)

def prepare(folderPath="./data", progressUpdate=None, progressEnd=None):
    # try:
    global PROGRESS_UPDATE, PROGRESS_COUNT
    PROGRESS_UPDATE = progressUpdate
    import os
    filePaths, exames = [], []
    for root, dirs, files in os.walk(folderPath):
        for file in files:
            filePath = os.path.join(root, file)
            filePaths.append(filePath)

    i, cnt = 0, len(filePaths) * 2
    for filePath in filePaths:
        i = i + 1
        PROGRESS_COUNT = 100.0 * i / cnt
        progressUpdate.emit(100.0 * i / cnt, f"开始处理文件 {filePath}")
        prepareExam(filePath)
        i = i + 1
        PROGRESS_COUNT = 100.0 * i / cnt
        progressUpdate.emit(100.0 * i / cnt, f"结束处理文件 {filePath}")
    EXAMS.sort(key=lambda x: x["timestamp"])
    progressEnd.emit(1)
    # except Exception as e:
    #     print(e)
    #     progressUpdate.emit(100, str(e))
    return Manager()