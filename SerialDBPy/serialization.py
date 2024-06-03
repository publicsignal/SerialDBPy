from typing import Optional
from Serialization.query import iQuery    

import os
import uuid

class Serializable(object):

    """

    INFORMATION:
        Table-related actions should always be @classmethods, unless functionality would be significantly hindered
            Example: create_if_not_exists() should be called on a Class, not an instance of the Class

    :class_param default_middleware: Default SQL query middleware; Ex: [database].[middleware].[table] 
    :class_param default_server: Default SQL query server; Ex: [database].[middleware].[table] 
    :class_param key_types: Different types of keys: Primary Key (PK), Foreign Key (FK), Composite Key (CK)

    :param resource_server: Servername or Warehouse; str
    :param resource_db: Database name; str
    :param resource_table: table name; str
    :param resource_map: Dict holding the column names and their associated class variable names
    """

    IGNORE_UNDERSCORE_VARS = os.environ.get( 'IGNORE_UNDERSCORE_VARS',True )
    OVERRIDE_UNDERSCORE_WITH_PROPERTY = os.environ.get( 'OVERRIDE_UNDERSCORE_WITH_PROPERTY',True )
    SANITIZE_QUERIES = os.environ.get( 'SANITIZE_QUERIES',True ) # Sanitizes all SQL queries to prevent injection attacks
    USE_SLOTS = os.environ.get( 'USE_SLOTS',True )
    CREATE_UUID_IF_NONE = os.environ.get( 'CREATE_UUID_IF_NONE',True ) # Creates a Primary Key for the object in case there is not one already set
    OVERRIDE_REPR = os.environ.get( 'OVERRIDE_REPR',True ) # Creates a new __repr__ to convert instance to str version

    default_server = os.environ.get( 'default_server','' )
    default_middleware = os.environ.get( 'default_middleware','' )
    key_types = ('<pk>','<fk>','<ck>')

    __slots__ = '__dict__' if USE_SLOTS else None

    def __init__(
            self, 
            server_name:Optional[str] = default_server, 
            middleware_name:Optional[str] = default_server
        ):

        self.default_middleware = middleware_name
        self.default_server = server_name

    def _get_vars(self):

        server = getattr(self,'resource_server',Serializable.default_server)
        db = getattr(self,'resource_db',None)
        table = getattr(self,'resource_table',None)
        map = getattr(self,'resource_map',{})
        keys = [ key for key in map if key in Serializable.key_types ]

        _mapsize = len( map.keys() )

        if map is None or _mapsize == 0:

            # Let's do default mapping if no map is available
            map = { key:key for key,val in self.__dict__.items() }

        elif _mapsize == len( keys ) and len( keys ) > 0:

            # if map only contains valid key types
            
            _keys = { key:map.get( key,None ) for key in keys }

            if not Serializable.IGNORE_UNDERSCORE_VARS:

                map = { key:key for key,val in self.__dict__.items() }
                map = { **_keys,**map }

            elif Serializable.IGNORE_UNDERSCORE_VARS and not Serializable.OVERRIDE_UNDERSCORE_WITH_PROPERTY:

                map = { key:key for key,val in self.__dict__.items() if key[0] != '_' }
                map = { **_keys,**map }                
            
            elif Serializable.IGNORE_UNDERSCORE_VARS and Serializable.OVERRIDE_UNDERSCORE_WITH_PROPERTY:
                
                map = { key:key for key,val in self.__dict__.items() if key[0] != '_' }
                replaced_underscores = { key[1:]:key[1:] for key,val in self.__dict__.items() if key[0] == '_' }
                map = { **_keys,**map,**replaced_underscores }

        return server,db,table,map
    
    @classmethod
    def _get_class_vars(cls):

        server = getattr(cls,'resource_server',Serializable.default_server)
        db = getattr(cls,'resource_db',None)
        table = getattr(cls,'resource_table',None)
        map = getattr(cls,'resource_map',{})
        
        keys = [ key for key in map if key in Serializable.key_types ]

        instance = cls()
        _mapsize = len( map.keys() )

        if map is None or _mapsize == 0:

            # Let's do default mapping if no map is available
            map = { key:key for key,val in instance.__dict__.items() }

        elif _mapsize == len( keys ) and len( keys ) > 0:

            # if map only contains valid key types
            
            _keys = { key:map.get( key,None ) for key in keys }

            if not Serializable.IGNORE_UNDERSCORE_VARS:

                map = { key:key for key,val in instance.__dict__.items() }
                map = { **_keys,**map }

            elif Serializable.IGNORE_UNDERSCORE_VARS and not Serializable.OVERRIDE_UNDERSCORE_WITH_PROPERTY:

                map = { key:key for key,val in instance.__dict__.items() if key[0] != '_' }
                map = { **_keys,**map }                
            
            elif Serializable.IGNORE_UNDERSCORE_VARS and Serializable.OVERRIDE_UNDERSCORE_WITH_PROPERTY:
                
                map = { key:key for key,val in instance.__dict__.items() if key[0] != '_' }
                replaced_underscores = { key[1:]:key[1:] for key,val in instance.__dict__.items() if key[0] == '_' }
                map = { **_keys,**map,**replaced_underscores }

        return server,db,table,map
    
    def _valid_mapping(func):

        def is_usable(self,*args, **kwargs):

            try:
                
                server,db,table,map = self._get_vars()

                if None in [server,db,table]:
                    raise KeyError(f'No database mapping found for class type ({type(self)})')
                elif map == None:
                    raise KeyError(f'No column/class mapping found for class type ({type(self)})')
                else:
                    return func(self,*args, **kwargs)

            except KeyError as ClassException:
                raise KeyError(f'Unknown mapping error for instance of class type ({type(self)}):\n {ClassException}')
        
        return is_usable
    

    def _valid_class_mapping(func):

        def is_usable(cls,*args, **kwargs):

            try:
                
                server,db,table,map = cls._get_class_vars()

                if None in [server,db,table]:
                    raise KeyError(f'No database mapping found for class type ({(cls)})')
                elif map is None:
                    raise KeyError(f'No column/class mapping found for class type ({(cls)})')
                else:
                    return func(cls,*args, **kwargs)

            except KeyError as ClassException:
                raise KeyError(f'Unknown mapping error for instance of class type ({(cls)}):\n {ClassException}')
        
        return is_usable
        
    
    
    @staticmethod
    def _uuid( 
        length:int = 32, 
        hyphenate:bool = False, 
        hyphen_length:int = 4 
    ):
        
        
        """
        Generate a UUID (Universally Unique Identifier) as a string.

        Parameters:
            length (Optional[int]): The desired length of the UUID string. Defaults to 10.
            hyphenate (Optional[bool]): Whether to include hyphens in the UUID string. Defaults to True.
            hyphen_length (Optional[int]): The number of characters between hyphens in the UUID string.
                This parameter is only used when `hyphenate` is True. Defaults to 4.

        Returns:
            str: The generated UUID as a string.
        
        Note:
            The `length` parameter specifies the total length of the UUID, excluding hyphens.
            For example, if `length` is set to 10 and `hyphenate` is True, the UUID will have
            the format "XXXX-XXXXX" where 'X' represents hexadecimal characters.
            If `hyphenate` is False, the UUID will have no hyphens.
        """

        uuid_str = str(uuid.uuid4())

        if hyphenate:
            parts = [uuid_str[i:i + hyphen_length] for i in range(0, length, hyphen_length)]
            return '-'.join(parts)
        else:
            return uuid_str

    def _keys( self ):

        """
        Function that returns keys' col name, var name
        """

        server,db,table,map = self._get_vars()

        keys = {}

        for key in Serializable.key_types: # key = <pk> or <ck> or <fk> etc...

            column_name = map.get( key,None ) # Column Name
            var_name = map.get( column_name,None ) # Python Object's Name

            if isinstance( column_name,str ):

                keys[key] = var_name # sets col name = var name

            elif isinstance( column_name,tuple ) or isinstance( column_name,list ):

                for col in column_name:
                    keys[col] = var_name

        return keys

    @property
    @_valid_mapping
    def _key_clauses( self ):

        server,db,table,map = self._get_vars()

        keys = self._keys()
        clauses = [ f'{val} = \'{ getattr( self,map[val],None ) }\'' for key,val in keys.items() if key in Serializable.key_types ]

        return f' WHERE { " AND ".join( clauses ) }'

    @_valid_mapping
    def get_from_json( 
        self, 
        data:dict, 
        _map:Optional[dict] = None 
    ):

        """
        Obtains object in JSON form and serializes it

        :param data: JSON data
        :param _map: JSON dictionary mapping the input's keys to the target's keys; (optional)
        """

        server,db,table,map = self._get_vars()

        for key,val in data.items():

            _pk = map.get(str(key).lower()) if not _map else _map.get(str(key).lower()) # Re-mapped key
            
            if _pk is not None:
                setattr(self,_pk,val) # Set attr if exists
        
        return self
    
    @classmethod
    @_valid_class_mapping
    def truncate( cls ):
        
        """
        Truncates the associated table
        """

        server,db,table,map = cls._get_class_vars()

        sql = f'truncate table {server}.{cls.default_middleware}.{table};'
        iQuery().execute( sql=sql )

        return cls
    
    
    @classmethod
    @_valid_class_mapping
    def create_table( cls ):
        
        """
        Create table if it doesnt already exist
        """
        
        server,db,table,map = cls._get_class_vars()
        instance = cls()
        
        n_map = [ f'{key} {type(getattr( instance ))}' for key,val in map.items() if key not in Serializable.key_types ]
        columns = ','.join(n_map)

        sql = f'create table {db}.{Serializable.default_middleware}.{table} ({columns})'
        iQuery().execute( sql=sql )

        return cls
        
    @classmethod
    @_valid_class_mapping
    def drop( cls ):

        """
        Drops the table
        """

        server,db,table,map = cls._get_class_vars()

        if isinstance( table, str ) and isinstance(server,str):

            sql = f'drop table if exists {server}.{cls.default_middleware}.{table};'
            iQuery().execute( sql=sql )
        
        return cls


    @classmethod
    @_valid_mapping
    def get_from_csv( 
        cls, 
        csv:list, 
        dictionary:Optional[dict] = None 
    ):

        """
        Obtains object data from CSV array

        :param csv: List containing the header and one row containing data
        :param row_number: The number of the row to be accessed
        """

        map = dictionary or getattr( cls,'resource_map',{} )
        headers = [ map.get( column,column ) for column in csv[0].split( ',' ) ] # Adjust the headers for the class's resource map
        output = []

        for row in csv:

            cols = row.split( ',' )
            instance = cls()

            try:
                for col, col_index, in enumerate( cols ):
                    setattr( instance,headers[col_index],col )
                output.append( instance )
            except:
                pass
        
        return output
    
    @classmethod
    @_valid_mapping
    def get_all_from_query( cls,query:str ):
        
        rows = Serializable.query( sql=query )

        return [ cls().get_from_json( data=row ) for row in rows ]
    
    @_valid_mapping
    def get_all( self, **kwargs ):

        """
        Queries objects from db and serializes them into instances of the parent class
        Grabs all items

        if kwargs are found, use them as WHERE clauses
        """

        server,db,table,map = self._get_vars()

        n_map = [ f'{key} as {val}' for key,val in map.items() if key not in Serializable.key_types ]
        columns = ','.join(n_map)
        instances = []
        sql = f'select distinct {columns} from {self.resource_db}.{Serializable.default_middleware}.{self.resource_table}'

        if len( kwargs.items() ) > 0:
            sql += f' WHERE {Serializable._generate_sql_clauses( filters=kwargs.items() )}'
        
        resp = iQuery( ).execute(sql=sql)

        for item in resp:
            
            instance = self.__class__( self )

            for key,val in item.items():

                if Serializable.OVERRIDE_UNDERSCORE_WITH_PROPERTY and hasattr( instance,f'_{key}'.lower() ):
                    setattr(instance, f'_{key}'.lower() ,val)
                else:
                    setattr(instance, f'{key}'.lower() ,val)

            instances.append( instance )
           
        return instances
    
    @_valid_mapping
    def get( self, **kwargs ):

        """
        Queries object from db and serializes it into an instance of the parent class
        Limited to one item

        if kwargs are found, use them as WHERE clauses
        """

        server,db,table,map = self._get_vars()

        n_map = [ f'{key} as {val}' for key,val in map.items() if key not in Serializable.key_types ]
        columns = ','.join(n_map)
        
        sql = f'select top 1 {columns} from {db}.{Serializable.default_middleware}.{table}'
        sql += f' WHERE {Serializable._generate_sql_clauses( filters=kwargs.items() )}' if len( kwargs.items() ) > 0 else self._key_clauses

        try:
            resp = iQuery( ).execute(sql=sql)
        except Exception as SQLException:
            resp = []

        if not isinstance( resp,list ) or ( isinstance( resp,list ) and len(resp) < 1 ) or ( isinstance( resp,list ) and len( resp ) > 0 and not isinstance( resp[0],dict ) ):
            return self

        for key,val in resp[0].items():

            if Serializable.OVERRIDE_UNDERSCORE_WITH_PROPERTY and hasattr( self,f'_{key}'.lower() ):
                setattr(self, f'_{key}'.lower() ,val)
            else:
                setattr(self, f'{key}'.lower() ,val)

            
        return self

    @_valid_mapping
    def serialize_to_html( self, html:str = None ):

        """
        Pivots instance of class into HTML target

        :param html: The HTML to which we will serialize
        """

        server,db,table,map = self._get_vars()
        
        vars = [ val for key,val in map.items() if key not in Serializable.key_types ]
        override = lambda a : a if a not in vars else getattr( self,a,a )
        new_html = html

        for var in vars:

            new_html = new_html.replace( f'@{var}@', str( override( var ) ) )

        return new_html
    
    @_valid_mapping
    def serialize_to_json(self):

        """
        Pivots class object into JSON object

        :param map: uses the resource map within the class 
        :ret dict: returns variables from map with their instance's name (not DB column names)
        """

        server,db,table,map = self._get_vars()

        output = {}

        for key,val in map.items():

            output[val] = getattr( self,val,None )

        return output

    @_valid_mapping
    def delete( self,**kwargs ):

        """
        Deletes the instance from the database
        """

        server,db,table,map = self._get_vars()
        
        if not kwargs:

            sql = f'delete from {db}.{Serializable.default_middleware}.{table} {self._key_clauses}'
            iQuery().execute( sql=sql )
            return self

        else:

            clauses = [ f'{key} = {val}' for key,val in kwargs.items() ]
            sql = f'delete from {db}.{Serializable.default_middleware}.{table} where { " AND ".join( clauses ) }'
            iQuery().execute( sql=sql )

            return self

    @_valid_mapping
    def insert(self):

        """
        Inserts valid instance of a class into the database
        
        1) Converts map to '' as [column_name] in sql structure
        2) Creates tuple of column names in order ([COL1], [COL2])
        3) create final query 'insert into {db_name} ({tuple}) select ','.join(map)' 
        """

        server,db,table,map = self._get_vars()

        column_name = map.get( '<pk>',None ) # Get primary key
        var_name = map.get( column_name,None ) # Python Object's Name

        if self.CREATE_UUID_IF_NONE and getattr( self,column_name,None ) is None:
            setattr( self,column_name,self._uuid() )

        iQuery().execute(sql=self.serialize_to_sql()) 

        return self
    
    @_valid_mapping
    def update(self):

        """
        Upserts valid instance of a class into the database
        
        1) Converts map to '' as [column_name] in sql structure
        2) Creates tuple of column names in order ([COL1], [COL2])
        3) create final query 'insert into {db_name} ({tuple}) select ','.join(map)' 
        """

        server,db,table,map = self._get_vars()
        que = []

        for key,val in map.items():

            if key not in Serializable.key_types:

                _val = (f"{getattr(self,val,'')}").replace("'","\\'")
                que.append( f'{key} = \'{_val}\'' )

        val_sql = ', '.join(que)

        return iQuery().execute(sql=f'update {db}.{Serializable.default_middleware}.{table} set {val_sql} {self._key_clauses}') 
    
    @_valid_mapping
    def serialize_to_sql(self):

        """
        Creates a SQL statement to insert a valid instance of a class into the database
        
        1) Converts map to '' as [column_name] in sql structure
        2) Creates tuple of column names in order ([COL1], [COL2])
        3) create final query 'insert into {db_name} ({tuple}) select ','.join(map)' 
        """
        
        server,db,table,map = self._get_vars()
        n_map:list = []
        columns:list = []

        for key,val in map.items():

            if key not in Serializable.key_types:

                n_val = (f"{getattr(self,val,'')}").replace("'","\\'")
                if n_val != 'None':
                    n_map.append( f"'{n_val}'" )
                else:
                    n_map.append( "''" )
                columns.append(f"{key}") # key = col name; surround by '' 
        
        col_sql = ','.join(columns)
        val_sql = ','.join(n_map)

        return f'insert into {db}.{Serializable.default_middleware}.{table} ({col_sql}) values ({val_sql})'
        
    @_valid_mapping
    def generate_primary_key(self,length:int = 10):

        """
        Queries object from db and serializes it into an instance of the parent class
        """

        server,db,table,map = self._get_vars()

        for key,val in map.items():
            
            """
            generates primary keys
            """
            
            if key == '<pk>':

                setattr(self,str(key).lower(), Serializable._uuid( length=length ) )

        return self
    
    @staticmethod
    def _generate_sql_clauses( filters:dict ):

        clause_parts = []

        for key, val in filters:
            
            if isinstance(val, str):
                clause_parts.append(f"{key} = '{val}'")
            elif val is None:
                clause_parts.append(f"{key} is null")
            elif isinstance(val, int):
                clause_parts.append(f"{key} = {val}")
            elif isinstance(val, float):
                clause_parts.append(f"{key} = {val}")
            elif isinstance(val, bool):
                # Convert boolean value to 1 (True) or 0 (False)
                clause_parts.append(f"{key} = {1 if val == True else False }")
            elif isinstance(val, dict):
                if "between" in val:
                    start_date, end_date = val["between"]
                    clause_parts.append(f"{key} BETWEEN '{start_date}' AND '{end_date}'")
                elif "before" in val:
                    before_date = val["before"]
                    clause_parts.append(f"{key} < '{before_date}'")
                elif "after" in val:
                    after_date = val["after"]
                    clause_parts.append(f"{key} > '{after_date}'")

            elif isinstance(val, (list, tuple)):
                # Assuming val is a list of values for IN clause
                formatted_values = ", ".join([f"'{v}'" if isinstance(v, str) else str(v) for v in val])
                clause_parts.append(f"{key} IN ({formatted_values})")

        return ' AND '.join(clause_parts)

    def __eq__( self, other ):

        return None