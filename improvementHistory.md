## Version 0.1.0 ##
It is a first version and the worst.
Memory usage depends on table size and run time is unacceptable.

I get all rows at the same time. Then I insert them one by one.
```python
def copyTable(tableName, sourceDb, destinationDb):
    rows = getRows(tableName, sourceDb)
    insertRows(tableName, destinationDb, rows)

def getRows(tableName, db):
    cur = db.cursor()
    query = "SELECT * FROM %s;" % tableName
    cur.execute(query)
    rows = cur.fetchall()

    return rows

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
```


## Version 0.1.1 ##
This version solves major time problem.
I ran python profiler with comand `python -m cProfile` on 0.1.0 version.
Then I found that most of the time 0.1.0 version script ran commit function.
```
ncalls  tottime  percall  cumtime  percall filename:lineno(function)
443308  574.703    0.001  574.703    0.001 {method 'commit' of '_mysql.connection' objects}
```

With very small change I got significant improvement.
I moved commit call outside the loop and decreased run time ten times.

```python
def insertRows(tableName, db, rows):
    cur = db.cursor()

    for row in rows:
        vals = toStr(row)
        try:
            query = "INSERT INTO %s values(%s)" % (tableName, vals)
            cur.execute(query)
        except Exception, e:
            print str(e)
            sys.exit()

    db.commit()
```


## Version 0.2.0 ##
This version solves memory usage problem.
The problem with memory was caused by select statement.
In 0.1.x versions I select all data at the same time.
To fix this I added limit to select statement and get data in smaller pieces.

```python
def copyTable(tableName, sourceDb, destinationDb):
    begin = 0
    rows = getRows(sourceDb, tableName, begin, SIZE)

    while len(rows) > 0:
        insertRows(destinationDb, tableName, rows)
        begin += SIZE
        rows = getRows(sourceDb, tableName, begin, SIZE)

def getRows(db, tableName, start, len):
    cur = db.cursor()
    query = "SELECT * FROM %s LIMIT %d,%d;" % (tableName, start, len)
    cur.execute(query)
    rows = cur.fetchall()

    return rows
```

SIZE is a constant with value 100000.
The less is SIZE the slowest script is and the lower memory usege is.


## Version 0.2.1 ##
This version solves the last problem with time.
Python profiler showed that in 0.2.0 version the greatest impact have query function.

```
ncalls  tottime  percall  cumtime  percall filename:lineno(function)
443314   42.084    0.000   42.084    0.000 {method 'query' of '_mysql.connection' objects}
```

To improve it I changed the way of inserting values.
In 0.2.0 version I insert one row at a time and in this version I insert
all rows that I have in one query.

```python
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
```

## Version 0.2.2 ##
In this version I try to decrease memory usage. To do this I created TableSelector class.
It gives possibility to experiment with different select sizes. 
There are two parameters SELECT_SIZE and FETCH_SIZE. 
SELECT_SIZE tell how many records will be selected in one query.
FETCH_SIZE tell how many records will be fetch from query result.

```python
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

def copyTable(tableName, sourceDb, destinationDb):
    tableSelector = TableSelector(tableName, sourceDb, SELECT_SIZE, FETCH_SIZE)
    rowsGenerator = tableSelector.getRowsGenerator()

    rows = rowsGenerator.next()
    while rows is not None:
        insertRows(destinationDb, tableName, rows)
        rows = rowsGenerator.next()
```
This table shows how parameters influence time and memory. 

| Select size | Fetch size |   Time   |  Memory  |
| ----------- | ---------- | -------- | -------- |
|    1024     |    1024    |  39.417s |  24.30MB |
|    2048     |    1024    |  26.278s |  24.55MB |
|    2048     |    2048    |  23.891s |  24.73MB |
|    4096     |    1024    |  20.573s |  25.33MB |
|    4096     |    2048    |  20.233s |  25.33MB |
|    4096     |    4096    |  16.561s |  25.46MB |
|    8192     |    1024    |  17.956s |  26.87MB |
|    8192     |    2048    |  15.868s |  26.87MB |
|    8192     |    4096    |  14.078s |  26.87MB |
|    8192     |    8192    |  14.643s |  27.24MB |
|    65536    |    1024    |  17.154s |  47.29MB |
|    65536    |    2048    |  13.292s |  47.28MB |
|    65536    |    4096    |  12.041s |  47.30MB |
|    65536    |    8192    |  10.244s |  47.31MB |
|    65536    |    16384   |   9.957s |  47.35MB |
|    65536    |    32768   |   9.663s |  47.40MB |
|    65536    |    65536   |   9.563s |  47.28MB |

It is not easy to tell which values are the best.
In my opinion good choice is SELECT_SIZE = 8192 and FETCH_SIZE = 4096.


## Versions comparison ##

| Version |   Time   |  Memory  |
| ------- | -------- | -------- |
|  0.1.0  | 11m6.686s| 119.53MB |
|  0.1.1  | 0m56.593s| 119.53MB |
|  0.2.0  | 1m1.163s |  59.44MB |
|  0.2.1  | 0m9.645s |  59.44MB |
|  0.2.2  | 0m14.078s|  26.87MB |


## Memory usage ##
Memory usage was measured by this script.
```bash
#!/usr/bin/env bash

## Print header
echo -e "Size\tResid.\tShared\tData\t%"

pageSize=$(getconf PAGE_SIZE)
max=0

while [ 1 ]; do
    ## Get the PID of the process name given as argument 1
    pidno=`pgrep $1`

    ## If the process is running, print the memory usage
    if [ -e /proc/$pidno/statm ]; then
        ## Get the memory info
        vals=`cat /proc/$pidno/statm`

        ## Count totalMemory usage
        totalVM=`echo $vals $pageSize | awk '{print $1*$8}'`

        if [[ $totalVM -gt $max ]]; then
            max=$totalVM
        fi
    ## If the process is not running
    else
        echo -e "$max"
        exit
    fi
done
```
