# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'form.ui'
##
## Created by: Qt User Interface Compiler version 6.8.0
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QLayout,
    QLineEdit, QMainWindow, QPushButton, QRadioButton,
    QSizePolicy, QVBoxLayout, QWidget)
import img_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.setEnabled(True)
        MainWindow.resize(400, 500)
        MainWindow.setMinimumSize(QSize(400, 500))
        MainWindow.setMaximumSize(QSize(400, 500))
        MainWindow.setStyleSheet(u"background-color:#212121;")
        MainWindow.setIconSize(QSize(24, 24))
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.centralwidget.setMinimumSize(QSize(400, 500))
        self.centralwidget.setMaximumSize(QSize(16777215, 500))
        self.horizontalLayout_3 = QHBoxLayout(self.centralwidget)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setSpacing(20)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(30, 30, 30, 30)
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.label_3 = QLabel(self.centralwidget)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setMinimumSize(QSize(150, 50))
        self.label_3.setMaximumSize(QSize(150, 50))
        self.label_3.setStyleSheet(u"QLabel {\n"
"    font-weight: 700;  \n"
"    padding-left: 30px; \n"
"	color:#fd4a24      \n"
"}")

        self.horizontalLayout_4.addWidget(self.label_3)

        self.label_2 = QLabel(self.centralwidget)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setMinimumSize(QSize(150, 50))
        self.label_2.setMaximumSize(QSize(150, 50))
        self.label_2.setStyleSheet(u"background-color:transparent;\n"
"image: url(:/image/Positivo.png);")

        self.horizontalLayout_4.addWidget(self.label_2)


        self.verticalLayout.addLayout(self.horizontalLayout_4)

        self.lineEdit_login = QLineEdit(self.centralwidget)
        self.lineEdit_login.setObjectName(u"lineEdit_login")
        self.lineEdit_login.setMaximumSize(QSize(16777215, 40))
        self.lineEdit_login.setStyleSheet(u" border: 1px solid #fd4a24;\n"
"border-radius:10px;\n"
"padding-left:6px;\n"
"color:#fff     ")

        self.verticalLayout.addWidget(self.lineEdit_login)

        self.lineEdit_senha = QLineEdit(self.centralwidget)
        self.lineEdit_senha.setObjectName(u"lineEdit_senha")
        self.lineEdit_senha.setMaximumSize(QSize(16777215, 40))
        self.lineEdit_senha.setStyleSheet(u" border: 1px solid #fd4a24;\n"
"border-radius:10px;\n"
"padding-left:6px;\n"
"color:#fff     ")
        self.lineEdit_senha.setEchoMode(QLineEdit.EchoMode.Password)

        self.verticalLayout.addWidget(self.lineEdit_senha)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(6)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self.pushButton = QPushButton(self.centralwidget)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setMinimumSize(QSize(150, 40))
        self.pushButton.setMaximumSize(QSize(150, 40))
        self.pushButton.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.pushButton.setStyleSheet(u" border: 1px solid #fd4a24;\n"
"border-radius:10px;\n"
"color:#fff     ")

        self.horizontalLayout.addWidget(self.pushButton)

        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        self.label.setMaximumSize(QSize(100000, 20))
        self.label.setStyleSheet(u"color:#fd4a24; background-color:transparent;")

        self.horizontalLayout.addWidget(self.label)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setSpacing(45)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self.radioButtonSE = QRadioButton(self.centralwidget)
        self.radioButtonSE.setObjectName(u"radioButtonSE")
        self.radioButtonSE.setMinimumSize(QSize(75, 40))
        self.radioButtonSE.setMaximumSize(QSize(75, 40))
        self.radioButtonSE.setTabletTracking(False)
        self.radioButtonSE.setStyleSheet(u"color:#fff;\n"
"border: 1px solid #fd4a24;\n"
"border-radius:10px;\n"
"padding: 10px;\n"
"\n"
"")

        self.horizontalLayout_2.addWidget(self.radioButtonSE)

        self.radioButtonMA = QRadioButton(self.centralwidget)
        self.radioButtonMA.setObjectName(u"radioButtonMA")
        self.radioButtonMA.setMinimumSize(QSize(75, 40))
        self.radioButtonMA.setMaximumSize(QSize(75, 40))
        self.radioButtonMA.setStyleSheet(u"border: 1px solid #fd4a24;\n"
"border-radius:10px;\n"
"padding: 10px;\n"
"color:#fff;")

        self.horizontalLayout_2.addWidget(self.radioButtonMA)

        self.radioButtonCE = QRadioButton(self.centralwidget)
        self.radioButtonCE.setObjectName(u"radioButtonCE")
        self.radioButtonCE.setMinimumSize(QSize(75, 40))
        self.radioButtonCE.setMaximumSize(QSize(75, 40))
        self.radioButtonCE.setStyleSheet(u"border: 1px solid #fd4a24;\n"
"border-radius:10px;\n"
"padding: 10px;\n"
"color:#fff;")

        self.horizontalLayout_2.addWidget(self.radioButtonCE)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.lineEdit = QLineEdit(self.centralwidget)
        self.lineEdit.setObjectName(u"lineEdit")
        self.lineEdit.setMaximumSize(QSize(16777215, 40))
        self.lineEdit.setStyleSheet(u" border: 1px solid #fd4a24;\n"
"border-radius:10px;\n"
"padding-left:6px;\n"
"color:#fff     ")

        self.verticalLayout.addWidget(self.lineEdit)

        self.pushButton_cadastrar = QPushButton(self.centralwidget)
        self.pushButton_cadastrar.setObjectName(u"pushButton_cadastrar")
        self.pushButton_cadastrar.setEnabled(False)
        self.pushButton_cadastrar.setMaximumSize(QSize(16777215, 40))
        self.pushButton_cadastrar.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.pushButton_cadastrar.setStyleSheet(u"QPushButton {\n"
"    background: qlineargradient(\n"
"        spread: pad, x1: 0, y1: 0.5, x2: 1, y2: 0.5,\n"
"        stop: 0 rgba(253, 74, 36, 1),\n"
"        stop: 0.44 rgba(255, 126, 0, 1),\n"
"        stop: 1 rgba(225, 73, 0, 1)\n"
"    );\n"
"    color: white;\n"
"    border-radius: 10px;\n"
"    font-size: 16px;\n"
"	font-weight: 700;\n"
"}\n"
"QPushButton:hover {\n"
"    background: qlineargradient(\n"
"        spread: pad, x1: 0, y1: 0.5, x2: 1, y2: 0.5,\n"
"        stop: 0 rgba(253, 84, 46, 1),\n"
"        stop: 0.44 rgba(255, 136, 10, 1),\n"
"        stop: 1 rgba(235, 83, 10, 1)\n"
"    );\n"
"}\n"
"QPushButton:pressed {\n"
"    background: qlineargradient(\n"
"        spread: pad, x1: 0, y1: 0.5, x2: 1, y2: 0.5,\n"
"        stop: 0 rgba(243, 64, 26, 1),\n"
"        stop: 0.44 rgba(245, 116, 0, 1),\n"
"        stop: 1 rgba(215, 63, 0, 1)\n"
"    );\n"
"}\n"
"")
        self.pushButton_cadastrar.setIconSize(QSize(0, 0))

        self.verticalLayout.addWidget(self.pushButton_cadastrar)


        self.horizontalLayout_3.addLayout(self.verticalLayout)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"AUTO ART/CRF", None))
#if QT_CONFIG(whatsthis)
        MainWindow.setWhatsThis(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><br/></p></body></html>", None))
#endif // QT_CONFIG(whatsthis)
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"AUTO ART/CRF", None))
        self.label_2.setText("")
        self.lineEdit_login.setPlaceholderText(QCoreApplication.translate("MainWindow", u"LOGIN", None))
        self.lineEdit_senha.setPlaceholderText(QCoreApplication.translate("MainWindow", u"SENHA", None))
        self.pushButton.setText(QCoreApplication.translate("MainWindow", u"Escolher Arquivo", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"...", None))
        self.radioButtonSE.setText(QCoreApplication.translate("MainWindow", u"CRF", None))
        self.radioButtonMA.setText(QCoreApplication.translate("MainWindow", u"MA", None))
        self.radioButtonCE.setText(QCoreApplication.translate("MainWindow", u"CE", None))
        self.lineEdit.setPlaceholderText(QCoreApplication.translate("MainWindow", u"N\u00famero da ART", None))
        self.pushButton_cadastrar.setText(QCoreApplication.translate("MainWindow", u"CADASTRAR", None))
    # retranslateUi

