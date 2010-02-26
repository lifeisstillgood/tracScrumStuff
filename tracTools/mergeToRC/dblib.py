#!/usr/local/bin/python

'''
Dumb lib fro dealing with trac

ticketchange class
history of changes
ticket itself


This should be using SQLAlchemy right now

'''
import pgdb # import used DB-API 2 module
import pg #holds error classes for pgdb.  Not sure why its split up
from DBUtils.PersistentDB import PersistentDB
from DBUtils.PooledDB import PooledDB
import time
import sys

#### dbstub
class PoolStub(object):
    '''stub for offline use of Pool '''
    def __init__(self):
        pass
    def connection(self):
        return ConnStub()

class ConnStub(object):
    def __init__(self):
        pass
    def cursor(self):
        return CursorStub()

class CursorStub(object):
    def __init__(self):
        pass
    def execute(self, SQL):
        pass
    def fetchall(self):
        #return a fake row set from a fake SQL query.
        return [

[3671], [3963], [3967], [3990], [3983], [3991], [3845], [3961], [3838], [3999], [3888], [3879], [3791], [4006], [3986], [3003], [3414], [4000], [3976], [3975], [3846], [2537], [3705], [3988], [4007], [4014], [3916], [3989], [4004], [3219], [4008], [3877], [3987], [3994], [3993], [4011], [3943], [3942], [3981], [3853], [2552], [4034], [3554], [3328], [3811], [4019], [4009], [4003], [4036], [4035], [3835], [4037], [3813], [3855], [3998], [4039], [4018], [3892], [3806], [3411], [3933], [3903]
               ]

class dblibError(Exception):
    pass

def set_module_globals():
    global pool
    _host = conf._host
    _database= conf._database
    _user = conf._user
    _password = conf._password



    if OFFLINE:
        pool = PoolStub()
    else: 
        try:
            pool = PooledDB(pgdb, 5, database=_database, 
                            user=_user, 
                            password=_password, 
                            host = _host)

        except pg.InternalError, e:
            raise dblibError("You have failed to connect to a dbase.   Perhaps you want to set OFFLINE \
                    to True, in order to use stubs.  Following was raised: " + str(e) )



def time2sse(timestr):
    '''convert time str (ISO) into Seconds Since Epoch

    trac annoingly uses SSE INTs for timestamps
    I will assume UTC
    I need to get better at date and time zones


    >>> time2sse('20090101')
    1230768000.0
    
    '''
    t = time.strptime(timestr, '%Y%m%d')    
    sse = time.mktime(t)
    return sse


def get_conn():
    """Return a db connection to the database 

      - but it is persisted so this can be called
       from anywhere"""
    db = pool.connection()
    return db


class tkt_history(object):
    '''Information on the history of a trac ticket '''
    
    def __init__(self, ticket_id, conn):
        '''Open up and grab all history for this tkt '''
        historySQL = """SELECT * from  ticket_change tch
                        where tch.ticket = %s
                        ORDER BY tch.time ASC;"""
        c = conn.cursor()
        c.execute(historySQL  % ticket_id)
        rs = c.fetchall()
        hdr = ['id','time','author','field','oldvalue','newvalue']
        self.rset = []
        for row in rs:
            self.rset.append(dict(zip(hdr, row)))
        
        c.close()

    def status_on_date(self, field, sse_time):
        '''Given a field, and a time, return the value of that field
           at the time specified
           Basically, find the most recent value for 'field' that was not changed after
           sec since epoch time'''
        
        filtered_by_field = [r for r in self.rset if r['field'] == field]
        filtered_by_time = [r['newvalue'] for r in filtered_by_field
                             if r['time'] <= sse_time]
        if len(   filtered_by_time) == 0:
            return None
        return filtered_by_time[-1:][0]

### Always run these
OFFLINE=False
pool = None
set_module_globals()
#### DO not think this is right. But not seeing a better way




if __name__ == '__main__':
    import doctest
    doctest.testmod()        
        
        
                    
