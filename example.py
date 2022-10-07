# # import sqlite3

# # conn = sqlite3.connect('example')
# # c = conn.cursor()
# # c.execute("CREATE TABLE IF NOT EXISTS tabla1(unix REAL, fecha TEXT, palabraclave TEXT, valor REAL)")
# # c.execute("INSERT INTO tabla1 VALUES(1452549219,'2018-02-12 16:50:39','Python',6)")
# # conn.commit()
# # c.close()
# # conn.close()

# import psycopg2

# con = psycopg2.connect(
#   database="postgres",
#   user="postgres", 
#   password = "cisco12345",
#   host="127.0.0.1",
#   port="5432"
#   )
# print("Database opened successfully")
# # cur = con.cursor()
# # # cur.execute('''CREATE TABLE STUDENT
# # #       (ADMISSION INT PRIMARY KEY     NOT NULL,
# # #       NAME           TEXT    NOT NULL,
# # #       AGE            INT     NOT NULL,
# # #       COURSE        CHAR(50),
# # #       DEPARTMENT        CHAR(50));''')

# # cur.execute("INSERT INTO STUDENT (ADMISSION,NAME,AGE,COURSE,DEPARTMENT) VALUES (3424, 'Alexis', 12, 'Computer Science', 'ICd')");
# # con.commit()
# # print("Record inserted successfully")
# # # con.close()
# # print("Table created successfully")
# # print("database opened successfully")


# # cur = con.cursor()
# # cur.execute("SELECT admission, name, age, course, department from STUDENT")
# # rows = cur.fetchall()

# # for row in rows:
# #     print("ADMISSION =", row[0])
# #     print("NAME =", row[1])
# #     print("AGE =", row[2])
# #     print("COURSE =", row[3])
# #     print("DEPARTMENT =", row[4], "n")

# # print("Operation done successfully")
# # con.close()mys

import mysql.connector

mydb = mysql.connector.connect(
  
  host = "localhost",
  user = "admin",
  password = "cisco12345"
)

mycursor = mydb.cursor()
mycursor.execute("CREATE DATABASE ejemplo_3")