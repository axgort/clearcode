import unittest
import datetime
from dbTableCopier import copyTable


class DbStub(object):
    def cursor(self):
        self.cur = CursorStub()
        return self.cur

    def close(self):
        pass

    def commit(self):
        pass


class CursorStub(object):
    def __init__(self):
        self.inserts = []
        self.selectWasCalled = 0
        self.fetchWasCalled = 0

    def execute(self, query):
        if query[:13] == 'SELECT * FROM':
            self.selectWasCalled = 1

        if query[:6] == 'INSERT':
            self.inserts.append(query)

    def fetchmany(self, size):
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


class TestDbTableCopier(unittest.TestCase):
    def setUp(self):
        self.sourceDb = DbStub()
        self.destinationDb = DbStub()

    def test_copyTable(self):
        copyTable('titles', self.sourceDb, self.destinationDb)

        inserts = ['INSERT INTO titles values(10001,"Senior Engineer",\
"1986-06-26","9999-01-01")',
                   'INSERT INTO titles values(10002,"Staff",\
"1996-08-03","9999-01-01")',
                   'INSERT INTO titles values(10004,"Engineer",\
"1986-12-01","1995-12-01")']

        self.assertEqual(self.destinationDb.cur.inserts[0], inserts[0])
        self.assertEqual(self.destinationDb.cur.inserts[1], inserts[1])
        self.assertEqual(self.destinationDb.cur.inserts[2], inserts[2])


if __name__ == '__main__':
    unittest.main()
