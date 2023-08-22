# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'form.ui'
##
## Created by: Qt User Interface Compiler version 6.5.1
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
from PySide6.QtWidgets import (QApplication, QLabel, QLineEdit, QMainWindow,
    QPushButton, QRadioButton, QSizePolicy, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.setEnabled(True)
        MainWindow.resize(500, 350)
        MainWindow.setMinimumSize(QSize(500, 350))
        MainWindow.setMaximumSize(QSize(500, 350))
        MainWindow.setStyleSheet(u"")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.pushButton = QPushButton(self.centralwidget)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setGeometry(QRect(80, 133, 141, 41))
        self.pushButton.setCursor(QCursor(Qt.PointingHandCursor))
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(240, 133, 161, 41))
        self.lineEdit = QLineEdit(self.centralwidget)
        self.lineEdit.setObjectName(u"lineEdit")
        self.lineEdit.setGeometry(QRect(130, 233, 251, 31))
        self.pushButton_cadastrar = QPushButton(self.centralwidget)
        self.pushButton_cadastrar.setObjectName(u"pushButton_cadastrar")
        self.pushButton_cadastrar.setEnabled(False)
        self.pushButton_cadastrar.setGeometry(QRect(170, 283, 161, 51))
        self.pushButton_cadastrar.setCursor(QCursor(Qt.PointingHandCursor))
        self.pushButton_cadastrar.setIconSize(QSize(0, 0))
        self.lineEdit_login = QLineEdit(self.centralwidget)
        self.lineEdit_login.setObjectName(u"lineEdit_login")
        self.lineEdit_login.setGeometry(QRect(120, 10, 261, 41))
        self.lineEdit_senha = QLineEdit(self.centralwidget)
        self.lineEdit_senha.setObjectName(u"lineEdit_senha")
        self.lineEdit_senha.setGeometry(QRect(120, 60, 261, 41))
        self.radioButtonCE = QRadioButton(self.centralwidget)
        self.radioButtonCE.setObjectName(u"radioButtonCE")
        self.radioButtonCE.setGeometry(QRect(170, 190, 51, 26))
        self.radioButtonMA = QRadioButton(self.centralwidget)
        self.radioButtonMA.setObjectName(u"radioButtonMA")
        self.radioButtonMA.setGeometry(QRect(230, 190, 51, 26))
        self.radioButtonSE = QRadioButton(self.centralwidget)
        self.radioButtonSE.setObjectName(u"radioButtonSE")
        self.radioButtonSE.setGeometry(QRect(290, 190, 51, 26))
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"D\u00c9BORA BOT", None))
#if QT_CONFIG(whatsthis)
        MainWindow.setWhatsThis(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><br/></p></body></html>", None))
#endif // QT_CONFIG(whatsthis)
        self.pushButton.setText(QCoreApplication.translate("MainWindow", u"Escolher Arquivo", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"...", None))
        self.lineEdit.setPlaceholderText(QCoreApplication.translate("MainWindow", u"N\u00famero da ART", None))
        self.pushButton_cadastrar.setText(QCoreApplication.translate("MainWindow", u"CADASTRAR", None))
        self.lineEdit_login.setPlaceholderText(QCoreApplication.translate("MainWindow", u"LOGIN", None))
        self.lineEdit_senha.setPlaceholderText(QCoreApplication.translate("MainWindow", u"SENHA", None))
        self.radioButtonCE.setText(QCoreApplication.translate("MainWindow", u"CE", None))
        self.radioButtonMA.setText(QCoreApplication.translate("MainWindow", u"MA", None))
        self.radioButtonSE.setText(QCoreApplication.translate("MainWindow", u"SE", None))
    # retranslateUi

