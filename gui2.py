# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'gui2ui.ui'
##
## Created by: Qt User Interface Compiler version 6.5.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QFrame, QGridLayout, QLabel,
    QMainWindow, QPushButton, QScrollBar, QSizePolicy,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1280, 720)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.buttons_frame = QFrame(self.centralwidget)
        self.buttons_frame.setObjectName(u"buttons_frame")
        self.buttons_frame.setGeometry(QRect(0, 10, 320, 700))
        self.buttons_frame.setFrameShape(QFrame.StyledPanel)
        self.buttons_frame.setFrameShadow(QFrame.Raised)
        self.layoutWidget = QWidget(self.buttons_frame)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.layoutWidget.setGeometry(QRect(0, 0, 321, 701))
        self.gridLayout = QGridLayout(self.layoutWidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(5, 5, 5, 5)
        self.weight_button = QPushButton(self.layoutWidget)
        self.weight_button.setObjectName(u"weight_button")

        self.gridLayout.addWidget(self.weight_button, 0, 0, 1, 1)

        self.force_val_label = QLabel(self.layoutWidget)
        self.force_val_label.setObjectName(u"force_val_label")

        self.gridLayout.addWidget(self.force_val_label, 3, 1, 1, 1)

        self.start_button = QPushButton(self.layoutWidget)
        self.start_button.setObjectName(u"start_button")
        self.start_button.setEnabled(True)

        self.gridLayout.addWidget(self.start_button, 2, 0, 1, 1)

        self.m1_val_label = QLabel(self.layoutWidget)
        self.m1_val_label.setObjectName(u"m1_val_label")

        self.gridLayout.addWidget(self.m1_val_label, 4, 1, 1, 1)

        self.force_label = QLabel(self.layoutWidget)
        self.force_label.setObjectName(u"force_label")

        self.gridLayout.addWidget(self.force_label, 3, 0, 1, 1)

        self.motor4_label = QLabel(self.layoutWidget)
        self.motor4_label.setObjectName(u"motor4_label")

        self.gridLayout.addWidget(self.motor4_label, 7, 0, 1, 1)

        self.m4_val_label = QLabel(self.layoutWidget)
        self.m4_val_label.setObjectName(u"m4_val_label")

        self.gridLayout.addWidget(self.m4_val_label, 7, 1, 1, 1)

        self.time_val_label = QLabel(self.layoutWidget)
        self.time_val_label.setObjectName(u"time_val_label")

        self.gridLayout.addWidget(self.time_val_label, 11, 1, 1, 1)

        self.weight_val_label = QLabel(self.layoutWidget)
        self.weight_val_label.setObjectName(u"weight_val_label")

        self.gridLayout.addWidget(self.weight_val_label, 0, 1, 1, 1)

        self.time_label = QLabel(self.layoutWidget)
        self.time_label.setObjectName(u"time_label")

        self.gridLayout.addWidget(self.time_label, 11, 0, 1, 1)

        self.motor1_label_2 = QLabel(self.layoutWidget)
        self.motor1_label_2.setObjectName(u"motor1_label_2")

        self.gridLayout.addWidget(self.motor1_label_2, 5, 0, 1, 1)

        self.pitch_label = QLabel(self.layoutWidget)
        self.pitch_label.setObjectName(u"pitch_label")

        self.gridLayout.addWidget(self.pitch_label, 9, 0, 1, 1)

        self.pushButton = QPushButton(self.layoutWidget)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setEnabled(False)

        self.gridLayout.addWidget(self.pushButton, 12, 0, 1, 2)

        self.stop_button = QPushButton(self.layoutWidget)
        self.stop_button.setObjectName(u"stop_button")

        self.gridLayout.addWidget(self.stop_button, 2, 1, 1, 1)

        self.tar_button = QPushButton(self.layoutWidget)
        self.tar_button.setObjectName(u"tar_button")

        self.gridLayout.addWidget(self.tar_button, 1, 0, 1, 2)

        self.m2_val_label = QLabel(self.layoutWidget)
        self.m2_val_label.setObjectName(u"m2_val_label")

        self.gridLayout.addWidget(self.m2_val_label, 5, 1, 1, 1)

        self.motor1_label = QLabel(self.layoutWidget)
        self.motor1_label.setObjectName(u"motor1_label")

        self.gridLayout.addWidget(self.motor1_label, 4, 0, 1, 1)

        self.m3_val_label = QLabel(self.layoutWidget)
        self.m3_val_label.setObjectName(u"m3_val_label")

        self.gridLayout.addWidget(self.m3_val_label, 6, 1, 1, 1)

        self.roll_val_label = QLabel(self.layoutWidget)
        self.roll_val_label.setObjectName(u"roll_val_label")

        self.gridLayout.addWidget(self.roll_val_label, 10, 1, 1, 1)

        self.roll_label = QLabel(self.layoutWidget)
        self.roll_label.setObjectName(u"roll_label")

        self.gridLayout.addWidget(self.roll_label, 10, 0, 1, 1)

        self.pitch_val_label = QLabel(self.layoutWidget)
        self.pitch_val_label.setObjectName(u"pitch_val_label")

        self.gridLayout.addWidget(self.pitch_val_label, 9, 1, 1, 1)

        self.motor3_label = QLabel(self.layoutWidget)
        self.motor3_label.setObjectName(u"motor3_label")

        self.gridLayout.addWidget(self.motor3_label, 6, 0, 1, 1)

        self.ratio = QLabel(self.layoutWidget)
        self.ratio.setObjectName(u"ratio")

        self.gridLayout.addWidget(self.ratio, 8, 0, 1, 1)

        self.label_2ratio_val = QLabel(self.layoutWidget)
        self.label_2ratio_val.setObjectName(u"label_2ratio_val")

        self.gridLayout.addWidget(self.label_2ratio_val, 8, 1, 1, 1)

        self.graph_frame = QFrame(self.centralwidget)
        self.graph_frame.setObjectName(u"graph_frame")
        self.graph_frame.setGeometry(QRect(320, 10, 960, 540))
        self.graph_frame.setFrameShape(QFrame.StyledPanel)
        self.graph_frame.setFrameShadow(QFrame.Raised)
        self.gridLayoutWidget = QWidget(self.graph_frame)
        self.gridLayoutWidget.setObjectName(u"gridLayoutWidget")
        self.gridLayoutWidget.setGeometry(QRect(0, 0, 961, 541))
        self.GL_layout = QGridLayout(self.gridLayoutWidget)
        self.GL_layout.setObjectName(u"GL_layout")
        self.GL_layout.setContentsMargins(0, 0, 0, 0)
        self.sliders_frame = QFrame(self.centralwidget)
        self.sliders_frame.setObjectName(u"sliders_frame")
        self.sliders_frame.setGeometry(QRect(320, 550, 960, 160))
        self.sliders_frame.setFrameShape(QFrame.StyledPanel)
        self.sliders_frame.setFrameShadow(QFrame.Raised)
        self.layoutWidget1 = QWidget(self.sliders_frame)
        self.layoutWidget1.setObjectName(u"layoutWidget1")
        self.layoutWidget1.setGeometry(QRect(0, 0, 961, 161))
        self.gridLayout_2 = QGridLayout(self.layoutWidget1)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(20, 20, 20, 20)
        self.phi_label = QLabel(self.layoutWidget1)
        self.phi_label.setObjectName(u"phi_label")

        self.gridLayout_2.addWidget(self.phi_label, 0, 0, 1, 1)

        self.phi_slider = QScrollBar(self.layoutWidget1)
        self.phi_slider.setObjectName(u"phi_slider")
        self.phi_slider.setEnabled(False)
        self.phi_slider.setMinimum(-110)
        self.phi_slider.setMaximum(110)
        self.phi_slider.setPageStep(1)
        self.phi_slider.setOrientation(Qt.Horizontal)

        self.gridLayout_2.addWidget(self.phi_slider, 0, 1, 1, 2)

        self.theta_label = QLabel(self.layoutWidget1)
        self.theta_label.setObjectName(u"theta_label")

        self.gridLayout_2.addWidget(self.theta_label, 1, 0, 1, 1)

        self.theta_slider = QScrollBar(self.layoutWidget1)
        self.theta_slider.setObjectName(u"theta_slider")
        self.theta_slider.setEnabled(False)
        self.theta_slider.setMinimum(-110)
        self.theta_slider.setMaximum(110)
        self.theta_slider.setPageStep(1)
        self.theta_slider.setTracking(True)
        self.theta_slider.setOrientation(Qt.Horizontal)

        self.gridLayout_2.addWidget(self.theta_slider, 1, 1, 1, 2)

        self.autolevel_button = QPushButton(self.layoutWidget1)
        self.autolevel_button.setObjectName(u"autolevel_button")
        self.autolevel_button.setEnabled(False)

        self.gridLayout_2.addWidget(self.autolevel_button, 2, 1, 1, 1)

        self.angle_button = QPushButton(self.layoutWidget1)
        self.angle_button.setObjectName(u"angle_button")

        self.gridLayout_2.addWidget(self.angle_button, 2, 2, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.weight_button.setText(QCoreApplication.translate("MainWindow", u"Weigh", None))
        self.force_val_label.setText(QCoreApplication.translate("MainWindow", u"force goes here", None))
        self.start_button.setText(QCoreApplication.translate("MainWindow", u"Start", None))
        self.m1_val_label.setText(QCoreApplication.translate("MainWindow", u"motor 1 goes here", None))
        self.force_label.setText(QCoreApplication.translate("MainWindow", u"Total Force", None))
        self.motor4_label.setText(QCoreApplication.translate("MainWindow", u"Motor 4", None))
        self.m4_val_label.setText(QCoreApplication.translate("MainWindow", u"m4 val", None))
        self.time_val_label.setText(QCoreApplication.translate("MainWindow", u"time val", None))
        self.weight_val_label.setText(QCoreApplication.translate("MainWindow", u"weight val", None))
        self.time_label.setText(QCoreApplication.translate("MainWindow", u"Elapsed time", None))
        self.motor1_label_2.setText(QCoreApplication.translate("MainWindow", u"Motor 2", None))
        self.pitch_label.setText(QCoreApplication.translate("MainWindow", u"Pitch:", None))
        self.pushButton.setText(QCoreApplication.translate("MainWindow", u"Save to File", None))
        self.stop_button.setText(QCoreApplication.translate("MainWindow", u"Stop", None))
        self.tar_button.setText(QCoreApplication.translate("MainWindow", u"TARE", None))
        self.m2_val_label.setText(QCoreApplication.translate("MainWindow", u"m2 val", None))
        self.motor1_label.setText(QCoreApplication.translate("MainWindow", u"Motor 1", None))
        self.m3_val_label.setText(QCoreApplication.translate("MainWindow", u"m3 val", None))
        self.roll_val_label.setText(QCoreApplication.translate("MainWindow", u"roll val", None))
        self.roll_label.setText(QCoreApplication.translate("MainWindow", u"Rol:", None))
        self.pitch_val_label.setText(QCoreApplication.translate("MainWindow", u"pitch val", None))
        self.motor3_label.setText(QCoreApplication.translate("MainWindow", u"Motor 3", None))
        self.ratio.setText(QCoreApplication.translate("MainWindow", u"Thrust-to-Weight", None))
        self.label_2ratio_val.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.phi_label.setText(QCoreApplication.translate("MainWindow", u"Phi:", None))
        self.theta_label.setText(QCoreApplication.translate("MainWindow", u"Theta:", None))
        self.autolevel_button.setText(QCoreApplication.translate("MainWindow", u"Auto-level", None))
        self.angle_button.setText(QCoreApplication.translate("MainWindow", u"Angle", None))
    # retranslateUi

