import sys
from PySide6.QtWidgets import \
    QApplication, QMainWindow, QWidget, QTabWidget, QFileDialog, \
    QHBoxLayout, QVBoxLayout, QLabel, QProgressBar, QPlainTextEdit, \
    QComboBox, QDateEdit, QGroupBox, QCheckBox, QRadioButton, QLineEdit
from PySide6.QtCore import QDate, QThread, Signal, QObject
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np
import matplotlib.pyplot as plt
plt.rcParams['font.family'] = 'SimSun'
plt.rcParams['font.sans-serif'] = ['SimSun']
from datetime import datetime
from Manager import GROUPS, SUBJECTS, prepare

manager = None

class GradeManagePanel(QWidget):
    def __init__(self, gradeManager):
        super().__init__()
        layout = QVBoxLayout(self)
        
        startDateGroup = QGroupBox()
        startDateLayout = QVBoxLayout(startDateGroup)
        startDateLabel = QLabel("选择开始日期:")
        startDateEdit = QDateEdit(calendarPopup=True)
        startDateEdit.setDisplayFormat("yyyy-MM-dd")
        startDateEdit.dateChanged.connect(gradeManager.plot)
        startDateEdit.setDate(QDate(2020, 1, 1))
        startDateLayout.addWidget(startDateLabel)
        startDateLayout.addWidget(startDateEdit)
        startDateGroup.setMaximumHeight(80)
        layout.addWidget(startDateGroup)
        self.startDateEdit = startDateEdit

        endDateGroup = QGroupBox()
        endDateLayout = QVBoxLayout(endDateGroup)
        endDateLabel = QLabel("选择截止日期:")
        endDateEdit = QDateEdit(calendarPopup=True)
        endDateEdit.setDisplayFormat("yyyy-MM-dd")
        endDateEdit.dateChanged.connect(gradeManager.plot)
        endDateEdit.setDate(QDate(2025, 1, 1))
        endDateLayout.addWidget(endDateLabel)
        endDateLayout.addWidget(endDateEdit)
        endDateGroup.setMaximumHeight(80)
        layout.addWidget(endDateGroup)
        self.endDateEdit = endDateEdit

        subjectGroup = QGroupBox()
        subjectLayout = QVBoxLayout(subjectGroup)
        subjectLabel = QLabel("学科:")
        self.subjectComboBox = QComboBox(self)
        self.subjectComboBox.addItems(SUBJECTS)
        self.subjectComboBox.currentIndexChanged.connect(gradeManager.plot)
        subjectLayout.addWidget(subjectLabel)
        subjectLayout.addWidget(self.subjectComboBox)
        subjectGroup.setMaximumHeight(80)
        layout.addWidget(subjectGroup)

        indicatorGroup = QGroupBox()
        indicatorLayout = QVBoxLayout(indicatorGroup)
        indicatorLabel = QLabel("指标:")
        indicators = ["最高分", "最低分", "平均分", "上线率"]
        self.indicatorComboBox = QComboBox(self)
        self.indicatorComboBox.addItems(indicators)
        self.indicatorComboBox.currentIndexChanged.connect(gradeManager.plot)
        indicatorLayout.addWidget(indicatorLabel)
        indicatorLayout.addWidget(self.indicatorComboBox)
        indicatorGroup.setMaximumHeight(80)
        layout.addWidget(indicatorGroup)

        classGroup = QGroupBox()
        classLayout = QVBoxLayout(classGroup)
        classLabel = QLabel("班级列表:")
        classes = GROUPS
        classLayout.addWidget(classLabel)
        self.groups = []
        for item in classes:
            classCheckBox = QCheckBox(item)
            classCheckBox.clicked.connect(gradeManager.plot)
            classLayout.addWidget(classCheckBox)
            self.groups.append((item, classCheckBox))
            classCheckBox.setChecked(True)
        layout.addWidget(classGroup)
    
    def checkedGroups(self):
        answer = []
        for group in self.groups:
            if group[1].isChecked():
                answer.append(group[0])
        return answer

    def checkedSubject(self):
        return self.subjectComboBox.currentText()

    def checkedIndicator(self):
        return self.indicatorComboBox.currentText()

    def startDate(self):
        date = self.startDateEdit.date()
        return datetime(date.year(), date.month(), date.day())

    def endDate(self):
        date = self.endDateEdit.date()
        return datetime(date.year(), date.month(), date.day())

class GradeView(QWidget):
    finishInit = False

    def __init__(self):
        super().__init__()
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.panel = GradeManagePanel(self)
        layout = QHBoxLayout(self)
        
        layout.addWidget(self.panel)
        layout.addWidget(self.canvas)
        self.finishInit = True
        self.plot()

    def plot(self):
        if not self.finishInit:
            return
        self.figure.clear()
        ax = self.figure.add_subplot()
        groups = self.panel.checkedGroups()
        indicator = {
            "最高分": "max",
            "最低分": "min",
            "平均分": "average",
            "上线率": "rate"
        }[self.panel.checkedIndicator()]
        results, names = manager.queryIndicator(
            indicator,
            self.panel.startDate(),
            self.panel.endDate(),
            groups,
            self.panel.checkedSubject())
        ticks = [i for i in range(len(names))]
        for group in groups:
            print(ticks, results[group])
            ax.plot(ticks, results[group], marker="o", linestyle="-", label=group)
        ax.set_xticks(ticks, names)
        ax.legend()
        self.canvas.draw()

class StudentManagerPanel(QWidget):
    def __init__(self, studentManager):
        super().__init__()
        self.studentManager = studentManager
        layout = QVBoxLayout(self)
        
        startDateGroup = QGroupBox()
        startDateLayout = QVBoxLayout(startDateGroup)
        startDateLabel = QLabel("选择开始日期:")
        startDateEdit = QDateEdit(calendarPopup=True)
        startDateEdit.setDisplayFormat("yyyy-MM-dd")
        startDateEdit.dateChanged.connect(studentManager.plot)
        startDateEdit.setDate(QDate(2020, 1, 1))
        startDateLayout.addWidget(startDateLabel)
        startDateLayout.addWidget(startDateEdit)
        layout.addWidget(startDateGroup)
        self.startDateEdit = startDateEdit

        endDateGroup = QGroupBox()
        endDateLayout = QVBoxLayout(endDateGroup)
        endDateLabel = QLabel("选择截止日期:")
        endDateEdit = QDateEdit(calendarPopup=True)
        endDateEdit.setDisplayFormat("yyyy-MM-dd")
        endDateEdit.dateChanged.connect(studentManager.plot)
        endDateEdit.setDate(QDate(2025, 1, 1))
        endDateLayout.addWidget(endDateLabel)
        endDateLayout.addWidget(endDateEdit)
        layout.addWidget(endDateGroup)
        self.endDateEdit = endDateEdit

        classGroup = QGroupBox()
        classLayout = QVBoxLayout(classGroup)
        classLabel = QLabel("班级列表:")
        classes = GROUPS
        classLayout.addWidget(classLabel)
        self.groups = []
        for item in classes:
            classCheckBox = QRadioButton(item)
            classCheckBox.clicked.connect(studentManager.plot)
            classLayout.addWidget(classCheckBox)
            self.groups.append((item, classCheckBox))
        self.groups[0][1].setChecked(True)
        layout.addWidget(classGroup)

        subjectGroup = QGroupBox()
        subjectLayout = QVBoxLayout(subjectGroup)
        subjectLabel = QLabel("科目:")
        subjects = SUBJECTS
        subjectLayout.addWidget(subjectLabel)
        self.subjects = []
        for subject in subjects:
            subjectCheckBox = QRadioButton(subject)
            subjectCheckBox.clicked.connect(studentManager.plot)
            subjectLayout.addWidget(subjectCheckBox)
            self.subjects.append((subject, subjectCheckBox))
        self.subjects[0][1].setChecked(True)
        layout.addWidget(subjectGroup)

        searchGroup = QGroupBox()
        searchLayout = QVBoxLayout(searchGroup)
        searchLabel = QLabel("搜索学生:")
        searchBox = QLineEdit()
        searchBox.setPlaceholderText("输入学生名字")
        searchBox.textChanged.connect(self.onStudentNameChanged)
        searchLayout.addWidget(searchLabel)
        searchLayout.addWidget(searchBox)
        self.student = ""
        layout.addWidget(searchGroup)
    
    def onStudentNameChanged(self, text):
        self.student = text
        self.studentManager.plot()

    def studentName(self):
        return self.student

    def checkedGroup(self):
        for group in self.groups:
            if group[1].isChecked():
                return group[0]
        return None
    
    def checkedSubject(self):
        for subject in self.subjects:
            if subject[1].isChecked():
                return subject[0]
        return None
    
    def startDate(self):
        date = self.startDateEdit.date()
        return datetime(date.year(), date.month(), date.day())

    def endDate(self):
        date = self.endDateEdit.date()
        return datetime(date.year(), date.month(), date.day())

class StudentView(QWidget):
    finishInit = False

    def __init__(self):
        super().__init__()
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.panel = StudentManagerPanel(self)
        layout = QHBoxLayout(self)
        layout.addWidget(self.panel)
        layout.addWidget(self.canvas)

        self.finishInit = True

    def plot(self):
        if not self.finishInit:
            return
        self.figure.clear()
        ax = self.figure.add_subplot()

        results, names = manager.queryScore(
            self.panel.studentName(),
            self.panel.startDate(),
            self.panel.endDate(),
            self.panel.checkedGroup(),
            self.panel.checkedSubject())
        ticks = [i for i in range(len(names))]
        ax.plot(ticks, results, marker="o", linestyle="-")
        ax.set_xticks(ticks, names)
        self.canvas.draw()

class Worker(QThread):
    progressUpdate = Signal(int, str)
    progressEnd = Signal(int)

    def __init__(self, directory):
        super().__init__()
        self.directory = directory

    def run(self):
        global manager
        manager = prepare(self.directory, self.progressUpdate, self.progressEnd)
        

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("成绩可视化工具")
        self.resize(800, 300)
        self.progressBar = QProgressBar()
        self.logTextEdit = QPlainTextEdit()
        self.logTextEdit.setReadOnly(True)
        
        layout = QVBoxLayout()
        self.container = QWidget()
        self.container.setLayout(layout)
        layout.addWidget(self.progressBar)
        layout.addWidget(self.logTextEdit)
        self.setCentralWidget(self.container)

        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.Directory)
        directory = dialog.getExistingDirectory(self, "选择目录")
        self.workerThread = Worker(directory)
        self.workerThread.progressUpdate.connect(self.updateProgress)
        self.workerThread.progressEnd.connect(self.removeProgress)
    
    def updateProgress(self, value, message):
        self.progressBar.setValue(value)
        self.logTextEdit.appendPlainText(message)

    def removeProgress(self):
        self.progressBar.deleteLater()
        self.logTextEdit.deleteLater()
        self.createTabs()
    
    def createTabs(self):
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        tab1 = GradeView()
        tab3 = StudentView()

        self.tabs.addTab(tab1, "年级")
        self.tabs.addTab(tab3, "学生")



if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()
    try:
        window.workerThread.start()
    except Exception as e:
        print(e)
        window.updateProgress(100, str(e))

    sys.exit(app.exec())