# A minimal SQLite shell for experiments

import sqlite3

#con = sqlite3.connect(":memory:")
con = sqlite3.connect("lssqllite.db")
con.isolation_level = None
cur = con.cursor()

#con.execute('CREATE TABLE barcode (id INTEGER, barcode TEXT, inserter TEXT, special INTEGER, special2 INTEGER, jobid INTEGER,seq INTEGER, runcmd INTEGER)')
#con.execute("INSERT INTO  barcode values (1,'0000111111000011','192.168.1.1',0,0,111111,1,1)")
#con.commit()

buffer = ""

print "Enter your SQL commands to execute in sqlite3."
print "Enter a blank line to exit."

while True:
    line = raw_input()
    if line == "":
        break
    buffer = line
    if sqlite3.complete_statement(buffer):
        try:
            buffer = buffer.strip()
            cur.execute(buffer)

            if buffer.lstrip().upper().startswith("CREATE"):
                con.commit()
            if buffer.lstrip().upper().startswith("INSERT"):
                con.commit()
            if buffer.lstrip().upper().startswith("SELECT"):
                print cur.fetchall()
        except sqlite3.Error as e:
            print "An error occurred:", e.args[0]
        buffer = ""
    else:
        print "no go (" + buffer + ')'

con.close()
