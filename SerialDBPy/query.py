from typing import Any, Optional
from snowflake.connector import DictCursor

import snowflake.connector
import os

class Connection(object):

    account = os.environ.get( 'SerialDBPy_ACCOUNT','' )
    pswd = os.environ.get( 'SerialDBPy_PSWD','' )
    user = os.environ.get( 'SerialDBPy_user','' )
    params = {'CLIENT_SESSION_KEEP_ALIVE':True}

    connector = snowflake.connector.connect( user=user,password=pswd,account=account,session_parameters = params )

    @classmethod
    def reset_connection(cls):

        Connection.connector = snowflake.connector.connect( user=cls.user,password=cls.pswd,account=cls.account,session_parameters = cls.params )


class iQuery(Connection):

    timeout = 5

    def __init__(self):

        self.cursor = None
        self.query_id = None
        
    def handle_cursor(func):

        def window(self,*args, **kwargs):
            
            try:
                self.cursor = Connection.connector.cursor(DictCursor)
            except:
                Connection.reset_connection()
                self.cursor = Connection.connector.cursor(DictCursor)
            
            _r = func(self,*args, **kwargs)
            self.cursor.close()
            
            return _r
        
        return window
    
    @handle_cursor
    def execute(self,sql:str = None,timeout:int = timeout ):

        #print( sql )
        
        return self.cursor.execute(sql,timeout=timeout).fetchall()
    
    @handle_cursor
    def async_execute(self,sql:str = None,timeout:int=timeout):

        """
        :return (str): Functions returns query ID
        """

        _q = self.cursor.execute_async(sql,timeout=timeout)
        self.query_id = self.cursor.sfqid

        return self.query_id

    @handle_cursor
    def async_results(self,query_id = None):

        """
        Fetches query results from query ID
        
        :ret dataframe: function returns a dataframe of the query's results
        """

        self.cursor.get_results_from_sfqid( query_id )
        return self.cursor.fetchall()