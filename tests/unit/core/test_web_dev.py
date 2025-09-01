# tests/unit/core/test_web_dev.py
# Unit tests for web development concepts and exercises

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import tempfile
import os

# Import modules under test (adjust based on your actual structure)
try:
    from src.core.web_dev import (
        FlaskExercise,
        FastAPIExercise,
        HTMLExercise,
        CSSExercise,
        JavaScriptExercise,
        RESTAPIExercise
    )
    from src.core.evaluators import WebDevEvaluator
except ImportError:
    # Mock classes for when actual modules don't exist
    class FlaskExercise:
        pass
    class FastAPIExercise:
        pass
    class HTMLExercise:
        pass
    class CSSExercise:
        pass
    class JavaScriptExercise:
        pass
    class RESTAPIExercise:
        pass
    class WebDevEvaluator:
        pass


class TestFlaskExercises:
    """Test cases for Flask web development exercises."""
    
    def test_basic_flask_app(self):
        """Test basic Flask application creation."""
        code = '''
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello, World!"

@app.route('/api/users/<int:user_id>')
def get_user(user_id):
    return jsonify({
        "id": user_id,
        "name": f"User {user_id}",
        "email": f"user{user_id}@example.com"
    })

@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.get_json()
    return jsonify({
        "id": 123,
        "name": data.get("name"),
        "email": data.get("email"),
        "created": True
    }), 201

# Test the routes
with app.test_client() as client:
    # Test basic route
    response_hello = client.get('/')
    hello_data = response_hello.data.decode()
    hello_status = response_hello.status_code
    
    # Test parameterized route
    response_user = client.get('/api/users/42')
    user_data = response_user.get_json()
    user_status = response_user.status_code
    
    # Test POST route
    new_user = {"name": "Alice", "email": "alice@example.com"}
    response_create = client.post('/api/users', 
                                 data=json.dumps(new_user),
                                 content_type='application/json')
    create_data = response_create.get_json()
    create_status = response_create.status_code
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['hello_status'] == 200
        assert "Hello, World!" in globals_dict['hello_data']
        assert globals_dict['user_status'] == 200
        assert globals_dict['user_data']['id'] == 42
        assert globals_dict['create_status'] == 201
        assert globals_dict['create_data']['created'] is True
    
    def test_flask_with_templates(self):
        """Test Flask with template rendering."""
        code = '''
from flask import Flask, render_template_string

app = Flask(__name__)

# Simple template
template = """
<!DOCTYPE html>
<html>
<head><title>{{ title }}</title></head>
<body>
    <h1>{{ heading }}</h1>
    <ul>
    {% for item in items %}
        <li>{{ item }}</li>
    {% endfor %}
    </ul>
</body>
</html>
"""

@app.route('/page')
def render_page():
    return render_template_string(template,
                                title="Test Page",
                                heading="My Items",
                                items=["Item 1", "Item 2", "Item 3"])

# Test template rendering
with app.test_client() as client:
    response = client.get('/page')
    html_content = response.data.decode()
    status_code = response.status_code
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['status_code'] == 200
        assert "Test Page" in globals_dict['html_content']
        assert "My Items" in globals_dict['html_content']
        assert "Item 1" in globals_dict['html_content']
    
    def test_flask_error_handling(self):
        """Test Flask error handling."""
        code = '''
from flask import Flask, jsonify, abort

app = Flask(__name__)

@app.route('/api/users/<int:user_id>')
def get_user(user_id):
    if user_id < 1:
        abort(400)
    if user_id > 1000:
        abort(404)
    return jsonify({"id": user_id, "name": f"User {user_id}"})

@app.errorhandler(400)
def bad_request(error):
    return jsonify({"error": "Bad request"}), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "User not found"}), 404

# Test error handling
with app.test_client() as client:
    # Test bad request
    response_400 = client.get('/api/users/0')
    data_400 = response_400.get_json()
    status_400 = response_400.status_code
    
    # Test not found
    response_404 = client.get('/api/users/1001')
    data_404 = response_404.get_json()
    status_404 = response_404.status_code
    
    # Test valid request
    response_200 = client.get('/api/users/42')
    data_200 = response_200.get_json()
    status_200 = response_200.status_code
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['status_400'] == 400
        assert "Bad request" in globals_dict['data_400']['error']
        assert globals_dict['status_404'] == 404
        assert "not found" in globals_dict['data_404']['error']
        assert globals_dict['status_200'] == 200
        assert globals_dict['data_200']['id'] == 42


class TestFastAPIExercises:
    """Test cases for FastAPI web development exercises."""
    
    def test_basic_fastapi_app(self):
        """Test basic FastAPI application creation."""
        code = '''
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

class User(BaseModel):
    id: Optional[int] = None
    name: str
    email: str
    age: Optional[int] = None

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    age: Optional[int] = None
    created: bool = True

# In-memory storage
users_db = {}
next_id = 1

@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}

@app.get("/api/users/{user_id}")
def get_user(user_id: int):
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    return users_db[user_id]

@app.post("/api/users", response_model=UserResponse)
def create_user(user: User):
    global next_id
    user_data = user.dict()
    user_data["id"] = next_id
    user_data["created"] = True
    users_db[next_id] = user_data
    next_id += 1
    return user_data

@app.get("/api/users", response_model=List[UserResponse])
def list_users():
    return list(users_db.values())

# Test the API
client = TestClient(app)

# Test root endpoint
response_root = client.get("/")
root_data = response_root.json()
root_status = response_root.status_code

# Test creating user
new_user = {"name": "Alice", "email": "alice@example.com", "age": 30}
response_create = client.post("/api/users", json=new_user)
create_data = response_create.json()
create_status = response_create.status_code

# Test getting user
user_id = create_data["id"]
response_get = client.get(f"/api/users/{user_id}")
get_data = response_get.json()
get_status = response_get.status_code

# Test listing users
response_list = client.get("/api/users")
list_data = response_list.json()
list_status = response_list.status_code
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['root_status'] == 200
        assert "Hello, FastAPI!" in globals_dict['root_data']['message']
        assert globals_dict['create_status'] == 200
        assert globals_dict['create_data']['name'] == "Alice"
        assert globals_dict['get_status'] == 200
        assert globals_dict['get_data']['email'] == "alice@example.com"
        assert globals_dict['list_status'] == 200
        assert len(globals_dict['list_data']) == 1
    
    def test_fastapi_validation(self):
        """Test FastAPI request validation."""
        code = '''
from fastapi import FastAPI, HTTPException, Query, Path
from fastapi.testclient import TestClient
from pydantic import BaseModel, validator
from typing import Optional

app = FastAPI()

class UserCreate(BaseModel):
    name: str
    email: str
    age: int
    
    @validator('age')
    def validate_age(cls, v):
        if v < 0 or v > 150:
            raise ValueError('Age must be between 0 and 150')
        return v
    
    @validator('email')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('Invalid email format')
        return v

@app.post("/api/users")
def create_user(user: UserCreate):
    return {"message": "User created", "user": user.dict()}

@app.get("/api/users")
def list_users(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    name_filter: Optional[str] = Query(None, min_length=2)
):
    return {
        "page": page,
        "size": size,
        "name_filter": name_filter,
        "users": []
    }

@app.get("/api/users/{user_id}")
def get_user(user_id: int = Path(..., ge=1, description="User ID")):
    return {"user_id": user_id}

client = TestClient(app)

# Test valid user creation
valid_user = {"name": "Alice", "email": "alice@example.com", "age": 30}
response_valid = client.post("/api/users", json=valid_user)
valid_status = response_valid.status_code

# Test invalid age
invalid_age_user = {"name": "Bob", "email": "bob@example.com", "age": 200}
response_invalid_age = client.post("/api/users", json=invalid_age_user)
invalid_age_status = response_invalid_age.status_code

# Test invalid email
invalid_email_user = {"name": "Charlie", "email": "invalid-email", "age": 25}
response_invalid_email = client.post("/api/users", json=invalid_email_user)
invalid_email_status = response_invalid_email.status_code

# Test query parameters
response_query = client.get("/api/users?page=2&size=20&name_filter=alice")
query_data = response_query.json()
query_status = response_query.status_code
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['valid_status'] == 200
        assert globals_dict['invalid_age_status'] == 422  # Validation error
        assert globals_dict['invalid_email_status'] == 422  # Validation error
        assert globals_dict['query_status'] == 200
        assert globals_dict['query_data']['page'] == 2
        assert globals_dict['query_data']['size'] == 20


class TestHTMLCSSExercises:
    """Test cases for HTML and CSS exercises."""
    
    def test_html_structure_validation(self):
        """Test HTML structure validation."""
        code = '''
from bs4 import BeautifulSoup

def validate_html_structure(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    results = {
        'has_doctype': html_content.strip().startswith('<!DOCTYPE'),
        'has_html_tag': soup.html is not None,
        'has_head_tag': soup.head is not None,
        'has_body_tag': soup.body is not None,
        'has_title': soup.title is not None,
        'title_text': soup.title.string if soup.title else None
    }
    
    return results

# Test valid HTML
valid_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Test Page</title>
</head>
<body>
    <h1>Welcome</h1>
    <p>This is a test page.</p>
</body>
</html>
"""

# Test invalid HTML (missing doctype and title)
invalid_html = """
<html>
<head>
</head>
<body>
    <h1>Welcome</h1>
</body>
</html>
"""

valid_results = validate_html_structure(valid_html)
invalid_results = validate_html_structure(invalid_html)
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        valid = globals_dict['valid_results']
        invalid = globals_dict['invalid_results']
        
        assert valid['has_doctype'] is True
        assert valid['has_html_tag'] is True
        assert valid['has_title'] is True
        assert valid['title_text'] == "Test Page"
        
        assert invalid['has_doctype'] is False
        assert invalid['has_title'] is False
    
    def test_css_parsing_and_validation(self):
        """Test CSS parsing and validation."""
        code = '''
import re

def parse_css_rules(css_content):
    # Simple CSS parser for basic validation
    rules = []
    
    # Remove comments
    css_content = re.sub(r'/\\*.*?\\*/', '', css_content, flags=re.DOTALL)
    
    # Find CSS rules
    rule_pattern = r'([^{}]+)\\s*{([^{}]+)}'
    matches = re.findall(rule_pattern, css_content)
    
    for selector, declarations in matches:
        selector = selector.strip()
        
        # Parse declarations
        properties = {}
        for declaration in declarations.split(';'):
            if ':' in declaration:
                prop, value = declaration.split(':', 1)
                properties[prop.strip()] = value.strip()
        
        rules.append({
            'selector': selector,
            'properties': properties
        })
    
    return rules

def validate_css_properties(rules):
    valid_properties = {
        'color', 'background-color', 'font-size', 'margin', 'padding',
        'border', 'width', 'height', 'display', 'position', 'text-align'
    }
    
    validation_results = []
    
    for rule in rules:
        rule_validation = {
            'selector': rule['selector'],
            'valid_properties': [],
            'invalid_properties': []
        }
        
        for prop in rule['properties']:
            if prop in valid_properties:
                rule_validation['valid_properties'].append(prop)
            else:
                rule_validation['invalid_properties'].append(prop)
        
        validation_results.append(rule_validation)
    
    return validation_results

# Test CSS
test_css = """
body {
    margin: 0;
    padding: 20px;
    font-size: 16px;
    background-color: #f0f0f0;
}

.header {
    color: #333;
    text-align: center;
    invalid-property: value;
}

#content {
    width: 100%;
    height: auto;
}
"""

parsed_rules = parse_css_rules(test_css)
validation_results = validate_css_properties(parsed_rules)
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        rules = globals_dict['parsed_rules']
        validation = globals_dict['validation_results']
        
        assert len(rules) == 3  # body, .header, #content
        assert any(rule['selector'] == 'body' for rule in rules)
        assert any(rule['selector'] == '.header' for rule in rules)
        
        # Check validation results
        header_validation = next(v for v in validation if v['selector'] == '.header')
        assert 'color' in header_validation['valid_properties']
        assert 'invalid-property' in header_validation['invalid_properties']


class TestJavaScriptExercises:
    """Test cases for JavaScript-related exercises (using PyExecJS or similar)."""
    
    def test_javascript_syntax_validation(self):
        """Test JavaScript syntax validation."""
        code = '''
import re

def validate_javascript_syntax(js_code):
    """Basic JavaScript syntax validation."""
    issues = []
    
    # Check for basic syntax issues
    lines = js_code.split('\\n')
    
    for i, line in enumerate(lines, 1):
        line = line.strip()
        if not line or line.startswith('//'):
            continue
        
        # Check for missing semicolons (simple check)
        if (line.endswith(')') or 
            line.endswith(']') or 
            line.endswith('}')) and not line.endswith(';'):
            if not any(keyword in line for keyword in ['if', 'for', 'while', 'function', 'else']):
                issues.append(f"Line {i}: Missing semicolon")
        
        # Check for undefined variables (very basic)
        if 'undefined' in line:
            issues.append(f"Line {i}: Potential undefined variable")
        
        # Check for console.log (good practice check)
        if 'console.log' in line:
            issues.append(f"Line {i}: Console.log found (remove for production)")
    
    return {
        'is_valid': len(issues) == 0,
        'issues': issues,
        'total_lines': len([l for l in lines if l.strip()])
    }

# Test valid JavaScript
valid_js = """
function calculateSum(a, b) {
    return a + b;
}

const result = calculateSum(5, 3);
const message = `The result is ${result}`;
"""

# Test invalid JavaScript
invalid_js = """
function calculateSum(a, b) {
    return a + b
}

const result = calculateSum(5, 3)
console.log(result);
let x = undefined;
"""

valid_result = validate_javascript_syntax(valid_js)
invalid_result = validate_javascript_syntax(invalid_js)
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        valid = globals_dict['valid_result']
        invalid = globals_dict['invalid_result']
        
        assert valid['is_valid'] is True
        assert len(valid['issues']) == 0
        
        assert invalid['is_valid'] is False
        assert len(invalid['issues']) > 0
        assert any("semicolon" in issue for issue in invalid['issues'])
    
    def test_javascript_function_analysis(self):
        """Test JavaScript function analysis."""
        code = '''
import re

def analyze_javascript_functions(js_code):
    """Analyze JavaScript functions in code."""
    
    # Find function declarations
    function_pattern = r'function\\s+(\\w+)\\s*\\(([^)]*)\\)\\s*{'
    arrow_function_pattern = r'(const|let|var)\\s+(\\w+)\\s*=\\s*\\(([^)]*)\\)\\s*=>'
    
    functions = []
    
    # Regular function declarations
    for match in re.finditer(function_pattern, js_code):
        name = match.group(1)
        params = [p.strip() for p in match.group(2).split(',') if p.strip()]
        functions.append({
            'name': name,
            'type': 'declaration',
            'parameters': params,
            'parameter_count': len(params)
        })
    
    # Arrow functions
    for match in re.finditer(arrow_function_pattern, js_code):
        name = match.group(2)
        params = [p.strip() for p in match.group(3).split(',') if p.strip()]
        functions.append({
            'name': name,
            'type': 'arrow',
            'parameters': params,
            'parameter_count': len(params)
        })
    
    return {
        'functions': functions,
        'total_functions': len(functions),
        'has_arrow_functions': any(f['type'] == 'arrow' for f in functions)
    }

# Test JavaScript with different function types
test_js = """
function regularFunction(a, b, c) {
    return a + b + c;
}

const arrowFunction = (x, y) => {
    return x * y;
}

const singleParamArrow = value => value * 2;

function noParams() {
    console.log("No parameters");
}
"""

analysis_result = analyze_javascript_functions(test_js)
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        result = globals_dict['analysis_result']
        assert result['total_functions'] >= 2
        assert result['has_arrow_functions'] is True
        
        # Check for specific functions
        function_names = [f['name'] for f in result['functions']]
        assert 'regularFunction' in function_names
        assert 'arrowFunction' in function_names


class TestRESTAPIExercises:
    """Test cases for REST API design and implementation exercises."""
    
    def test_rest_api_design_principles(self):
        """Test REST API design principles validation."""
        code = '''
def validate_rest_endpoint(method, path, description=""):
    """Validate REST API endpoint against best practices."""
    issues = []
    
    # Check HTTP method usage
    valid_methods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']
    if method not in valid_methods:
        issues.append(f"Invalid HTTP method: {method}")
    
    # Check URL structure
    if not path.startswith('/'):
        issues.append("Path should start with /")
    
    # Check for proper resource naming
    path_parts = [p for p in path.split('/') if p]
    
    for part in path_parts:
        # Resources should be nouns, not verbs
        verbs = ['get', 'post', 'create', 'update', 'delete', 'fetch']
        if any(verb in part.lower() for verb in verbs):
            issues.append(f"Path contains verb '{part}' - use nouns for resources")
        
        # Should use plural nouns for collections
        if part and not part.startswith('{') and not part.endswith('s') and part.isalpha():
            issues.append(f"Resource '{part}' should be plural")
    
    # Check method-path combinations
    if method == 'GET' and path.count('{') > 1:
        issues.append("GET with multiple parameters should use query params")
    
    if method == 'POST' and '{' in path:
        issues.append("POST for creation shouldn't include resource ID in path")
    
    return {
        'method': method,
        'path': path,
        'is_valid': len(issues) == 0,
        'issues': issues
    }

# Test various API endpoints
endpoints = [
    ('GET', '/api/users', 'Get all users'),
    ('GET', '/api/users/{id}', 'Get specific user'),
    ('POST', '/api/users', 'Create new user'),
    ('PUT', '/api/users/{id}', 'Update user'),
    ('DELETE', '/api/users/{id}', 'Delete user'),
    
    # Bad examples
    ('GET', '/api/getUsers', 'Bad: verb in URL'),
    ('POST', '/api/user/{id}', 'Bad: ID in POST'),
    ('PATCH', 'api/user', 'Bad: missing /, singular noun'),
]

results = [validate_rest_endpoint(method, path, desc) for method, path, desc in endpoints]
valid_endpoints = [r for r in results if r['is_valid']]
invalid_endpoints = [r for r in results if not r['is_valid']]
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert len(globals_dict['valid_endpoints']) == 5  # First 5 are good
        assert len(globals_dict['invalid_endpoints']) == 3  # Last 3 are bad
        
        # Check specific issues
        invalid = globals_dict['invalid_endpoints']
        assert any("verb" in str(endpoint['issues']) for endpoint in invalid)
        assert any("ID in POST" in str(endpoint['issues']) for endpoint in invalid)
    
    def test_api_response_formatting(self):
        """Test API response formatting standards."""
        code = '''
import json
from datetime import datetime

def format_api_response(data=None, error=None, status_code=200, metadata=None):
    """Format API response according to standards."""
    response = {
        'timestamp': datetime.utcnow().isoformat(),
        'status_code': status_code,
        'success': 200 <= status_code < 300
    }
    
    if data is not None:
        response['data'] = data
    
    if error:
        response['error'] = {
            'message': error.get('message', 'An error occurred'),
            'code': error.get('code', 'UNKNOWN_ERROR'),
            'details': error.get('details')
        }
    
    if metadata:
        response['metadata'] = metadata
    
    return response

def validate_api_response(response_data):
    """Validate API response format."""
    required_fields = ['timestamp', 'status_code', 'success']
    issues = []
    
    for field in required_fields:
        if field not in response_data:
            issues.append(f"Missing required field: {field}")
    
    # Check data consistency
    if 'status_code' in response_data:
        status_code = response_data['status_code']
        expected_success = 200 <= status_code < 300
        actual_success = response_data.get('success', False)
        
        if expected_success != actual_success:
            issues.append("Success flag doesn't match status code")
    
    # Check error format
    if 'error' in response_data:
        error = response_data['error']
        if not isinstance(error, dict):
            issues.append("Error should be an object")
        elif 'message' not in error:
            issues.append("Error object missing message field")
    
    return {
        'is_valid': len(issues) == 0,
        'issues': issues
    }

# Test different response scenarios
success_response = format_api_response(
    data={'users': [{'id': 1, 'name': 'Alice'}]},
    status_code=200,
    metadata={'total_count': 1, 'page': 1}
)

error_response = format_api_response(
    error={'message': 'User not found', 'code': 'USER_NOT_FOUND'},
    status_code=404
)

success_validation = validate_api_response(success_response)
error_validation = validate_api_response(error_response)

# Test invalid response
invalid_response = {'data': 'some data'}  # Missing required fields
invalid_validation = validate_api_response(invalid_response)
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['success_validation']['is_valid'] is True
        assert globals_dict['error_validation']['is_valid'] is True
        assert globals_dict['invalid_validation']['is_valid'] is False
        
        # Check response structure
        success_resp = globals_dict['success_response']
        assert success_resp['success'] is True
        assert 'data' in success_resp
        assert 'metadata' in success_resp
        
        error_resp = globals_dict['error_response']
        assert error_resp['success'] is False
        assert 'error' in error_resp
        assert error_resp['error']['code'] == 'USER_NOT_FOUND'


class TestWebDevEvaluator:
    """Test cases for web development code evaluator."""
    
    @pytest.fixture
    def evaluator(self):
        """Create a web dev evaluator instance."""
        return WebDevEvaluator()
    
    def test_evaluate_flask_app(self, evaluator):
        """Test evaluation of Flask application."""
        code = '''
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/health')
def health_check():
    return jsonify({'status': 'healthy', 'service': 'test-api'})

# Test the route
with app.test_client() as client:
    response = client.get('/api/health')
    data = response.get_json()
    status_code = response.status_code
'''
        result = evaluator.evaluate(code)
        
        assert result['success'] is True
        assert result['globals']['status_code'] == 200
        assert result['globals']['data']['status'] == 'healthy'
    
    def test_check_web_security_practices(self, evaluator):
        """Test checking for web security practices."""
        secure_code = '''
from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.get_json()
    
    # Input validation
    if not data or 'password' not in data:
        return jsonify({'error': 'Invalid input'}), 400
    
    # Hash password
    password_hash = generate_password_hash(data['password'])
    
    return jsonify({'message': 'User created'}), 201
'''
        
        insecure_code = '''
from flask import Flask, request, jsonify

app = Flask(__name__)
app.secret_key = "hardcoded_secret"

@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.get_json()
    
    # Store password in plain text (BAD!)
    password = data['password']
    
    return jsonify({'message': 'User created'}), 201
'''
        
        secure_analysis = evaluator.analyze_security(secure_code)
        insecure_analysis = evaluator.analyze_security(insecure_code)
        
        assert secure_analysis['security_score'] > insecure_analysis['security_score']
        assert 'password_hashing' in secure_analysis['good_practices']
        assert 'hardcoded_secrets' in insecure_analysis['vulnerabilities']
    
    def test_api_endpoint_analysis(self, evaluator):
        """Test API endpoint analysis."""
        api_code = '''
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/users', methods=['GET'])
def get_users():
    return jsonify([])

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    return jsonify({'id': user_id})

@app.route('/api/users', methods=['POST'])
def create_user():
    return jsonify({'created': True}), 201

@app.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    return jsonify({'updated': True})

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    return '', 204
'''
        
        analysis = evaluator.analyze_api_endpoints(api_code)
        
        assert analysis['total_endpoints'] == 5
        assert analysis['rest_compliance_score'] > 0.8
        assert 'GET' in analysis['methods_used']
        assert 'POST' in analysis['methods_used']
        assert '/api/users' in analysis['resource_paths']


class TestWebSecurityExercises:
    """Test cases for web security exercises."""
    
    def test_sql_injection_prevention(self):
        """Test SQL injection prevention techniques."""
        code = '''
import sqlite3

# Vulnerable code (for educational purposes)
def vulnerable_login(username, password):
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()
    
    # Create test table
    cursor.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            password TEXT
        )
    """)
    cursor.execute("INSERT INTO users (username, password) VALUES ('admin', 'secret123')")
    
    # VULNERABLE: String concatenation
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    
    try:
        cursor.execute(query)
        result = cursor.fetchone()
        return result is not None
    except:
        return False
    finally:
        conn.close()

# Secure code
def secure_login(username, password):
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()
    
    # Create test table
    cursor.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            password TEXT
        )
    """)
    cursor.execute("INSERT INTO users (username, password) VALUES ('admin', 'secret123')")
    
    # SECURE: Parameterized query
    query = "SELECT * FROM users WHERE username = ? AND password = ?"
    
    try:
        cursor.execute(query, (username, password))
        result = cursor.fetchone()
        return result is not None
    finally:
        conn.close()

# Test normal login
normal_login_vulnerable = vulnerable_login('admin', 'secret123')
normal_login_secure = secure_login('admin', 'secret123')

# Test SQL injection attempt
injection_attempt = "admin' OR '1'='1"
injection_vulnerable = vulnerable_login(injection_attempt, 'wrong_password')
injection_secure = secure_login(injection_attempt, 'wrong_password')
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        # Normal login should work for both
        assert globals_dict['normal_login_vulnerable'] is True
        assert globals_dict['normal_login_secure'] is True
        
        # Injection should only work on vulnerable version
        assert globals_dict['injection_vulnerable'] is True  # Vulnerable to injection
        assert globals_dict['injection_secure'] is False    # Protected from injection
    
    def test_xss_prevention(self):
        """Test XSS prevention techniques."""
        code = '''
import html
import re

def vulnerable_render(user_input):
    """Vulnerable to XSS - directly renders user input."""
    return f"<div>Hello, {user_input}!</div>"

def secure_render(user_input):
    """Secure - escapes user input."""
    escaped_input = html.escape(user_input)
    return f"<div>Hello, {escaped_input}!</div>"

def validate_input(user_input):
    """Additional validation to reject potentially malicious input."""
    # Check for script tags and javascript
    dangerous_patterns = [
        r'<script.*?>.*?</script>',
        r'javascript:',
        r'on\w+\s*=',  # event handlers like onclick=
        r'<iframe',
        r'<object',
        r'<embed'
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, user_input, re.IGNORECASE):
            return False
    
    return True

# Test cases
normal_input = "Alice"
xss_script = "<script>alert('XSS')</script>"
xss_event = "<img src=x onerror=alert('XSS')>"

# Test normal input
normal_vulnerable = vulnerable_render(normal_input)
normal_secure = secure_render(normal_input)

# Test XSS attempts
xss_vulnerable = vulnerable_render(xss_script)
xss_secure = secure_render(xss_script)

# Test validation
normal_valid = validate_input(normal_input)
xss_script_valid = validate_input(xss_script)
xss_event_valid = validate_input(xss_event)
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        # Normal input should work fine
        assert "Alice" in globals_dict['normal_vulnerable']
        assert "Alice" in globals_dict['normal_secure']
        
        # XSS should be escaped in secure version
        assert "<script>" in globals_dict['xss_vulnerable']  # Vulnerable
        assert "&lt;script&gt;" in globals_dict['xss_secure']  # Escaped
        
        # Validation should catch malicious input
        assert globals_dict['normal_valid'] is True
        assert globals_dict['xss_script_valid'] is False
        assert globals_dict['xss_event_valid'] is False


class TestWebPerformanceExercises:
    """Test cases for web performance optimization exercises."""
    
    def test_caching_strategies(self):
        """Test caching implementation strategies."""
        code = '''
import time
from functools import wraps

# Simple in-memory cache
cache = {}

def simple_cache(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Create cache key
        key = str(args) + str(sorted(kwargs.items()))
        
        if key in cache:
            return cache[key]
        
        result = func(*args, **kwargs)
        cache[key] = result
        return result
    
    return wrapper

# LRU Cache simulation
class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = {}
        self.access_order = []
    
    def get(self, key):
        if key in self.cache:
            # Move to end (most recently used)
            self.access_order.remove(key)
            self.access_order.append(key)
            return self.cache[key]
        return None
    
    def put(self, key, value):
        if key in self.cache:
            # Update existing
            self.cache[key] = value
            self.access_order.remove(key)
            self.access_order.append(key)
        else:
            # Add new
            if len(self.cache) >= self.capacity:
                # Remove least recently used
                lru_key = self.access_order.pop(0)
                del self.cache[lru_key]
            
            self.cache[key] = value
            self.access_order.append(key)

@simple_cache
def expensive_operation(n):
    """Simulate expensive computation."""
    time.sleep(0.01)  # Simulate delay
    return n * n

# Test caching performance
start_time = time.time()

# First call - should be slow
result1 = expensive_operation(5)
first_call_time = time.time() - start_time

# Second call - should be fast (cached)
start_time = time.time()
result2 = expensive_operation(5)
second_call_time = time.time() - start_time

# Test LRU cache
lru = LRUCache(2)
lru.put("a", 1)
lru.put("b", 2)
lru.put("c", 3)  # Should evict "a"

value_a = lru.get("a")  # Should be None
value_b = lru.get("b")  # Should be 2
value_c = lru.get("c")  # Should be 3
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        # Cache should work
        assert globals_dict['result1'] == 25
        assert globals_dict['result2'] == 25
        assert globals_dict['second_call_time'] < globals_dict['first_call_time']
        
        # LRU cache should work
        assert globals_dict['value_a'] is None  # Evicted
        assert globals_dict['value_b'] == 2
        assert globals_dict['value_c'] == 3
    
    def test_response_compression(self):
        """Test response compression techniques."""
        code = '''
import gzip
import json

def compress_response(data, compression_type='gzip'):
    """Compress response data."""
    if isinstance(data, dict):
        data = json.dumps(data)
    
    if isinstance(data, str):
        data = data.encode('utf-8')
    
    if compression_type == 'gzip':
        compressed = gzip.compress(data)
        return compressed
    
    return data

def calculate_compression_ratio(original, compressed):
    """Calculate compression ratio."""
    original_size = len(original) if isinstance(original, bytes) else len(original.encode('utf-8'))
    compressed_size = len(compressed)
    
    return {
        'original_size': original_size,
        'compressed_size': compressed_size,
        'compression_ratio': compressed_size / original_size,
        'space_saved_percent': ((original_size - compressed_size) / original_size) * 100
    }

# Test with JSON data
large_data = {
    'users': [
        {'id': i, 'name': f'User {i}', 'email': f'user{i}@example.com'}
        for i in range(100)
    ],
    'metadata': {
        'total': 100,
        'page_size': 100,
        'current_page': 1
    }
}

original_json = json.dumps(large_data)
compressed_data = compress_response(large_data)
compression_stats = calculate_compression_ratio(original_json, compressed_data)
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        stats = globals_dict['compression_stats']
        assert stats['compressed_size'] < stats['original_size']
        assert stats['compression_ratio'] < 1.0
        assert stats['space_saved_percent'] > 0


@pytest.mark.integration
class TestWebDevIntegration:
    """Integration tests for web development exercises."""
    
    def test_full_stack_application_simulation(self):
        """Test a complete full-stack application scenario."""
        code = '''
from flask import Flask, request, jsonify
from datetime import datetime
import json

# Simple in-memory database
db = {
    'users': {},
    'posts': {},
    'next_user_id': 1,
    'next_post_id': 1
}

app = Flask(__name__)

# User management
@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.get_json()
    
    user_id = db['next_user_id']
    db['next_user_id'] += 1
    
    user = {
        'id': user_id,
        'username': data['username'],
        'email': data['email'],
        'created_at': datetime.now().isoformat()
    }
    
    db['users'][user_id] = user
    return jsonify(user), 201

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    if user_id not in db['users']:
        return jsonify({'error': 'User not found'}), 404
    return jsonify(db['users'][user_id])

# Post management
@app.route('/api/posts', methods=['POST'])
def create_post():
    data = request.get_json()
    
    # Verify user exists
    if data['author_id'] not in db['users']:
        return jsonify({'error': 'Author not found'}), 400
    
    post_id = db['next_post_id']
    db['next_post_id'] += 1
    
    post = {
        'id': post_id,
        'title': data['title'],
        'content': data['content'],
        'author_id': data['author_id'],
        'created_at': datetime.now().isoformat()
    }
    
    db['posts'][post_id] = post
    return jsonify(post), 201

@app.route('/api/posts', methods=['GET'])
def get_posts():
    posts = list(db['posts'].values())
    # Add author information
    for post in posts:
        author = db['users'].get(post['author_id'])
        if author:
            post['author'] = author['username']
    
    return jsonify(posts)

# Test the full application flow
with app.test_client() as client:
    # Create a user
    user_data = {
        'username': 'testuser',
        'email': 'test@example.com'
    }
    user_response = client.post('/api/users', json=user_data)
    user = user_response.get_json()
    
    # Create a post
    post_data = {
        'title': 'My First Post',
        'content': 'This is the content of my first post.',
        'author_id': user['id']
    }
    post_response = client.post('/api/posts', json=post_data)
    post = post_response.get_json()
    
    # Get all posts
    posts_response = client.get('/api/posts')
    all_posts = posts_response.get_json()
    
    # Verify the flow worked
    flow_success = (
        user_response.status_code == 201 and
        post_response.status_code == 201 and
        posts_response.status_code == 200 and
        len(all_posts) == 1 and
        all_posts[0]['author'] == 'testuser'
    )
'''
        globals_dict = {}
        exec(code, globals_dict)
        
        assert globals_dict['flow_success'] is True
        assert globals_dict['user']['username'] == 'testuser'
        assert globals_dict['post']['title'] == 'My First Post'
        assert len(globals_dict['all_posts']) == 1


if __name__ == '__main__':
    pytest.main([__file__])