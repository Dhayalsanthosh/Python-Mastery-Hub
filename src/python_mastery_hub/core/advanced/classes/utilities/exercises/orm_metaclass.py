"""
ORM Metaclass Exercise Implementation.

This module provides a metaclass exercise for automatically generating
database table schemas and ORM functionality.
"""

import re
from typing import Dict, Any, Type, Optional, List


class ORMMetaclassExercise:
    """Exercise for creating an ORM metaclass that generates database schemas."""
    
    def __init__(self):
        self.title = "ORM Table Creator"
        self.description = "Create a metaclass that automatically generates database table schemas"
        self.difficulty = "expert"
    
    def get_instructions(self) -> str:
        """Return exercise instructions."""
        return """
        Create a metaclass that automatically generates database table schemas:
        
        1. Analyze class attributes to identify field types
        2. Generate SQL CREATE TABLE statements automatically
        3. Add field validation and type mapping
        4. Implement automatic primary key handling
        5. Support foreign key relationships
        6. Add methods for basic CRUD operations
        7. Maintain a registry of all model classes
        8. Provide introspection capabilities
        """
    
    def get_tasks(self) -> List[str]:
        """Return list of specific tasks."""
        return [
            "Create a metaclass that analyzes class attributes",
            "Generate SQL CREATE TABLE statements automatically", 
            "Add field validation and type mapping",
            "Implement automatic primary key and relationship handling",
            "Add methods for basic CRUD operations",
            "Maintain a registry of model classes",
            "Support field constraints and validation",
            "Provide model introspection capabilities"
        ]
    
    def get_starter_code(self) -> str:
        """Return starter code template."""
        return '''
class FieldType:
    """Base class for field types."""
    def __init__(self, **kwargs):
        self.kwargs = kwargs

class CharField(FieldType):
    def __init__(self, max_length=255, **kwargs):
        super().__init__(**kwargs)
        self.max_length = max_length

class IntegerField(FieldType):
    pass

class ModelMeta(type):
    """Metaclass for ORM models."""
    
    def __new__(mcs, name, bases, attrs):
        # TODO: Analyze fields and generate schema
        pass

class Model(metaclass=ModelMeta):
    """Base model class."""
    pass
'''
    
    def get_solution(self) -> str:
        """Return complete solution."""
        return '''
import re
from typing import Dict, Any, Type, Optional, List, Union
from datetime import datetime

class FieldType:
    """Base class for field types."""
    
    def __init__(self, primary_key=False, null=True, default=None, unique=False, 
                 validators=None, help_text=""):
        self.primary_key = primary_key
        self.null = null
        self.default = default
        self.unique = unique
        self.validators = validators or []
        self.help_text = help_text
        self.name = None  # Set by __set_name__
    
    def __set_name__(self, owner, name):
        """Called when field is assigned to a class."""
        self.name = name
    
    def to_sql(self) -> str:
        """Convert field to SQL column definition."""
        raise NotImplementedError(f"to_sql not implemented for {type(self).__name__}")
    
    def validate(self, value) -> bool:
        """Validate field value."""
        if value is None:
            return self.null
        
        # Run custom validators
        for validator in self.validators:
            if not validator(value):
                return False
        
        return True
    
    def clean(self, value):
        """Clean and transform value."""
        return value

class CharField(FieldType):
    """Character field with max length constraint."""
    
    def __init__(self, max_length=255, **kwargs):
        super().__init__(**kwargs)
        self.max_length = max_length
    
    def to_sql(self) -> str:
        sql = f"VARCHAR({self.max_length})"
        if self.primary_key:
            sql += " PRIMARY KEY"
        if not self.null:
            sql += " NOT NULL"
        if self.unique and not self.primary_key:
            sql += " UNIQUE"
        if self.default is not None:
            sql += f" DEFAULT '{self.default}'"
        return sql
    
    def validate(self, value) -> bool:
        if not super().validate(value):
            return False
        if value is not None and len(str(value)) > self.max_length:
            return False
        return True
    
    def clean(self, value):
        return str(value).strip() if value is not None else value

class IntegerField(FieldType):
    """Integer field with optional auto-increment."""
    
    def __init__(self, auto_increment=False, min_value=None, max_value=None, **kwargs):
        super().__init__(**kwargs)
        self.auto_increment = auto_increment
        self.min_value = min_value
        self.max_value = max_value
    
    def to_sql(self) -> str:
        sql = "INTEGER"
        if self.auto_increment:
            sql += " AUTO_INCREMENT"
        if self.primary_key:
            sql += " PRIMARY KEY"
        if not self.null:
            sql += " NOT NULL"
        if self.unique and not self.primary_key:
            sql += " UNIQUE"
        if self.default is not None:
            sql += f" DEFAULT {self.default}"
        return sql
    
    def validate(self, value) -> bool:
        if not super().validate(value):
            return False
        if value is not None:
            try:
                int_value = int(value)
                if self.min_value is not None and int_value < self.min_value:
                    return False
                if self.max_value is not None and int_value > self.max_value:
                    return False
            except (ValueError, TypeError):
                return False
        return True
    
    def clean(self, value):
        return int(value) if value is not None else value

class FloatField(FieldType):
    """Floating point number field."""
    
    def __init__(self, precision=None, scale=None, **kwargs):
        super().__init__(**kwargs)
        self.precision = precision
        self.scale = scale
    
    def to_sql(self) -> str:
        if self.precision and self.scale:
            sql = f"DECIMAL({self.precision},{self.scale})"
        else:
            sql = "FLOAT"
        
        if self.primary_key:
            sql += " PRIMARY KEY"
        if not self.null:
            sql += " NOT NULL"
        if self.default is not None:
            sql += f" DEFAULT {self.default}"
        return sql
    
    def validate(self, value) -> bool:
        if not super().validate(value):
            return False
        if value is not None:
            try:
                float(value)
            except (ValueError, TypeError):
                return False
        return True
    
    def clean(self, value):
        return float(value) if value is not None else value

class BooleanField(FieldType):
    """Boolean field."""
    
    def to_sql(self) -> str:
        sql = "BOOLEAN"
        if not self.null:
            sql += " NOT NULL"
        if self.default is not None:
            sql += f" DEFAULT {self.default}"
        return sql
    
    def validate(self, value) -> bool:
        if not super().validate(value):
            return False
        return True
    
    def clean(self, value):
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', 'on')
        return bool(value) if value is not None else value

class DateTimeField(FieldType):
    """DateTime field with auto_now and auto_now_add options."""
    
    def __init__(self, auto_now=False, auto_now_add=False, **kwargs):
        super().__init__(**kwargs)
        self.auto_now = auto_now
        self.auto_now_add = auto_now_add
    
    def to_sql(self) -> str:
        sql = "DATETIME"
        if not self.null:
            sql += " NOT NULL"
        if self.default is not None:
            sql += f" DEFAULT '{self.default}'"
        elif self.auto_now_add:
            sql += " DEFAULT CURRENT_TIMESTAMP"
        return sql

class ForeignKey(FieldType):
    """Foreign key field referencing another table."""
    
    def __init__(self, to_table: str, on_delete="CASCADE", **kwargs):
        super().__init__(**kwargs)
        self.to_table = to_table
        self.on_delete = on_delete
    
    def to_sql(self) -> str:
        sql = "INTEGER"
        if not self.null:
            sql += " NOT NULL"
        sql += f" REFERENCES {self.to_table}(id)"
        if self.on_delete:
            sql += f" ON DELETE {self.on_delete}"
        return sql

class ModelMeta(type):
    """Metaclass for ORM models that generates database schemas."""
    
    registry: Dict[str, Type] = {}
    
    def __new__(mcs, name, bases, attrs):
        # Don't process the base Model class
        if name == 'Model':
            return super().__new__(mcs, name, bases, attrs)
        
        # Extract fields from class attributes
        fields = {}
        for attr_name, attr_value in list(attrs.items()):
            if isinstance(attr_value, FieldType):
                fields[attr_name] = attr_value
                # Remove field definitions from class attributes
                del attrs[attr_name]
        
        # Inherit fields from parent classes
        for base in bases:
            if hasattr(base, '_fields'):
                for field_name, field in base._fields.items():
                    if field_name not in fields:
                        fields[field_name] = field
        
        # Ensure there's a primary key
        if not any(field.primary_key for field in fields.values()):
            fields['id'] = IntegerField(primary_key=True, auto_increment=True, null=False)
        
        # Store fields and metadata
        attrs['_fields'] = fields
        attrs['_table_name'] = mcs._generate_table_name(name)
        attrs['_meta'] = {
            'model_name': name,
            'table_name': mcs._generate_table_name(name),
            'fields': fields,
            'created_at': datetime.now()
        }
        
        # Create the class
        cls = super().__new__(mcs, name, bases, attrs)
        
        # Add dynamic methods
        mcs._add_crud_methods(cls)
        
        # Generate and store SQL schema
        cls._schema_sql = mcs._generate_schema(cls)
        
        # Register the model
        mcs.registry[name] = cls
        
        return cls
    
    @staticmethod
    def _generate_table_name(class_name: str) -> str:
        """Convert CamelCase class name to snake_case table name."""
        # Insert underscores before uppercase letters (except the first)
        table_name = re.sub(r'(?<!^)(?=[A-Z])', '_', class_name).lower()
        return table_name + 's'  # Pluralize
    
    @staticmethod
    def _generate_schema(cls) -> str:
        """Generate CREATE TABLE SQL for the model."""
        table_name = cls._table_name
        field_definitions = []
        
        for field_name, field in cls._fields.items():
            column_def = f"{field_name} {field.to_sql()}"
            field_definitions.append(column_def)
        
        sql = f"CREATE TABLE {table_name} (\\n"
        sql += ",\\n  ".join(f"  {field_def}" for field_def in field_definitions)
        sql += "\\n);"
        
        return sql
    
    @staticmethod
    def _add_crud_methods(cls):
        """Add CRUD methods to the model class."""
        
        def __init__(self, **kwargs):
            self._data = {}
            self._dirty_fields = set()
            self._is_new = True
            
            for field_name, field in self._fields.items():
                if field_name in kwargs:
                    if field.validate(kwargs[field_name]):
                        cleaned_value = field.clean(kwargs[field_name])
                        self._data[field_name] = cleaned_value
                    else:
                        raise ValueError(f"Invalid value for {field_name}: {kwargs[field_name]}")
                elif field.default is not None:
                    self._data[field_name] = field.default
                elif field.primary_key and hasattr(field, 'auto_increment') and field.auto_increment:
                    # Auto-increment fields will be set by the database
                    pass
                elif not field.null:
                    raise ValueError(f"Field {field_name} cannot be null")
        
        def __getattr__(self, name):
            if name in self._fields:
                return self._data.get(name)
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
        
        def __setattr__(self, name, value):
            if name.startswith('_') or name in ['_data', '_dirty_fields', '_is_new']:
                super(cls, self).__setattr__(name, value)
            elif name in self._fields:
                field = self._fields[name]
                if field.validate(value):
                    cleaned_value = field.clean(value)
                    self._data[name] = cleaned_value
                    if hasattr(self, '_dirty_fields'):
                        self._dirty_fields.add(name)
                else:
                    raise ValueError(f"Invalid value for {name}: {value}")
            else:
                raise AttributeError(f"'{type(self).__name__}' has no field '{name}'")
        
        def to_dict(self):
            """Convert model instance to dictionary."""
            return self._data.copy()
        
        def to_sql_insert(self):
            """Generate INSERT SQL for this instance."""
            fields = [k for k, v in self._data.items() if v is not None]
            values = [repr(self._data[k]) for k in fields]
            
            sql = f"INSERT INTO {self._table_name} ({', '.join(fields)}) "
            sql += f"VALUES ({', '.join(values)});"
            return sql
        
        def to_sql_update(self, where_clause: str = None):
            """Generate UPDATE SQL for this instance."""
            if not where_clause:
                pk_field = next((name for name, field in self._fields.items() if field.primary_key), 'id')
                pk_value = self._data.get(pk_field)
                if pk_value is None:
                    raise ValueError("Cannot update without primary key value")
                where_clause = f"{pk_field} = {repr(pk_value)}"
            
            updates = [f"{k} = {repr(v)}" for k, v in self._data.items() 
                      if v is not None and not self._fields[k].primary_key]
            
            sql = f"UPDATE {self._table_name} SET {', '.join(updates)} WHERE {where_clause};"
            return sql
        
        def save(self):
            """Save the model instance (INSERT or UPDATE)."""
            if self._is_new:
                sql = self.to_sql_insert()
                self._is_new = False
            else:
                sql = self.to_sql_update()
            
            self._dirty_fields.clear()
            return sql
        
        @classmethod
        def create_table(cls):
            """Return the CREATE TABLE SQL for this model."""
            return cls._schema_sql
        
        @classmethod
        def describe(cls):
            """Return a description of the model fields."""
            description = f"Model: {cls.__name__} (Table: {cls._table_name})\\n"
            description += f"Created: {cls._meta['created_at']}\\n"
            description += "Fields:\\n"
            
            for field_name, field in cls._fields.items():
                field_info = f"  {field_name}: {type(field).__name__}"
                
                if field.primary_key:
                    field_info += " (PK)"
                if not field.null:
                    field_info += " (NOT NULL)"
                if field.unique:
                    field_info += " (UNIQUE)"
                if field.default is not None:
                    field_info += f" DEFAULT={field.default}"
                if field.help_text:
                    field_info += f" - {field.help_text}"
                
                description += field_info + "\\n"
            
            return description
        
        @classmethod
        def get_field(cls, field_name: str):
            """Get field definition by name."""
            return cls._fields.get(field_name)
        
        @classmethod
        def get_fields(cls):
            """Get all field definitions."""
            return cls._fields.copy()
        
        @classmethod 
        def validate_data(cls, data: dict):
            """Validate a dictionary of data against model fields."""
            errors = {}
            
            for field_name, value in data.items():
                if field_name in cls._fields:
                    field = cls._fields[field_name]
                    if not field.validate(value):
                        errors[field_name] = f"Invalid value: {value}"
                else:
                    errors[field_name] = f"Unknown field: {field_name}"
            
            # Check required fields
            for field_name, field in cls._fields.items():
                if not field.null and field_name not in data and field.default is None:
                    errors[field_name] = "This field is required"
            
            return errors
        
        def is_valid(self):
            """Check if the current instance is valid."""
            errors = self.__class__.validate_data(self._data)
            return len(errors) == 0
        
        def __str__(self):
            fields_str = ", ".join(f"{k}={repr(v)}" for k, v in self._data.items())
            return f"{type(self).__name__}({fields_str})"
        
        def __repr__(self):
            return str(self)
        
        # Add methods to class
        cls.__init__ = __init__
        cls.__getattr__ = __getattr__
        cls.__setattr__ = __setattr__
        cls.to_dict = to_dict
        cls.to_sql_insert = to_sql_insert
        cls.to_sql_update = to_sql_update
        cls.save = save
        cls.create_table = classmethod(create_table)
        cls.describe = classmethod(describe)
        cls.get_field = classmethod(get_field)
        cls.get_fields = classmethod(get_fields)
        cls.validate_data = classmethod(validate_data)
        cls.is_valid = is_valid
        cls.__str__ = __str__
        cls.__repr__ = __repr__

class Model(metaclass=ModelMeta):
    """Base model class for ORM."""
    pass

def test_orm_metaclass():
    """Test the ORM metaclass implementation."""
    print("=== ORM Metaclass Test ===")
    
    # Define models
    class User(Model):
        username = CharField(max_length=50, unique=True, null=False, 
                           help_text="Unique username for login")
        email = CharField(max_length=100, unique=True, null=False,
                         validators=[lambda x: '@' in x])
        age = IntegerField(null=True, default=18, min_value=0, max_value=150)
        is_active = BooleanField(default=True, null=False)
        created_at = DateTimeField(auto_now_add=True)
    
    class Post(Model):
        title = CharField(max_length=200, null=False)
        content = CharField(max_length=1000)
        author_id = ForeignKey('users', null=False)
        views = IntegerField(default=0)
        rating = FloatField(precision=3, scale=2, default=0.0)
        published = BooleanField(default=False)
    
    # Show generated schemas
    print("\\n1. Generated Schemas:")
    print("User table schema:")
    print(User.create_table())
    
    print("\\nPost table schema:")
    print(Post.create_table())
    
    # Show model descriptions
    print("\\n2. Model Descriptions:")
    print(User.describe())
    print(Post.describe())
    
    # Test model creation and validation
    print("\\n3. Model Instance Tests:")
    try:
        user = User(username="alice", email="alice@example.com", age=25)
        print(f"Valid user: {user}")
        print(f"User dict: {user.to_dict()}")
        print(f"Is valid: {user.is_valid()}")
    except Exception as e:
        print(f"User creation failed: {e}")
    
    try:
        post = Post(title="My First Post", content="Hello World!", author_id=1, views=10)
        print(f"Valid post: {post}")
    except Exception as e:
        print(f"Post creation failed: {e}")
    
    # Test validation
    print("\\n4. Validation Tests:")
    try:
        invalid_user = User(username="a" * 100, email="invalid")  # Too long username, invalid email
    except ValueError as e:
        print(f"Expected validation error: {e}")
    
    # Test field access
    print("\\n5. Field Access Tests:")
    user.age = 30
    print(f"Updated age: {user.age}")
    
    try:
        user.age = "not_a_number"  # Should fail
    except ValueError as e:
        print(f"Expected type error: {e}")
    
    # Generate SQL
    print("\\n6. SQL Generation:")
    print("User INSERT:")
    print(user.to_sql_insert())
    
    print("\\nPost INSERT:")
    print(post.to_sql_insert())
    
    print("\\nUser UPDATE:")
    print(user.to_sql_update())
    
    # Test model registry
    print("\\n7. Model Registry:")
    print(f"Registered models: {list(ModelMeta.registry.keys())}")
    
    # Test field introspection
    print("\\n8. Field Introspection:")
    user_fields = User.get_fields()
    for name, field in user_fields.items():
        print(f"  {name}: {type(field).__name__} - {field.help_text}")
    
    # Test data validation
    print("\\n9. Data Validation:")
    test_data = {"username": "bob", "email": "invalid_email", "age": 200}
    errors = User.validate_data(test_data)
    if errors:
        print(f"Validation errors: {errors}")
    else:
        print("Data is valid")

if __name__ == "__main__":
    test_orm_metaclass()
'''
    
    def get_test_cases(self) -> List[Dict[str, str]]:
        """Return test cases for validation."""
        return [
            {
                "name": "Metaclass field detection",
                "test": "Verify metaclass correctly identifies and processes field types"
            },
            {
                "name": "SQL schema generation", 
                "test": "Verify CREATE TABLE statements are generated correctly"
            },
            {
                "name": "Field validation",
                "test": "Verify field constraints and validation work properly"
            },
            {
                "name": "CRUD operations",
                "test": "Verify INSERT, UPDATE SQL generation works"
            },
            {
                "name": "Model registry",
                "test": "Verify models are registered and accessible"
            },
            {
                "name": "Primary key handling",
                "test": "Verify automatic primary key creation"
            },
            {
                "name": "Foreign key relationships",
                "test": "Verify foreign key constraints are generated"
            },
            {
                "name": "Model introspection",
                "test": "Verify model metadata and field access work"
            }
        ]