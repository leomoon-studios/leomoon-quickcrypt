#-*- coding: utf-8 -*-

"""
Usage:
  QuickCrypt [-e FILE | -d FILE]
"""

#version: 2.0.9

# TODO:

import os
import sys
#load dlls
dllpath = os.path.dirname(os.path.realpath(sys.argv[0]))
os.environ["PATH"] += os.pathsep + dllpath
os.environ["DYLD_FALLBACK_LIBRARY_PATH"] = dllpath
import random
from PyQt5 import QtWidgets, QtCore, QtGui #pyqt stuff
#local imports
from ext.darkdetect import isDark #darkdetect 0.7.1 [ https://github.com/albertosottile/darkdetect ] 20220718
from ext.docopt import docopt
from file_operations import delete_source_after_success, decrypt_file, encrypt_file
from gui.guiMain import Ui_main

home_dir = os.path.expanduser("~")

QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True) #enable highdpi scaling
QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True) #use highdpi icons

title = 'LeoMoon QuickCrypt'
ver = '1.0.0'

class mainUi(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        args = docopt(__doc__, version=ver)
        #print(args['FILE'])
        #print(args)
        QtWidgets.QWidget.__init__(self, None)
        self.themeFlg = False
        self.setAcceptDrops(True) #accept file drops
        self.ui = Ui_main()
        self.ui.setupUi(self)
		#disable resizing
        self.setFixedSize(self.width(), self.height())
        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.MSWindowsFixedSizeDialogHint | QtCore.Qt.WindowMinimizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        #self.setWindowFlags(QtCore.Qt.FramelessWindowHint) #frameless window
        #self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.WindowTitleHint | QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowCloseButtonHint) #close only window
        #self.ui.tabWidget.currentChanged.connect(self._tabChange) #detect tab change
        ###############################################################################
        ####### Variables #############################################################
        ###############################################################################
        self.hotSwitch = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+M"), self)
        self.hotSwitch.activated.connect(self._theme)
        self.titleFontsize = 15
        self.uiFontsize = 10
        self.statusFontsize = 11
        if sys.platform.startswith('darwin'):
            self.titleFontsize = 20
            self.uiFontsize = 13
            self.statusFontsize = 14
        self.ui.titleLbl.setFont(QtGui.QFont("Vazir", self.titleFontsize, QtGui.QFont.Black))
        # self.ui.verLbl.setFont(QtGui.QFont('Vazir', self.statusFontsize))
        self.ui.encFileInp.setFont(QtGui.QFont('Vazir', self.uiFontsize))
        self.ui.encPassInp.setFont(QtGui.QFont('Vazir', self.uiFontsize))
        self.ui.encPassConfirmInp.setFont(QtGui.QFont('Vazir', self.uiFontsize))
        self.ui.encDelCbox.setFont(QtGui.QFont('Vazir', self.uiFontsize))
        self.ui.encBrowseBtn.setFont(QtGui.QFont('Vazir', self.statusFontsize))
        self.ui.decFileInp.setFont(QtGui.QFont('Vazir', self.uiFontsize))
        self.ui.decPassInp.setFont(QtGui.QFont('Vazir', self.uiFontsize))
        self.ui.decDelCbox.setFont(QtGui.QFont('Vazir', self.uiFontsize))
        self.ui.decBrowseBtn.setFont(QtGui.QFont('Vazir', self.statusFontsize))
        self.ui.lengthLbl.setFont(QtGui.QFont('Vazir', self.uiFontsize))
        self.ui.lengthSbox.setFont(QtGui.QFont('Vazir', self.uiFontsize))
        self.ui.lowerCbox.setFont(QtGui.QFont('Vazir', self.uiFontsize))
        self.ui.numCbox.setFont(QtGui.QFont('Vazir', self.uiFontsize))
        self.ui.pppCbox.setFont(QtGui.QFont('Vazir', self.uiFontsize))
        self.ui.upperCbox.setFont(QtGui.QFont('Vazir', self.uiFontsize))
        self.ui.specialCbox.setFont(QtGui.QFont('Vazir', self.uiFontsize))
        self.ui.encClearBtn.setFont(QtGui.QFont('Vazir', self.uiFontsize))
        self.ui.encBtn.setFont(QtGui.QFont('Vazir', self.uiFontsize, QtGui.QFont.Black))
        self.ui.decClearBtn.setFont(QtGui.QFont('Vazir', self.uiFontsize))
        self.ui.decBtn.setFont(QtGui.QFont('Vazir', self.uiFontsize, QtGui.QFont.Black))
        self.ui.genClearBtn.setFont(QtGui.QFont('Vazir', self.uiFontsize))
        self.ui.genBtn.setFont(QtGui.QFont('Vazir', self.uiFontsize, QtGui.QFont.Black))
        self.ui.copyLbl.setFont(QtGui.QFont('Vazir', self.uiFontsize))
        self.ui.statusLbl.setFont(QtGui.QFont('Vazir', self.uiFontsize))
        self.ui.tabWidget.setFont(QtGui.QFont('Vazir', self.uiFontsize))
        self.ui.titleLbl.setText(title)
        self.ui.verLbl.setText('v'+ver)
        #modify ui based on arguments
        if args['-e']:
            self.ui.tabWidget.setTabEnabled(1,False)
            self.ui.tabWidget.setStyleSheet("QTabBar::tab::disabled {width: 0; height: 0; margin: 0; padding: 0; border: none;} ")
            if os.path.exists(args['FILE']):
                self.ui.encFileInp.setText(args['FILE'])
                self.ui.encPassInp.setFocus()
            else:
                self.ui.encBrowseBtn.setFocus()
        elif args['-d']:
            self.ui.tabWidget.setTabEnabled(0,False)
            self.ui.tabWidget.setStyleSheet("QTabBar::tab::disabled {width: 0; height: 0; margin: 0; padding: 0; border: none;} ")
            self.ui.tabWidget.setTabEnabled(2,False)
            self.ui.tabWidget.setStyleSheet("QTabBar::tab::disabled {width: 0; height: 0; margin: 0; padding: 0; border: none;} ")
            if os.path.exists(args['FILE']):
                self.ui.decFileInp.setText(args['FILE'])
                self.ui.decPassInp.setFocus()
            else:
                self.ui.decBrowseBtn.setFocus()
        else: #activate browse button
            self.ui.encBrowseBtn.setFocus()
        #self.statusBar().setSizeGripEnabled(False) #disable resize arrow
        if isDark():
            self.themeFlg = False
            self._theme()
        else:
            self.themeFlg = True
            self._theme()
        #prepare status bar
        self.ui.statusLbl.setText('Ready.')
        self.ui.copyLbl.setOpenExternalLinks(True)
        self.ui.copyLbl.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse)
        self.ui.copyLbl.setText('© LeoMoon Studios')
        #self.ui.statusbar.addPermanentWidget(self.ui.statusLbl, 4)
        #self.ui.statusbar.addPermanentWidget(self.ui.copyLbl, 2)
        #label as link
        #self.ui.copyLbl.setOpenExternalLinks(True)
        #self.ui.copyLbl.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse)
        #self.ui.copyLbl.setText('<a style="text-decoration:none; color: inherit;" href="http://leomoon.com">© LeoMoon Studios</a>')
        #ui functions
        self.ui.encBrowseBtn.clicked.connect(self._encBrowse)
        self.ui.encClearBtn.clicked.connect(self._clearall)
        self.ui.encBtn.clicked.connect(self._encrypt)
        self.ui.decClearBtn.clicked.connect(self._clearall)
        self.ui.decBrowseBtn.clicked.connect(self._decBrowse)
        self.ui.decBtn.clicked.connect(self._decrypt)
        self.ui.genBtn.clicked.connect(self._passgen)
        self.ui.genClearBtn.clicked.connect(self._clearall)
        self.ui.pppCbox.toggled.connect(self._toggle)
        # if sys.platform.startswith('darwin'): #macos
        #     #pyqt 5.14.1 fixes
        #     self.ui.tabWidget.resize(self.ui.tabWidget.width(), self.ui.tabWidget.height()+3)
        #     self.ui.encBrowseBtn.resize(self.ui.encBrowseBtn.width()+11, self.ui.encBrowseBtn.height()+7)
        #     self.ui.decBrowseBtn.resize(self.ui.decBrowseBtn.width()+11, self.ui.decBrowseBtn.height()+7)
        #     self.ui.encClearBtn.resize(self.ui.encClearBtn.width()+11, self.ui.encClearBtn.height()+6)
        #     self.ui.encBtn.resize(self.ui.encBtn.width()+11, self.ui.encBtn.height()+6)
        #     self.ui.decClearBtn.resize(self.ui.decClearBtn.width()+11, self.ui.decClearBtn.height()+6)
        #     self.ui.decBtn.resize(self.ui.decBtn.width()+11, self.ui.decBtn.height()+6)
        #     self.ui.genBtn.resize(self.ui.genBtn.width()+11, self.ui.genBtn.height()+6)
        #     self.ui.genClearBtn.resize(self.ui.genClearBtn.width()+11, self.ui.genClearBtn.height()+6)
        #     self.ui.tabWidget.move(self.ui.tabWidget.pos().x()-2, self.ui.tabWidget.pos().y())
        #     self.ui.encBrowseBtn.move(self.ui.encBrowseBtn.pos().x()-6, self.ui.encBrowseBtn.pos().y()-3)
        #     self.ui.decBrowseBtn.move(self.ui.decBrowseBtn.pos().x()-6, self.ui.decBrowseBtn.pos().y()-3)
        #     self.ui.encClearBtn.move(self.ui.encClearBtn.pos().x()-6, self.ui.encClearBtn.pos().y()-2)
        #     self.ui.encBtn.move(self.ui.encBtn.pos().x()-6, self.ui.encBtn.pos().y()-2)
        #     self.ui.decClearBtn.move(self.ui.decClearBtn.pos().x()-6, self.ui.decClearBtn.pos().y()-2)
        #     self.ui.decBtn.move(self.ui.decBtn.pos().x()-6, self.ui.decBtn.pos().y()-2)
        #     self.ui.genClearBtn.move(self.ui.genClearBtn.pos().x()-6, self.ui.genClearBtn.pos().y()-2)
        #     self.ui.genBtn.move(self.ui.genBtn.pos().x()-6, self.ui.genBtn.pos().y()-2)
            #pyqt 5.10.1 fixes
            #self.ui.tabWidget.move(10-2, 90-3)
            #self.ui.encClearBtn.move(200-6, 90-3)
            #self.ui.encBtn.move(290-6, 90-3)
            #self.ui.decClearBtn.move(200-6, 90-3)
            #self.ui.decBtn.move(290-6, 90-3)
            #self.ui.genClearBtn.move(200-6, 90-3)
            #self.ui.genClearBtn.resize(81+6+5, 41+9)
            #self.ui.genBtn.move(290-6, 90-3)
            #self.ui.encClearBtn.resize(81+6+5, 41+9)
            #self.ui.encBtn.resize(81+6+5, 41+9)
            #self.ui.decClearBtn.resize(81+6+5, 41+9)
            #self.ui.decBtn.resize(81+6+5, 41+9)
            #self.ui.genBtn.resize(81+6+5, 41+9)

        ###############################################################################
        ####### Variables #############################################################
        ###############################################################################
        self.setWindowTitle(title)
        self.buffersize = 64*1024
        self.pppChars = '!#%+23456789:=?@ABCDEFGHJKLMNPRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
        self.upperChars = 'ABCDEFGHIJLKMNOPQRSTUVWXYZ'
        self.lowerChars = 'abcdefghijklmnopqrstuvwxyz'
        self.specialChars = '`~@#$%^&*()_+-=[]\\{|}"\',.<>/?'
        self.numChars = '01234567890'

    ###############################################################################
    ####### File Drop #############################################################
    ###############################################################################
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls:
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls:
            try:
                event.setDropAction(QtCore.Qt.CopyAction)
                event.accept()
                urls = event.mimeData().urls()
                if os.path.isfile(str(urls[0].toLocalFile())):
                    self._dropOpen(str(urls[0].toLocalFile()))
            except Exception as error:
                event.ignore()
        else:
            event.ignore()

    ###############################################################################
    ####### File Manipulation #####################################################
    ###############################################################################
    def _dropOpen(self, name):
        self.ui.encFileInp.setText('') #set text to nothing first
        self.ui.decFileInp.setText('') #set text to nothing first
        name = name.replace('file://','').rstrip()
        if name and os.path.exists(name):
            self.ui.encFileInp.setText(name)
            self.ui.decFileInp.setText(name)
        # else:
        #     self.ui.editorEdit.setFocus()

    def _encBrowse(self):
        self.filename = QtWidgets.QFileDialog.getOpenFileName(self, 'Open...', home_dir, "(*.*)")
        if self.filename and os.path.exists(self.filename[0]):
            self.ui.encFileInp.setText(self.filename[0])

    def _decBrowse(self):
        self.filename = QtWidgets.QFileDialog.getOpenFileName(self, 'Open...', home_dir, "(*.*)")
        if self.filename and os.path.exists(self.filename[0]):
            self.ui.decFileInp.setText(self.filename[0])

    ###############################################################################
    ####### Functions #############################################################
    ###############################################################################
    #def _tabChange(self, i): #detect tab change to set default button
    #    if i == 0:
    #        self.ui.encBtn.setDefault(True)
    #    elif i == 1:
    #        self.ui.decBtn.setDefault(True)
    #    elif i == 2:
    #        self.ui.genBtn.setDefault(True)

    def _theme(self):
        if not self.themeFlg:
            dark_theme = QtGui.QPalette()
            dark_theme.setColor(QtGui.QPalette.Window, QtGui.QColor(55,53,53))
            dark_theme.setColor(QtGui.QPalette.WindowText, QtGui.QColor(227,227,227))
            dark_theme.setColor(QtGui.QPalette.Base, QtGui.QColor(30,30,30))
            dark_theme.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(55,55,55))
            dark_theme.setColor(QtGui.QPalette.ToolTipBase, QtGui.QColor(50,50,50))
            dark_theme.setColor(QtGui.QPalette.ToolTipText, QtGui.QColor(227,227,227))
            dark_theme.setColor(QtGui.QPalette.Text, QtGui.QColor(227,227,227))
            dark_theme.setColor(QtGui.QPalette.Link, QtGui.QColor(227,227,227))
            dark_theme.setColor(QtGui.QPalette.Button, QtGui.QColor(50,50,50))
            dark_theme.setColor(QtGui.QPalette.ButtonText, QtGui.QColor(227,227,227))
            dark_theme.setColor(QtGui.QPalette.BrightText, QtGui.QColor(227,227,227))
            dark_theme.setColor(QtGui.QPalette.Highlight, QtGui.QColor(18,131,220))
            dark_theme.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.black)
            dark_theme.setColor(QtGui.QPalette.Active, QtGui.QPalette.Button, QtGui.QColor(53, 53, 53))
            dark_theme.setColor(QtGui.QPalette.Inactive, QtGui.QPalette.Button, QtGui.QColor(53, 53, 53))
            dark_theme.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, QtGui.QColor(85,83,83))
            dark_theme.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, QtGui.QColor(85,83,83))
            dark_theme.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Text, QtGui.QColor(85,83,83))
            dark_theme.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Light, QtGui.QColor(53, 53, 53))
            QtGui.QGuiApplication.setPalette(dark_theme)
            self.setStyleSheet("""
                                    QFrame#banner {background-color: qlineargradient(x1:0 y1:0, x2:0 y2:1, stop:0 #5e5b5b, stop:1 #373535); border-radius: 0px;}
                                    QLabel#titleLbl {color: rgb(227,227,227);}
                                    QLabel#verLbl {color: rgb(227,227,227);}
                                        """)
            # self.ui.actionDarkMode.setChecked(True)
        else:
            light_theme = QtGui.QPalette()
            light_theme.setColor(QtGui.QPalette.Window, QtGui.QColor(240,240,240))
            light_theme.setColor(QtGui.QPalette.WindowText, QtGui.QColor(68,68,68))
            light_theme.setColor(QtGui.QPalette.Base, QtGui.QColor(255,255,255))
            light_theme.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(255,255,255))
            light_theme.setColor(QtGui.QPalette.ToolTipBase, QtGui.QColor(240,240,240))
            light_theme.setColor(QtGui.QPalette.ToolTipText, QtGui.QColor(68,68,68))
            light_theme.setColor(QtGui.QPalette.Text, QtGui.QColor(68,68,68))
            light_theme.setColor(QtGui.QPalette.Link, QtGui.QColor(68,68,68))
            light_theme.setColor(QtGui.QPalette.Button, QtGui.QColor(240,240,240))
            light_theme.setColor(QtGui.QPalette.ButtonText, QtGui.QColor(68,68,68))
            light_theme.setColor(QtGui.QPalette.BrightText, QtGui.QColor(68,68,68))
            light_theme.setColor(QtGui.QPalette.Highlight, QtGui.QColor(18,131,220))
            light_theme.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.white)
            light_theme.setColor(QtGui.QPalette.Active, QtGui.QPalette.Button, QtGui.QColor(240,240,240))
            light_theme.setColor(QtGui.QPalette.Inactive, QtGui.QPalette.Button, QtGui.QColor(240,240,240))
            light_theme.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, QtGui.QColor(118,118,118))
            light_theme.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, QtGui.QColor(118,118,118))
            light_theme.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Text, QtGui.QColor(118,118,118))
            light_theme.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Light, QtGui.QColor(243,243,243))
            QtGui.QGuiApplication.setPalette(light_theme)
            self.setStyleSheet("""
                                    QFrame#banner {background-color: qlineargradient(x1:0 y1:0, x2:0 y2:1, stop:0 #c9c9c9, stop:1 #F0F0F0); border-radius: 0px;}
                                    QLabel#titleLbl {color: rgb(68,68,68);}
                                    QLabel#verLbl {color: rgb(68,68,68);}
                                        """)
            # self.ui.actionDarkMode.setChecked(False)
        self.themeFlg = not self.themeFlg

    def _clearall(self):
        self.ui.encFileInp.setText('')
        self.ui.encPassInp.setText('')
        self.ui.encPassConfirmInp.setText('')
        self.ui.decFileInp.setText('')
        self.ui.decPassInp.setText('')
        self.ui.historyEdit.setPlainText('')
        self.ui.statusLbl.setText('All fields cleared.')

    def _encrypt(self):
        if self.ui.encFileInp.text() == '':
            self.ui.statusLbl.setText('<span style="color:#CD5C5C;">Please select a file to encrypt!</span>')
        elif os.path.exists(self.ui.encFileInp.text()) is False:
            self.ui.statusLbl.setText('<span style="color:#CD5C5C;">Selected file does not exist!</span>')
        elif os.path.isdir(self.ui.encFileInp.text()) is True:
            self.ui.statusLbl.setText('<span style="color:#CD5C5C;">Please select a file, not a folder!</span>')
        elif self.ui.encPassInp.text() == '':
            self.ui.statusLbl.setText('<span style="color:#CD5C5C;">Password can not be empty!</span>')
        elif self.ui.encPassInp.text() != self.ui.encPassConfirmInp.text():
            self.ui.statusLbl.setText('<span style="color:#CD5C5C;">Passwords do not match!</span>')
        else:
            self.ui.statusLbl.setText('Encrypting... Please wait...')
            try:
                encrypt_file(self.ui.encFileInp.text(), self.ui.encPassInp.text())
                delete_source_after_success(self.ui.encFileInp.text(), self.ui.encDelCbox.isChecked())
                self.ui.statusLbl.setText('<span style="color:#228B22;">File encrypted successfully.</span>')
            except (OSError, ValueError) as error:
                self.ui.statusLbl.setText('<span style="color:#CD5C5C;">'+str(error)+'</span>')

    def _decrypt(self):
        if self.ui.decFileInp.text() == '':
            self.ui.statusLbl.setText('<span style="color:#CD5C5C;">Please select a file to decrypt!</span>')
        elif os.path.exists(self.ui.decFileInp.text()) is False:
            self.ui.statusLbl.setText('<span style="color:#CD5C5C;">Selected file does not exist!</span>')
        elif os.path.isdir(self.ui.decFileInp.text()) is True:
            self.ui.statusLbl.setText('<span style="color:#CD5C5C;">Please select a file, not a folder!</span>')
        elif self.ui.decPassInp.text() == '':
            self.ui.statusLbl.setText('<span style="color:#CD5C5C;">Password can not be empty!</span>')
        else:
            try:
                decrypt_file(self.ui.decFileInp.text(), self.ui.decPassInp.text())
                delete_source_after_success(self.ui.decFileInp.text(), self.ui.decDelCbox.isChecked())
                self.ui.statusLbl.setText('<span style="color:#228B22;">File decrypted successfully.</span>')
            except (OSError, ValueError) as error:
                self.ui.statusLbl.setText('<span style="color:#CD5C5C;">'+str(error)+'</span>')
            finally:
                self.ui.decPassInp.setText('')

    def _toggle(self):
        if self.ui.pppCbox.isChecked():
            self.ui.lowerCbox.setEnabled(False)
            self.ui.upperCbox.setEnabled(False)
            self.ui.numCbox.setEnabled(False)
            self.ui.specialCbox.setEnabled(False)
        else:
            self.ui.lowerCbox.setEnabled(True)
            self.ui.upperCbox.setEnabled(True)
            self.ui.numCbox.setEnabled(True)
            self.ui.specialCbox.setEnabled(True)

    def _passgen(self):
        self.chars = ''
        if self.ui.pppCbox.isChecked():
            self.chars += self.pppChars
        else:
            if self.ui.upperCbox.isChecked():
                self.chars += self.upperChars
            if self.ui.lowerCbox.isChecked():
                self.chars += self.lowerChars
            if self.ui.numCbox.isChecked():
                self.chars += self.numChars
            if self.ui.specialCbox.isChecked():
                self.chars += self.specialChars
        self.ui.historyEdit.moveCursor(QtGui.QTextCursor.End)
        self.ui.historyEdit.append(''.join(random.choice(self.chars) for i in range(self.ui.lengthSbox.value())))
        self.ui.statusLbl.setText('<span style="color:green;">Password generated successfully.</span>')

    def _exit(self):
        self.close()

    def closeEvent(self, event):
        self.close()

def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')
    QtGui.QFontDatabase.addApplicationFont(':/gfx/fonts/Vazir.ttf') #add custom font to install
    QtGui.QFontDatabase.addApplicationFont(':/gfx/fonts/Vazir-Black.ttf') #add custom font to install
    main = mainUi()
    main.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
