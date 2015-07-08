import MySQLdb

TABLENAME = 'titles'
SOURCE_DB_IP = 'localhost'
SOURCE_DB_USER = 'root'
SOURCE_DB_PASSWD = ''
SOURCE_DB_NAME = 'employees'
DESTINATION_DB_IP = 'localhost'
DESTINATION_DB_USER = 'root'
DESTINATION_DB_PASSWD = ''
DESTINATION_DB_NAME = 'employees_without_title'

sourceDb = MySQLdb.connect(host=SOURCE_DB_IP,
                           user=SOURCE_DB_USER,
                           passwd=SOURCE_DB_PASSWD,
                           db=SOURCE_DB_NAME)

destinationDb = MySQLdb.connect(host=DESTINATION_DB_IP,
                                user=DESTINATION_DB_USER,
                                passwd=DESTINATION_DB_PASSWD,
                                db=DESTINATION_DB_NAME)


query = "SELECT * FROM %s;" % (TABLENAME)

cur = sourceDb.cursor()
cur.execute(query)
sourceRows = cur.fetchall()

cur = destinationDb.cursor()
cur.execute(query)
destinationRows = cur.fetchall()


result = True

if len(sourceRows) != len(destinationRows):
    result = False
    print 'ERROR: Length mismatch'
else:
    for (rowS, rowD) in zip(sourceRows, destinationRows):
        for (itemS, itemD) in zip(rowS, rowD):
            if itemS != itemD:
                result = False
                print 'ERROR: ' + str(itemS) + ' not equal ' + str(itemD)


if result:
    print 'PASSED'
else:
    print 'FAILED'

sourceDb.close()
destinationDb.close()
