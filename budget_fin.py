import csv
import sqlite3
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime



open("creditexpense.db", "w").close()
con = sqlite3.connect("creditexpense.db")
cur = con.cursor()
cur.execute("CREATE TABLE balance(id INTEGER PRIMARY KEY, balance FLOAT, name TEXT)")
cur.execute ("CREATE TABLE date(balance_id INTEGER, transDate DATE, FOREIGN KEY(balance_id) REFERENCES balance(id)) ")
cur.execute("CREATE TABLE Transtype (balance_id INTEGER, type TEXT, FOREIGN KEY(balance_id) REFERENCES balance(id))")
cur.execute("CREATE TABLE category(saleCategory TEXT, balance_id, FOREIGN KEY(balance_id) REFERENCES balance(id))")
with open ("creditcard.csv") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        balance = row["Amount"]
        name = row["Description"]
        cur.execute ("INSERT INTO balance (name) VALUES(?)", [name])
        id = cur.execute("INSERT INTO balance (balance) VALUES(?)", [balance])
        id = cur.lastrowid
        for type in row["Type"].split():
            cur.execute("INSERT INTO Transtype (balance_id, type) VALUES (?, ?)", (id, type))
        for date in row["Post Date"].split():
            cur.execute("INSERT INTO date(balance_id, transDATE) VALUES(?, ?)", (id, date))
        for category in row["Category"].split(","):
            cur.execute("INSERT INTO category(balance_id, saleCategory) VALUES(?, ?)", (id, category))

sale =  cur.execute("SELECT tB.saleCategory, SUM(tA.balance) FROM category tB JOIN balance tA ON tA.id=tB.balance_id GROUP BY tB.balance_id")


category =[]
amount = []
for row in sale:
    print(row)
    category.append(row[0])
    amount.append(row[1])
plt.pie(amount, labels=category)
plt.show()

# Line Graph of budget against time of transactions
dates = [
    i[0]
    for i in cur.execute(
        "SELECT DISTINCT dt.transDATE from date dt ORDER BY dt.transDATE"
    )
]
dtime = []
rbudg = [0]
time_expense = {"Green": [[], []], "Red": [[], []]}

for date in dates:
    res = [
        item[0]
        for item in cur.execute(
            "SELECT SUM(ba.balance) FROM balance ba, date dt WHERE dt.balance_id=ba.id AND dt.transDATE='{}'".format(
                date
            )
        )
    ]
    dtime.append(datetime.strptime(date, "%m/%d/%Y"))
    rbudg.append(rbudg[-1] + res[0])
    if rbudg[-1] > 0:
        time_expense["Green"][0].append(dtime[-1])
        time_expense["Green"][1].append(rbudg[-1])
    else:
        time_expense["Red"][0].append(dtime[-1])
        time_expense["Red"][1].append(rbudg[-1])

del rbudg[0]
# Apply data to plot
plt.plot(dtime, rbudg, color="Blue", zorder=5)
plt.scatter(
    time_expense["Green"][0], time_expense["Green"][1], color="Green", zorder=10
)
plt.scatter(time_expense["Red"][0], time_expense["Red"][1], color="Red", zorder=15)
plt.axhline(y=0, color="Black", linewidth=1, zorder=2)
plt.show()

# for i in category:
#     print(i)
# debitSum= cur.execute("SELECT SUM(balance) FROM balance where id IN (SELECT balance_id FROM Transtype where type = 'DEBIT')")
# debitSum = cur.fetchone()
# creditSum= cur.execute("SELECT SUM(balance) FROM balance where id IN (SELECT balance_id FROM Transtype where type = 'CREDIT')")
# creditSum = cur.fetchone()
# totalCash = debitSum[0]-creditSum[0]

# print("The total CASH FLOW is:", '{0:.2f}'.format(totalCash))
con.commit()
con.close()

