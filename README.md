## SerialDBPy README
# Overview
SerialDBPy is a lightweight Python ORM library meant to handle basic CRUD operations between Python objects and SQL Databases.

**NOTE**: Queries are not yet parameterized, and therefore cannot prevent SQL injection attacks. Fixes are being pushed shortly!

# Features
- Serialize class instances to a database
- Deserialize database records into class instances
- Automatically handle primary keys with UUID generation
- Support for custom mappings between class attributes and database columns
- Flexible configuration through environment variables

## Usage
# Basic Usage
To use SerialDBPy, simply inherit it in your class and call the relevant methods for serialization and deserialization.

```python
import os
from SerialDBPy import Serializable

os.environ['default_server'] = 'server_containing_databases'
os.environ['default_middleware'] = 'default_schema' # Example: SELECT TOP 100 * FROM [db_name].[default_schema].[table];
os.environ['SerialDBPy_ACCOUNT'] = 'SNOWFLAKE_ACCOUNT'
os.environ['SerialDBPy_PSWD'] = 'SNOWFLAKE_ACCOUNT_PSWD'
os.environ['SerialDBPy_user'] = 'SNOWFLAKE_USER'

class Person( Serializable ):
    
    resource_db = 'my_database' # Database where the associated table can be found
    resource_table = 'my_table' # Name of table
    resource_map = { 
        # Maps class variables to associated columns in a SQL table
        # pk = Primary Key; fk = Foreign Key
        # FORMAT: 'variable_name':'db_column_name'
        '<pk>':'id',
        'id':'id', # Optional when var name is the same as the associated column name
        'name':'name', # Optional when var name is the same as the associated column name
        'age':'age' # Optional when var name is the same as the associated column name
    }

    def __init__(self, name, age, height):
        
        self.id = None
        self.name = name
        self.age = age
        self.height = height
```

Using SerialDBPy using Python Dataclasses
```python
from SerialDBPy import Serializable
from typing import ClassVar
from dataclasses import dataclass
import os

os.environ['default_server'] = 'server_containing_databases'
os.environ['default_middleware'] = 'default_schema' # Example: SELECT TOP 100 * FROM [db_name].[default_schema].[table];
os.environ['SerialDBPy_ACCOUNT'] = 'SNOWFLAKE_ACCOUNT'
os.environ['SerialDBPy_PSWD'] = 'SNOWFLAKE_ACCOUNT_PSWD'
os.environ['SerialDBPy_user'] = 'SNOWFLAKE_USER'


@dataclass
class Person( Serializable ):

    resource_db:ClassVar[str] = 'my_database'
    resource_table:ClassVar[str] = 'my_table'

    resource_map:ClassVar[dict] = {
        '<pk>':'id'
    }

    id:str
    name:str
    age:int
    height:int

person = Person( name='John Doe' )
print( person.serialize_to_json() )
```

```python
# Create and insert a new person
person = Person(name="John Doe", age=30, height=200)
person.id = person._uuid()
person.insert()

# Updates the person's row in our DB
person.name = 'Jane Doe'
person.age = 27
person.height = 150
person.update()

# Converts the instance of Person into JSON format
print( person.serialize_to_json() )
```
```python
# Retrieve a person from the database
# Gets John Doe from our database (I always recommend getting by the Primary Key, but either way works)
# the kwargs on a .get() are akin to a SQL where clause
person = Person()
person.get(name="John Doe") 
```
```python
# Deletes a person from the database
person = Person().get(name="John Doe", age=30, height=200)
person.delete()
```
```python
""" Table-related actions """

# Truncates the table associated with the Person class
Person.truncate()

# Drops the table associated with the Person class
Person.drop()

# Creates a new table given the schema explicitly or implicitly defined by the resource_map
Person.create_table()
```

# Configuration
## SerialDBPy allows configuration through environment variables:

- IGNORE_UNDERSCORE_VARS: Ignore variables starting with an underscore (default: True)
- OVERRIDE_UNDERSCORE_WITH_PROPERTY: Override underscore variables with properties (default: True)
- USE_SLOTS: Use __slots__ for memory optimization (default: True)
- CREATE_UUID_IF_NONE: Create a UUID primary key if none is set (default: True)
- OVERRIDE_REPR: Override the __repr__ method for string representation (default: True)
- default_server: Default SQL query server **REQUIRED**
- default_middleware: Default SQL query middleware **REQUIRED**

# Methods
## Instance Methods
- insert(): Inserts the instance into the database.
- update(): Updates the instance in the database.
- delete(**kwargs): Deletes the instance from the database.
- get(**kwargs): Retrieves a single instance from the database.
- get_all(**kwargs): Retrieves all instances from the database.
- serialize_to_json(): Converts the instance to a JSON object.

## Class Methods
- truncate(): Truncates the associated table.
- get_from_csv(csv, dictionary): Deserializes objects from a CSV array.
- get_all_from_query(query): Deserializes objects from a SQL query.

License
SerialDBPy is licensed under the MIT License. See the LICENSE file for more details.

