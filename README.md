## SerialDBPy README
# Overview
SerialDBPy is a lightweight Python ORM library meant to handle basic CRUD operations between Python objects and SQL Databases.

# Features
- Serialize class instances to a database
- Deserialize database records into class instances
- Automatically handle primary keys with UUID generation
- Support for custom mappings between class attributes and database columns
- SQL injection prevention through query sanitization
- Flexible configuration through environment variables

## Usage
# Basic Usage
To use SerialDBPy, simply inherit it in your class and call the relevant methods for serialization and deserialization.

```python
from serialdbpy import SerialDBPy

os.environ['default_server'] = 'server_containing_databases'
os.environ['default_middleware'] = 'default_schema' # Example: SELECT TOP 100 * FROM [db_name].[default_schema].[table];
os.environ['SerialDBPy_ACCOUNT'] = 'SNOWFLAKE_ACCOUNT'
os.environ['SerialDBPy_PSWD'] = 'SNOWFLAKE_ACCOUNT_PSWD'
os.environ['SerialDBPy_user'] = 'SNOWFLAKE_USER'

class Person( SerialDBPy ):
    
    resource_db = 'my_database' # Database where the associated table can be found
    resource_table = 'my_table' # Name of table
    resource_map = { 
        # Maps class variables to associated columns in a SQL table
        # pk = Primary Key; fk = Foreign Key
        # FORMAT: 'variable_name':'db_column_name'
        '<pk>':'id',
        'id':'id',
        'name':'name',
        'age':'age'
    }

    def __init__(self, name, age, height):
        
        self.id = None
        self.name = name
        self.age = age
        self.height = height
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
# Truncates the table associated with the Person class
Person.truncate()
```
# Configuration
## SerialDBPy allows configuration through environment variables:

- IGNORE_UNDERSCORE_VARS: Ignore variables starting with an underscore (default: True)
- OVERRIDE_UNDERSCORE_WITH_PROPERTY: Override underscore variables with properties (default: True)
- SANITIZE_QUERIES: Sanitize all SQL queries to prevent injection attacks (default: True)
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

