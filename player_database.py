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
import sqlite3
import os

def egdfile_to_sqlite(conn, filename):
    c = conn.cursor()
    c.execute('''CREATE TABLE players
                 (firstname text, lastname text, rank text, id int, GoR int)''')
    with open(filename) as asciifile:
        # Remove first 26 lines in file.
        for _ in range(26):
            asciifile.next()

        for row in asciifile:
            if row == '\n':
                break
            name = row[11:49]
            rank = row[60:63]
            club = row[53:57]
            egdid = row[1:9]
            GoR = row[71:75]

            # Format name into first and last.
            name = name.strip()
            names = name.split(' ')
            try:
                firstname = names[1]
            except IndexError:
                firstname = ''

            lastname = names[0]

            try:
                GoR = int(GoR)
            except TypeError:
                GoR = None
            try:
                egdid = int(egdid)
            except TypeError:
                egdid = None
                

            c.execute('INSERT INTO players VALUES ("{0}", "{1}", "{2}", {3}, {4})'.format(
                firstname, lastname, rank, egdid, GoR))

    conn.commit()







def main():
    filename = './EGD/test.db'
    asciitxt_filename = 'EGD/allworld_lp.html'
    if os.path.exists(filename):
        os.remove(filename)

    conn = sqlite3.connect(filename)
    egdfile_to_sqlite(conn, asciitxt_filename)
    c = conn.cursor()
    
    for row in c.execute('SELECT * FROM players WHERE firstname LIKE "%Eski%"'):
        print(row)
    conn.close()


    
if __name__=='__main__':
    main()
