import sys, select, sqlite3

timeout = 10
cmd_reset   = '9990001'
cmd_take    = '9990002'
cmd_return  = '9990003'
prefix_item = '12'
prefix_card = '00'

card = None
items = None

# Rented out
# select item from (select max(id) as id from checkout group by item) join checkout using (id) where card is not null;

con = sqlite3.connect('checkout.db')
with con:
    cur = con.cursor()
    try:
        cur.execute("CREATE TABLE checkout(id INTEGER PRIMARY KEY, card INTEGER, item INTEGER NOT NULL, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP);")
    except:
        pass

def save_take():
    global card, items, con
    for item in items:
        cur.execute("INSERT INTO checkout (card, item) VALUES(?, ?)", (card, item))
    items = set([])
    con.commit()
    # card remains available

def save_return():
    global card, items, con
    for item in items:
        cur.execute("INSERT INTO checkout (item) VALUES(?)", (item,))
    con.commit()
    items = set([])
    # card remains available

def process_reset():
    global card, items
    card  = None
    items = set([])

def process_take(timeout = False):
    global card, items
    if len(items) == 0:
        return
    elif card is not None:
        print "Er worden %d items aan kaart %d toegevoegd." % (len(items), card)
        save_take()
    elif timeout:
        print "Er is geen kaart aangeboden, de lijst is geleegd."
        process_reset()
    else:
        print "Scan eerst een kaart"

def process_return():
    if len(items) == 0:
        return
    else:
        print "Er worden %d items teruggebracht." % (len(items))
        save_return()

def process_input(reader):
    global card, items
    if reader == cmd_reset:
        process_reset()
    elif reader == cmd_take:
        process_take()
    elif reader == cmd_return:
        process_return()
    elif reader.startswith(prefix_item):
        try:
            items.add(int(reader))
        except:
            pass
    elif reader.startswith(prefix_card):
        try:
            card = int(reader)
        except:
            pass

def input():
    print "Scan een kaart of een item"
    i, o, e = select.select( [sys.stdin], [], [], 10 )

    if (i):
        reader = sys.stdin.readline().strip()
        process_input(reader)
    else:
        process_take()

if __name__ == "__main__":
    process_reset()
    while True:
        input()
