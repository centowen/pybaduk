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
    
    for row in c.execute('SELECT * FROM players WHERE firstname LIKE "%Magnu%"'):
        print(row)
    conn.close()


    
if __name__=='__main__':
    main()
