import sys
import MySQLdb
import datetime

TYPE_STR = type('str')
TYPE_DATETIME = type(datetime.date(2000, 1, 1))
TYPE_NONE = type(None)


def toStr(row):
    res = []
    for item in row:
        if type(item) == TYPE_NONE:
            res.append('NULL')
        elif type(item) == TYPE_STR:
            res.append('"'+item+'"')
        elif type(item) == TYPE_DATETIME:
            res.append('"'+str(item)+'"')
        else:
            res.append(str(item))

    return ','.join(res)


def insertRows(tableName, db, rows):
    cur = db.cursor()

    for row in rows:
        vals = toStr(row)
        try:
            query = "INSERT INTO %s values(%s)" % (tableName, vals)
            cur.execute(query)
            db.commit()
        except Exception, e:
            print str(e)
            sys.exit()


def getRows(tableName, db):
    cur = db.cursor()
    query = "SELECT * FROM %s;" % tableName
    cur.execute(query)
    rows = cur.fetchall()

    return rows


def copyTable(tableName, sourceDb, destinationDb):
    rows = getRows(tableName, sourceDb)
    insertRows(tableName, destinationDb, rows)


def getParams(argv):
    params = {
        'tableName': argv[1],
        'ipAddress1': argv[2],
        'user1': argv[3],
        'passwd1': argv[4],
        'dbName1': argv[5],
        'ipAddress2': argv[6],
        'user2': argv[7],
        'passwd2': argv[8],
        'dbName2': argv[9],
    }

    return params


def main():
    prms = getParams(sys.argv)

    sourceDb = MySQLdb.connect(host=prms['ipAddress1'], user=prms['user1'],
                               passwd=prms['passwd1'], db=prms['dbName1'])
    destinationDb = MySQLdb.connect(host=prms['ipAddress2'], user=prms['user2'],
                                    passwd=prms['passwd2'], db=prms['dbName2'])

    copyTable(prms['tableName'], sourceDb, destinationDb)

    sourceDb.close()
    destinationDb.close()


if __name__ == '__main__':
    main()
