# Design Document: Python Calculator API

## Overview

The Python Calculator API is a RESTful web service providing basic arithmetic operations (addition, subtraction, multiplication, division) through HTTP endpoints. The system is designed with a layered architecture separating business logic from HTTP handling, enabling easy extension with new operations. The service runs in a containerized environment (Docker with Alpine base) and is deployed via CI/CD pipeline using GitHub Actions with OIDC authentication to AWS ECR.

### Key Design Goals

1. **Modularity**: Extensible operation framework allowing new operations without modifying core logic
2. **Simplicity**: Minimal dependencies and lightweight deployment footprint
3. **Reliability**: Health check endpoint for monitoring and orchestration
4. **Automation**: CI/CD pipeline with secure credential handling via OIDC
5. **Correctness**: Property-based testing for arithmetic operations to ensure mathematical correctness

---

## Architecture

### Layered Component Design

The system follows a three-layer architecture:

```
┌─────────────────────────────────────────┐
│         HTTP Request Handler            │
│  (Flask/FastAPI - Request/Response)     │
├─────────────────────────────────────────┤
│      Operation Registry & Router        │
│  (Maps endpoints to operation handlers) │
├─────────────────────────────────────────┤
│      Business Logic Layer               │
│  (Pure arithmetic operations)           │
└─────────────────────────────────────────┘
```

**Layer 1: Business Logic Layer**
- Pure functions implementing arithmetic operations
- No HTTP dependencies or side effects
- Easily testable with property-based testing
- Operations: `add()`, `subtract()`, `multiply()`, `divide()`

**Layer 2: Operation Registry & Router**
- Central registry for operation handlers
- Maps operation names to handler functions
- Provides consistent interface for adding new operations
- Handles operation lookup and invocation

**Layer 3: HTTP Request Handler**
- Flask or FastAPI application
- Handles HTTP request parsing and response formatting
- Delegates to operation registry for computation
- Manages health check endpoint

### Data Flow

```
HTTP Request
    ↓
[HTTP Handler] → Parse JSON body
    ↓
[Operation Router] → Lookup operation handler
    ↓
[Business Logic] → Execute arithmetic operation
    ↓
[HTTP Handler] → Format JSON response
    ↓
HTTP Response
```

---

## Components and Interfaces

### 1. Business Logic Component

**Module**: `calculator/operations.py`

```python
def add(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b

def subtract(a: float, b: float) -> float:
    """Subtract b from a."""
    return a - b

def multiply(a: float, b: float) -> float:
    """Multiply two numbers."""
    return a * b

def divide(a: float, b: float) -> float:
    """Divide a by b."""
    return a / b
```

**Characteristics**:
- Pure functions with no side effects
- Accept numeric operands (float)
- Return numeric results (float)
- No HTTP or I/O dependencies

### 2. Operation Registry Component

**Module**: `calculator/registry.py`

```python
class OperationRegistry:
    """Registry for arithmetic operations."""
    
    def __init__(self):
        self._operations = {}
    
    def register(self, name: str, handler: Callable) -> None:
        """Register an operation handler."""
        self._operations[name] = handler
    
    def get(self, name: str) -> Callable:
        """Get an operation handler by name."""
        if name not in self._operations:
            raise KeyError(f"Operation '{name}' not found")
        return self._operations[name]
    
    def execute(self, name: str, a: float, b: float) -> float:
        """Execute an operation with given operands."""
        handler = self.get(name)
        return handler(a, b)
```

**Characteristics**:
- Centralized operation management
- Supports dynamic operation registration
- Provides consistent execution interface
- Enables extensibility without modifying HTTP layer

### 3. HTTP Handler Component

**Module**: `calculator/app.py`

```python
from flask import Flask, request, jsonify
from calculator.registry import OperationRegistry
from calculator import operations

app = Flask(__name__)
registry = OperationRegistry()

# Register operations
registry.register('add', operations.add)
registry.register('subtract', operations.subtract)
registry.register('multiply', operations.multiply)
registry.register('divide', operations.divide)

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy'}), 200

@app.route('/add', methods=['POST'])
def add_handler():
    """Handle addition requests."""
    return _handle_operation('add')

@app.route('/subtract', methods=['POST'])
def subtract_handler():
    """Handle subtraction requests."""
    return _handle_operation('subtract')

@app.route('/multiply', methods=['POST'])
def multiply_handler():
    """Handle multiplication requests."""
    return _handle_operation('multiply')

@app.route('/divide', methods=['POST'])
def divide_handler():
    """Handle division requests."""
    return _handle_operation('divide')

def _handle_operation(operation_name: str):
    """Generic operation handler."""
    try:
        data = request.get_json()
        a = data.get('a')
        b = data.get('b')
        
        if a is None or b is None:
            return jsonify({'error': 'Missing operands'}), 400
        
        result = registry.execute(operation_name, a, b)
        return jsonify({'result': result}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500
```

**Characteristics**:
- Handles HTTP request/response lifecycle
- Parses JSON request bodies
- Delegates computation to operation registry
- Returns consistent JSON response format
- Handles errors gracefully

---

## API Endpoint Design

### Request/Response Format

All arithmetic operation endpoints follow this pattern:

**Request**:
```json
{
  "a": <number>,
  "b": <number>
}
```

**Response (Success - 200)**:
```json
{
  "result": <number>
}
```

**Response (Error - 400)**:
```json
{
  "error": "<error message>"
}
```

### Endpoints

#### POST /add
- **Description**: Add two numbers
- **Request Body**: `{"a": <number>, "b": <number>}`
- **Response**: `{"result": <sum>}`
- **Status Codes**: 200 (success), 400 (invalid input), 500 (server error)

#### POST /subtract
- **Description**: Subtract b from a
- **Request Body**: `{"a": <number>, "b": <number>}`
- **Response**: `{"result": <difference>}`
- **Status Codes**: 200 (success), 400 (invalid input), 500 (server error)

#### POST /multiply
- **Description**: Multiply two numbers
- **Request Body**: `{"a": <number>, "b": <number>}`
- **Response**: `{"result": <product>}`
- **Status Codes**: 200 (success), 400 (invalid input), 500 (server error)

#### POST /divide
- **Description**: Divide a by b
- **Request Body**: `{"a": <number>, "b": <number>}`
- **Response**: `{"result": <quotient>}`
- **Status Codes**: 200 (success), 400 (invalid input), 500 (server error)

#### GET /health
- **Description**: Health check endpoint
- **Response**: `{"status": "healthy"}`
- **Status Code**: 200
- **SLA**: Must respond within 100 milliseconds

---

## Health Check Implementation

The health check endpoint provides a simple mechanism for ECS and load balancers to verify service availability:

**Endpoint**: `GET /health`

**Implementation**:
```python
@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy'}), 200
```

**Characteristics**:
- Minimal processing (no external dependencies)
- Fast response time (< 100ms)
- Returns 200 status code when healthy
- Used by ECS for task health monitoring
- Used by load balancers for routing decisions

**ECS Integration**:
- Health check task definition will call `GET /health`
- Interval: 30 seconds (configurable)
- Timeout: 5 seconds
- Healthy threshold: 2 consecutive successes
- Unhealthy threshold: 3 consecutive failures

---

## Docker Containerization

### Dockerfile Design

```dockerfile
# Multi-stage build for minimal image size
FROM python:3.11-alpine AS builder

WORKDIR /app

# Install build dependencies
RUN apk add --no-cache gcc musl-dev

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --user --no-cache-dir -r requirements.txt

# Final stage
FROM python:3.11-alpine

WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY calculator/ ./calculator/
COPY app.py .

# Set environment variables
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

# Expose port 80
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost/health')"

# Run application
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=80"]
```

**Design Decisions**:
- **Alpine Base**: Minimal image size (~50MB vs 900MB+ with standard Python)
- **Multi-stage Build**: Reduces final image size by excluding build tools
- **Non-root User**: Security best practice (optional, can be added)
- **Health Check**: Docker-level health monitoring
- **Port 80**: Standard HTTP port for ECS deployment
- **PYTHONUNBUFFERED**: Ensures logs are streamed in real-time

### Image Optimization

- **Base Image**: `python:3.11-alpine` (~50MB)
- **Dependencies**: Flask + minimal requirements (~10MB)
- **Application Code**: ~1MB
- **Total Image Size**: ~60-70MB

---

## GitHub Actions CI/CD Workflow

### Workflow Design

**File**: `.github/workflows/build-and-push.yml`

```yaml
name: Build and Push to ECR

on:
  push:
    branches:
      - main

permissions:
  id-token: write
  contents: read

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::${{ secrets.AWS_ACCOUNT_ID }}:role/github-actions-role
          aws-region: us-east-1
      
      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v2
      
      - name: Build Docker image
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          ECR_REPOSITORY: python-calculator-api
          IMAGE_TAG: ${{ github.sha }}
        run: |
          docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG .
          docker tag $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG $ECR_REGISTRY/$ECR_REPOSITORY:latest
      
      - name: Push image to Amazon ECR
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          ECR_REPOSITORY: python-calculator-api
          IMAGE_TAG: ${{ github.sha }}
        run: |
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:latest
```

**OIDC Configuration**:
- Uses GitHub's OIDC provider for temporary AWS credentials
- No static AWS credentials stored in repository
- Role-based access control via IAM
- Automatic credential rotation

**Workflow Steps**:
1. Checkout repository code
2. Assume IAM role via OIDC
3. Login to Amazon ECR
4. Build Docker image with commit SHA tag
5. Push image to ECR with both commit SHA and `latest` tags

### AWS IAM Setup

**Trust Relationship** (for GitHub Actions role):
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::ACCOUNT_ID:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:OWNER/REPO:*"
        }
      }
    }
  ]
}
```

**Permissions** (for ECR push):
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ecr:GetDownloadUrlForLayer",
        "ecr:BatchGetImage",
        "ecr:PutImage",
        "ecr:InitiateLayerUpload",
        "ecr:UploadLayerPart",
        "ecr:CompleteLayerUpload"
      ],
      "Resource": "arn:aws:ecr:us-east-1:ACCOUNT_ID:repository/python-calculator-api"
    },
    {
      "Effect": "Allow",
      "Action": "ecr:GetAuthorizationToken",
      "Resource": "*"
    }
  ]
}
```

---

## Modular Operation Framework

### Operation Registration Pattern

The framework enables adding new operations without modifying core logic:

**Step 1: Implement Operation**
```python
# In calculator/operations.py
def power(a: float, b: float) -> float:
    """Raise a to the power of b."""
    return a ** b
```

**Step 2: Register Operation**
```python
# In calculator/app.py
registry.register('power', operations.power)
```

**Step 3: Add HTTP Endpoint**
```python
@app.route('/power', methods=['POST'])
def power_handler():
    return _handle_operation('power')
```

**Benefits**:
- Separation of concerns (business logic vs HTTP)
- Consistent operation interface
- Easy to test operations independently
- Minimal changes to existing code
- Supports dynamic operation registration

### Extension Points

1. **New Arithmetic Operations**: Add function to `operations.py`, register in registry
2. **Advanced Operations**: Implement in separate module, register same way
3. **Persistence Layer**: Add to registry without changing HTTP layer
4. **Caching**: Wrap operation handlers in caching decorator
5. **Logging/Monitoring**: Add middleware to HTTP layer

---

## Data Models

### Operation Input Model

```python
class OperationRequest:
    """Request model for arithmetic operations."""
    a: float  # First operand
    b: float  # Second operand
```

### Operation Output Model

```python
class OperationResponse:
    """Response model for arithmetic operations."""
    result: float  # Calculation result
```

### Error Response Model

```python
class ErrorResponse:
    """Error response model."""
    error: str  # Error message
```

---

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Addition Commutativity

*For any* two numeric operands a and b, adding them in either order should produce the same result: `add(a, b) == add(b, a)`

**Validates: Requirements 1.1, 1.2, 1.3**

### Property 2: Addition Identity

*For any* numeric operand a, adding zero should return the original value: `add(a, 0) == a`

**Validates: Requirements 1.1, 1.2, 1.3**

### Property 3: Subtraction Inverse

*For any* numeric operand a, subtracting a value and then adding it back should return the original value: `add(subtract(a, b), b) == a`

**Validates: Requirements 2.1, 2.2, 2.3**

### Property 4: Multiplication Commutativity

*For any* two numeric operands a and b, multiplying them in either order should produce the same result: `multiply(a, b) == multiply(b, a)`

**Validates: Requirements 3.1, 3.2, 3.3**

### Property 5: Multiplication Identity

*For any* numeric operand a, multiplying by one should return the original value: `multiply(a, 1) == a`

**Validates: Requirements 3.1, 3.2, 3.3**

### Property 6: Division Inverse

*For any* numeric operand a and non-zero b, dividing by a value and then multiplying by it should return the original value: `multiply(divide(a, b), b) == a` (within floating-point precision)

**Validates: Requirements 4.1, 4.2, 4.3**

### Property 8: Arithmetic Associativity (Addition)

*For any* three numeric operands a, b, and c, the order of addition should not affect the result: `add(add(a, b), c) == add(a, add(b, c))`

**Validates: Requirements 1.1, 1.2, 1.3**

### Property 9: Arithmetic Associativity (Multiplication)

*For any* three numeric operands a, b, and c, the order of multiplication should not affect the result: `multiply(multiply(a, b), c) == multiply(a, multiply(b, c))`

**Validates: Requirements 3.1, 3.2, 3.3**

---

## Error Handling

### Error Categories

**1. Input Validation Errors (400 Bad Request)**
- Missing operands: `{"error": "Missing operands"}`
- Invalid JSON format: `{"error": "Invalid JSON"}`
- Non-numeric operands: `{"error": "Operands must be numeric"}`

**2. Operation Errors (400 Bad Request)**
- Invalid operation: `{"error": "Operation 'xyz' not found"}`

**3. Server Errors (500 Internal Server Error)**
- Unexpected exceptions: `{"error": "Internal server error"}`
- Unhandled edge cases

### Error Handling Strategy

```python
def _handle_operation(operation_name: str):
    """Generic operation handler with error handling."""
    try:
        # Parse request
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON'}), 400
        
        a = data.get('a')
        b = data.get('b')
        
        # Validate operands
        if a is None or b is None:
            return jsonify({'error': 'Missing operands'}), 400
        
        if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
            return jsonify({'error': 'Operands must be numeric'}), 400
        
        # Execute operation
        result = registry.execute(operation_name, a, b)
        return jsonify({'result': result}), 200
    
    except ValueError as e:
        # Operation-specific errors
        return jsonify({'error': str(e)}), 400
    
    except KeyError as e:
        # Operation not found
        return jsonify({'error': f'Operation not found: {str(e)}'}), 400
    
    except Exception as e:
        # Unexpected errors
        return jsonify({'error': 'Internal server error'}), 500
```

---

## Testing Strategy

### Unit Tests

**Test File**: `tests/test_operations.py`

Unit tests verify specific examples and edge cases:

```python
def test_add_positive_numbers():
    assert add(2, 3) == 5

def test_add_negative_numbers():
    assert add(-2, -3) == -5

def test_add_mixed_signs():
    assert add(5, -3) == 2

def test_subtract_positive_numbers():
    assert subtract(5, 3) == 2

def test_multiply_positive_numbers():
    assert multiply(3, 4) == 12

def test_divide_positive_numbers():
    assert divide(10, 2) == 5

def test_divide_by_zero():
    with pytest.raises(ValueError):
        divide(10, 0)
```

### Property-Based Tests

**Test File**: `tests/test_properties.py`

Property-based tests verify universal properties across many generated inputs:

```python
from hypothesis import given, strategies as st

# Property 1: Addition Commutativity
@given(st.floats(allow_nan=False, allow_infinity=False), 
       st.floats(allow_nan=False, allow_infinity=False))
def test_add_commutativity(a, b):
    """Feature: python-calculator-api, Property 1: Addition Commutativity"""
    assert add(a, b) == add(b, a)

# Property 2: Addition Identity
@given(st.floats(allow_nan=False, allow_infinity=False))
def test_add_identity(a):
    """Feature: python-calculator-api, Property 2: Addition Identity"""
    assert add(a, 0) == a

# Property 3: Subtraction Inverse
@given(st.floats(allow_nan=False, allow_infinity=False),
       st.floats(allow_nan=False, allow_infinity=False))
def test_subtract_inverse(a, b):
    """Feature: python-calculator-api, Property 3: Subtraction Inverse"""
    assert add(subtract(a, b), b) == a

# Property 4: Multiplication Commutativity
@given(st.floats(allow_nan=False, allow_infinity=False),
       st.floats(allow_nan=False, allow_infinity=False))
def test_multiply_commutativity(a, b):
    """Feature: python-calculator-api, Property 4: Multiplication Commutativity"""
    assert multiply(a, b) == multiply(b, a)

# Property 5: Multiplication Identity
@given(st.floats(allow_nan=False, allow_infinity=False))
def test_multiply_identity(a):
    """Feature: python-calculator-api, Property 5: Multiplication Identity"""
    assert multiply(a, 1) == a

# Property 6: Division Inverse
@given(st.floats(allow_nan=False, allow_infinity=False),
       st.floats(allow_nan=False, allow_infinity=False, min_value=0.001))
def test_divide_inverse(a, b):
    """Feature: python-calculator-api, Property 6: Division Inverse"""
    # Allow for floating-point precision errors
    result = multiply(divide(a, b), b)
    assert abs(result - a) < 1e-9

# Property 7: Division by Zero Error
@given(st.floats(allow_nan=False, allow_infinity=False))
def test_divide_by_zero(a):
    """Feature: python-calculator-api, Property 7: Division by Zero Error"""
    with pytest.raises(ValueError):
        divide(a, 0)

# Property 8: Addition Associativity
@given(st.floats(allow_nan=False, allow_infinity=False),
       st.floats(allow_nan=False, allow_infinity=False),
       st.floats(allow_nan=False, allow_infinity=False))
def test_add_associativity(a, b, c):
    """Feature: python-calculator-api, Property 8: Arithmetic Associativity (Addition)"""
    assert add(add(a, b), c) == add(a, add(b, c))

# Property 9: Multiplication Associativity
@given(st.floats(allow_nan=False, allow_infinity=False),
       st.floats(allow_nan=False, allow_infinity=False),
       st.floats(allow_nan=False, allow_infinity=False))
def test_multiply_associativity(a, b, c):
    """Feature: python-calculator-api, Property 9: Arithmetic Associativity (Multiplication)"""
    assert multiply(multiply(a, b), c) == multiply(a, multiply(b, c))
```

**Configuration**:
- Minimum 100 iterations per property test
- Use Hypothesis library for Python
- Filter out NaN and infinity values
- Allow for floating-point precision tolerance

### Integration Tests

**Test File**: `tests/test_api.py`

Integration tests verify HTTP endpoints and request/response handling:

```python
def test_add_endpoint():
    response = client.post('/add', json={'a': 2, 'b': 3})
    assert response.status_code == 200
    assert response.json == {'result': 5}

def test_divide_by_zero_endpoint():
    response = client.post('/divide', json={'a': 10, 'b': 0})
    assert response.status_code == 400
    assert 'error' in response.json

def test_health_check():
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json == {'status': 'healthy'}

def test_missing_operands():
    response = client.post('/add', json={'a': 2})
    assert response.status_code == 400
    assert 'error' in response.json
```

### Test Coverage Goals

- **Business Logic**: 100% coverage via property-based tests
- **HTTP Layer**: 90%+ coverage via integration tests
- **Error Handling**: 100% coverage via unit and integration tests
- **Overall**: 95%+ code coverage

---

## Project Structure

```
python-calculator-api/
├── .github/
│   └── workflows/
│       └── build-and-push.yml          # CI/CD pipeline
├── calculator/
│   ├── __init__.py
│   ├── operations.py                   # Business logic (pure functions)
│   ├── registry.py                     # Operation registry
│   └── app.py                          # Flask HTTP handler
├── tests/
│   ├── __init__.py
│   ├── test_operations.py              # Unit tests for operations
│   ├── test_properties.py              # Property-based tests
│   └── test_api.py                     # Integration tests
├── .kiro/
│   └── specs/
│       └── python-calculator-api/
│           ├── requirements.md         # Feature requirements
│           └── design.md               # This design document
├── Dockerfile                          # Container image definition
├── requirements.txt                    # Python dependencies
├── app.py                              # Application entry point
├── pytest.ini                          # Pytest configuration
└── README.md                           # Project documentation
```

### File Descriptions

- **calculator/operations.py**: Pure arithmetic functions (add, subtract, multiply, divide)
- **calculator/registry.py**: Operation registry for dynamic operation management
- **calculator/app.py**: Flask application with HTTP endpoints
- **tests/test_operations.py**: Unit tests for business logic
- **tests/test_properties.py**: Property-based tests using Hypothesis
- **tests/test_api.py**: Integration tests for HTTP endpoints
- **Dockerfile**: Multi-stage Docker build for Alpine-based image
- **requirements.txt**: Python dependencies (Flask, Hypothesis, pytest)
- **app.py**: Application entry point (imports and runs Flask app)

---

## Deployment Considerations

### ECS Task Definition

```json
{
  "family": "python-calculator-api",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "containerDefinitions": [
    {
      "name": "calculator",
      "image": "ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/python-calculator-api:latest",
      "portMappings": [
        {
          "containerPort": 80,
          "hostPort": 80,
          "protocol": "tcp"
        }
      ],
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3,
        "startPeriod": 5
      },
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/python-calculator-api",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

### Load Balancer Configuration

- **Target Group**: HTTP on port 80
- **Health Check Path**: `/health`
- **Health Check Interval**: 30 seconds
- **Healthy Threshold**: 2 consecutive successes
- **Unhealthy Threshold**: 3 consecutive failures

---

## Summary

The Python Calculator API design provides:

1. **Layered Architecture**: Clear separation between business logic, operation registry, and HTTP handling
2. **Extensibility**: Modular operation framework for adding new operations without modifying core code
3. **Correctness**: Property-based testing for arithmetic operations to ensure mathematical correctness
4. **Reliability**: Health check endpoint for monitoring and orchestration
5. **Automation**: CI/CD pipeline with secure OIDC-based AWS authentication
6. **Containerization**: Minimal Alpine-based Docker image optimized for production
7. **Maintainability**: Clear project structure and consistent patterns for future enhancements

The design addresses all requirements while maintaining simplicity and enabling future extensibility.
