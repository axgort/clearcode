import sys
import MySQLdb
import datetime

TYPE_STR = type('str')
TYPE_DATETIME = type(datetime.date(2000, 1, 1))
TYPE_NONE = type(None)
SELECT_SIZE = 8192
FETCH_SIZE = 4092


class TableSelector(object):
    def __init__(self, tableName, db, selectSize, fetchSize):
        self.db = db
        self.tableName = tableName
        self.selectSize = selectSize
        self.fetchSize = fetchSize
        self.cursor = None
        self.selectPositon = 0

    def select(self, selectSize):
        if self.cursor is None:
            self.cursor = self.db.cursor()

        queryData = (self.tableName, self.selectPositon, selectSize)
        query = "SELECT * FROM %s LIMIT %d,%d;" % queryData
        self.cursor.execute(query)
        self.selectPositon += selectSize

        return self.cursor

    def getRowsGenerator(self):
        cursor = self.select(self.selectSize)
        rows = cursor.fetchmany(self.fetchSize)

        while len(rows) > 0:
            yield rows
            rows = self.cursor.fetchmany(self.fetchSize)

            if len(rows) <= 0:
                cursor = self.select(self.selectSize)
                rows = cursor.fetchmany(self.fetchSize)

        yield None


def toStr(row):
    res = []
    for item in row:
        if type(item) == TYPE_NONE:
            res.append('NULL')
        elif type(item) == TYPE_STR:
            res.append('"'+item+'"')
        elif type(item) == TYPE_DATETIME:
            res.append('"'+str(item)+'"')
        else:  # for numeric values
            res.append(str(item))

    return ','.join(res)


def insertRows(db, tableName, rows):
    cur = db.cursor()

    query = "INSERT INTO %s values" % tableName

    for row in rows:
        vals = toStr(row)
        query += "(%s)," % vals

    query = query[:-1]  # Remove "," from the end of query

    try:
        cur.execute(query)
    except Exception, e:
        print str(e)
        sys.exit()

    db.commit()


def getRows(db, tableName, start, len):
    cur = db.cursor()
    query = "SELECT * FROM %s LIMIT %d,%d;" % (tableName, start, len)
    cur.execute(query)
    rows = cur.fetchall()

    return rows


def copyTable(tableName, sourceDb, destinationDb):
    tableSelector = TableSelector(tableName, sourceDb, SELECT_SIZE, FETCH_SIZE)
    rowsGenerator = tableSelector.getRowsGenerator()

    rows = rowsGenerator.next()
    while rows is not None:
        insertRows(destinationDb, tableName, rows)
        rows = rowsGenerator.next()


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
