#!/usr/bin/python
# -*- coding: utf-8 -*-
# The GNU General Public License is a free, copyleft license for
# software and other kinds of works.
# 
# The licenses for most software and other practical works are designed
# to take away your freedom to share and change the works. By contrast,
# the GNU General Public License is intended to guarantee your freedom
# to share and change all versions of a program--to make sure it remains
# free software for all its users. We, the Free Software Foundation, use
# the GNU General Public License for most of our software; it applies
# also to any other work released this way by its authors. You can apply
# it to your programs, too.
# 
# When we speak of free software, we are referring to freedom, not
# price. Our General Public Licenses are designed to make sure that you
# have the freedom to distribute copies of free software (and charge for
# them if you wish), that you receive source code or can get it if you
# want it, that you can change the software or use pieces of it in new
# free programs, and that you know you can do these things.
# 
# To protect your rights, we need to prevent others from denying you
# these rights or asking you to surrender the rights. Therefore, you
# have certain responsibilities if you distribute copies of the
# software, or if you modify it: responsibilities to respect the freedom
# of others.
# 
# For example, if you distribute copies of such a program, whether
# gratis or for a fee, you must pass on to the recipients the same
# freedoms that you received. You must make sure that they, too, receive
# or can get the source code. And you must show them these terms so they
# know their rights.
# 
# Developers that use the GNU GPL protect your rights with two steps:
# (1) assert copyright on the software, and (2) offer you this License
# giving you legal permission to copy, distribute and/or modify it.
# 
# For the developers' and authors' protection, the GPL clearly explains
# that there is no warranty for this free software. For both users' and
# authors' sake, the GPL requires that modified versions be marked as
# changed, so that their problems will not be attributed erroneously to
# authors of previous versions.
# 
# Some devices are designed to deny users access to install or run
# modified versions of the software inside them, although the
# manufacturer can do so. This is fundamentally incompatible with the
# aim of protecting users' freedom to change the software. The
# systematic pattern of such abuse occurs in the area of products for
# individuals to use, which is precisely where it is most unacceptable.
# Therefore, we have designed this version of the GPL to prohibit the
# practice for those products. If such problems arise substantially in
# other domains, we stand ready to extend this provision to those
# domains in future versions of the GPL, as needed to protect the
# freedom of users.
# 
# Finally, every program is threatened constantly by software patents.
# States should not allow patents to restrict development and use of
# software on general-purpose computers, but in those that do, we wish
# to avoid the special danger that patents applied to a free program
# could make it effectively proprietary. To prevent this, the GPL
# assures that patents cannot be used to render the program non-free.
# 
# The precise terms and conditions for copying, distribution and
# modification follow.
import codecs
import sys
import logging

from PyQt4.QtCore import QTimer, QSettings
from PyQt4.QtGui import QMainWindow, QWidget, QApplication
import egdcodec

from qttest_ui import Ui_MainWindow
from player_tab import PlayerTab
from pairing_tab import PairingTab
from tournament import Tournament


codecs.register_error('egd', egdcodec.egd_replace)
try:
    logging.basicConfig(filename='debug.log', level=logging.DEBUG)
except:
    pass


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

    def updatetabs(self):
        """Update all open tabs from underlying data model."""
        for i in range(len(self.ui.tabWidget)):
            widget = self.ui.tabWidget.widget(i)
            widget.update()


def main():
    app = QApplication(sys.argv)

    settings = QSettings('weirdo', 'pybaduk')

    turnpath = str(settings.value('turnpath').toString())
    if turnpath == '':
        turnpath = './turn'
        settings.setValue('turnpath', turnpath)
    gbgopen = Tournament(turnpath, u'Göteborg Open 2013')

    mainwindow = MainWindow()
    updatetimer = QTimer()
    updatetimer.timeout.connect(mainwindow.updatetabs)
    updatetimer.start(500)

    playerTab = PlayerTab(gbgopen)
    pairingTab = PairingTab(gbgopen)
    mainwindow.ui.tabWidget.clear()
    mainwindow.ui.tabWidget.addTab(playerTab, "Players")
    mainwindow.ui.tabWidget.addTab(pairingTab, "Pairings")
    mainwindow.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
