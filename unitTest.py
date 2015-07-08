import unittest
import datetime
from dbTableCopier import copyTable


class DbStub(object):
    def __init__(self):
        self.cursorWasCalled = 0

    def cursor(self):
        if self.cursorWasCalled == 0:
            self.cursorWasCalled = 1
            self.cur = CursorStub1()
        else:
            self.cur = CursorStub2()
        return self.cur

    def close(self):
        pass

    def commit(self):
        pass


class CursorStub1(object):
    def __init__(self):
        self.inserts = []
        self.selectWasCalled = 0
        self.fetchWasCalled = 0

    def execute(self, query):
        if query[:13] == 'SELECT * FROM':
            self.selectWasCalled = 1

        if query[:6] == 'INSERT':
            self.inserts.append(query)

    def fetchall(self):
        if self.selectWasCalled:
            rows = []
            if self.fetchWasCalled == 0:
                self.fetchWasCalled = 1
                rows = [
                    (10001L, 'Senior Engineer',
                        datetime.date(1986, 6, 26), datetime.date(9999, 1, 1)),
                    (10002L, 'Staff',
                        datetime.date(1996, 8, 3), datetime.date(9999, 1, 1)),
                    (10004L, 'Engineer',
                        datetime.date(1986, 12, 1), datetime.date(1995, 12, 1))]
            return rows


class CursorStub2(object):
    def execute(self, query):
        pass

    def fetchall(self):
        return []


class TestDbTableCopier(unittest.TestCase):
    def setUp(self):
        self.sourceDb = DbStub()
        self.destinationDb = DbStub()

    def test_copyTable(self):
        copyTable('titles', self.sourceDb, self.destinationDb)

        insert = 'INSERT INTO titles values' + \
            '(10001,"Senior Engineer","1986-06-26","9999-01-01"),' + \
            '(10002,"Staff","1996-08-03","9999-01-01"),' + \
            '(10004,"Engineer","1986-12-01","1995-12-01")'

        self.assertEqual(self.destinationDb.cur.inserts[0], insert)


if __name__ == '__main__':
    unittest.main()
