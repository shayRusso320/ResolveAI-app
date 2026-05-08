# Implementation Plan: Python Calculator API

## Overview

This implementation plan breaks down the Python Calculator API feature into discrete, actionable coding tasks. The tasks follow a layered architecture approach: starting with project setup and dependencies, then implementing the business logic layer, operation registry, HTTP handler, and finally comprehensive testing and deployment automation.

Each task builds incrementally on previous steps, ensuring that core functionality is validated early through automated tests. Property-based tests validate universal correctness properties of arithmetic operations, while unit and integration tests ensure specific examples and edge cases work correctly.

---

## Tasks

- [x] 1. Set up project structure and dependencies
  - Create project directory structure with `calculator/`, `tests/`, and `.github/workflows/` directories
  - Create `requirements.txt` with Flask, Hypothesis, and pytest dependencies
  - Create `pytest.ini` configuration file for test discovery and execution
  - Create `__init__.py` files in `calculator/` and `tests/` directories
  - _Requirements: 7.1, 8.1, 8.2_

- [x] 2. Implement business logic layer (operations.py)
  - Create `calculator/operations.py` with pure arithmetic functions: `add()`, `subtract()`, `multiply()`, `divide()`
  - Ensure all functions accept float operands and return float results
  - _Requirements: 1.1, 2.1, 3.1, 4.1_

- [ ]* 2.1 Write property test for addition commutativity
  - **Property 1: Addition Commutativity**
  - **Validates: Requirements 1.1, 1.2, 1.3**
  - Use Hypothesis to generate random float pairs and verify `add(a, b) == add(b, a)`

- [ ]* 2.2 Write property test for addition identity
  - **Property 2: Addition Identity**
  - **Validates: Requirements 1.1, 1.2, 1.3**
  - Use Hypothesis to verify `add(a, 0) == a` for all numeric values

- [ ]* 2.3 Write property test for addition associativity
  - **Property 8: Arithmetic Associativity (Addition)**
  - **Validates: Requirements 1.1, 1.2, 1.3**
  - Use Hypothesis to verify `add(add(a, b), c) == add(a, add(b, c))` for all numeric values

- [x] 3. Implement operation registry (registry.py)
  - Create `calculator/registry.py` with `OperationRegistry` class
  - Implement `register(name, handler)` method to register operation handlers
  - Implement `get(name)` method to retrieve operation handlers by name
  - Implement `execute(name, a, b)` method to execute operations with operands
  - Raise `KeyError` when operation is not found
  - _Requirements: 8.1, 8.2, 10.1, 10.2_

- [x] 4. Implement HTTP handler (app.py)
  - Create `calculator/app.py` with Flask application setup
  - Register all four arithmetic operations (add, subtract, multiply, divide) in the registry
  - Implement generic `_handle_operation()` helper function for consistent request/response handling
  - Implement POST endpoints for `/add`, `/subtract`, `/multiply`, `/divide`
  - Implement GET `/health` endpoint returning `{"status": "healthy"}` with 200 status code
  - Add JSON request parsing and validation for operands (check for presence and numeric type)
  - Add error handling for missing operands (400 status), operation errors (400 status), and unexpected errors (500 status)
  - _Requirements: 1.1, 2.1, 3.1, 4.1, 5.1, 5.2, 5.3, 6.1, 6.2_

- [ ]* 4.1 Write property test for subtraction inverse
  - **Property 3: Subtraction Inverse**
  - **Validates: Requirements 2.1, 2.2, 2.3**
  - Use Hypothesis to verify `add(subtract(a, b), b) == a` for all numeric values

- [ ]* 4.2 Write property test for multiplication commutativity
  - **Property 4: Multiplication Commutativity**
  - **Validates: Requirements 3.1, 3.2, 3.3**
  - Use Hypothesis to generate random float pairs and verify `multiply(a, b) == multiply(b, a)`

- [ ]* 4.3 Write property test for multiplication identity
  - **Property 5: Multiplication Identity**
  - **Validates: Requirements 3.1, 3.2, 3.3**
  - Use Hypothesis to verify `multiply(a, 1) == a` for all numeric values

- [ ]* 4.4 Write property test for multiplication associativity
  - **Property 9: Arithmetic Associativity (Multiplication)**
  - **Validates: Requirements 3.1, 3.2, 3.3**
  - Use Hypothesis to verify `multiply(multiply(a, b), c) == multiply(a, multiply(b, c))` for all numeric values

- [ ]* 4.5 Write property test for division inverse
  - **Property 6: Division Inverse**
  - **Validates: Requirements 4.1, 4.2, 4.3**
  - Use Hypothesis to verify `multiply(divide(a, b), b) ≈ a` (within floating-point precision) for non-zero b

- [x] 5. Write unit tests for operations
  - Create `tests/test_operations.py` with unit tests for each operation
  - Test addition with positive, negative, and mixed-sign operands
  - Test subtraction with positive, negative, and mixed-sign operands
  - Test multiplication with positive, negative, and mixed-sign operands
  - Test division with positive, negative, and mixed-sign operands
  - Test edge cases (zero operands, very large/small numbers)
  - _Requirements: 1.1, 2.1, 3.1, 4.1_

- [x] 6. Write integration tests for API endpoints
  - Create `tests/test_api.py` with integration tests for HTTP endpoints
  - Test successful POST requests to `/add`, `/subtract`, `/multiply`, `/divide` with valid operands
  - Test error responses for missing operands (400 status code)
  - Test error responses for non-numeric operands (400 status code)
  - Test GET `/health` endpoint returns 200 status and `{"status": "healthy"}`
  - Test invalid JSON request body handling (400 status code)
  - _Requirements: 1.1, 2.1, 3.1, 4.1, 5.1, 5.2, 5.3, 6.1, 6.2_

- [x] 7. Checkpoint - Ensure all tests pass
  - Run `pytest` to execute all unit, property-based, and integration tests
  - Verify 100% code coverage for business logic layer
  - Verify 90%+ code coverage for HTTP layer
  - Ensure all tests pass before proceeding to containerization
  - _Requirements: All_

- [x] 8. Create Dockerfile for containerization
  - Create `Dockerfile` with multi-stage build using `python:3.11-alpine` base image
  - Stage 1 (builder): Install build dependencies, copy requirements.txt, install Python dependencies
  - Stage 2 (final): Copy dependencies from builder, copy application code, set environment variables
  - Expose port 80 for HTTP traffic
  - Add HEALTHCHECK instruction with 30-second interval, 5-second timeout, 3 retries
  - Set PYTHONUNBUFFERED=1 environment variable for real-time log streaming
  - Set CMD to run Flask application on 0.0.0.0:80
  - _Requirements: 7.1, 7.2, 7.3_

- [x] 9. Create application entry point (app.py at root)
  - Create `app.py` at project root that imports and runs the Flask application from `calculator/app.py`
  - Ensure the entry point is compatible with Flask's module discovery
  - _Requirements: 6.1, 6.2_

- [x] 10. Create GitHub Actions CI/CD workflow
  - Create `.github/workflows/build-and-push.yml` workflow file
  - Configure workflow to trigger on push to main branch
  - Add checkout step to retrieve repository code
  - Add AWS credentials configuration step using OIDC (role-to-assume with AWS account ID)
  - Add Amazon ECR login step
  - Add Docker build step with image tagging (commit SHA and latest)
  - Add Docker push step to push both tagged images to ECR
  - Set appropriate permissions (id-token: write, contents: read)
  - _Requirements: 9.1, 9.2, 9.3_

- [x] 11. Create project documentation (README.md)
  - Create `README.md` with project overview and feature description
  - Document API endpoints with request/response examples for all four operations
  - Document health check endpoint
  - Include setup instructions for local development (install dependencies, run tests)
  - Include Docker build and run instructions
  - Include deployment instructions for ECS
  - Document the modular architecture and how to add new operations
  - _Requirements: 8.1, 8.2, 10.1, 10.2_

- [x] 12. Final checkpoint - Verify complete implementation
  - Run all tests one final time to ensure everything passes
  - Verify Docker image builds successfully
  - Verify application starts and responds to health check
  - Verify all API endpoints work correctly with manual testing or automated integration tests
  - Ensure all requirements are satisfied
  - _Requirements: All_

---

## Notes

- Tasks marked with `*` are optional property-based test sub-tasks and can be skipped for faster MVP delivery
- Each task references specific requirements for traceability
- Property-based tests validate universal correctness properties defined in the design document
- Unit tests validate specific examples and edge cases
- Integration tests validate HTTP request/response handling and error scenarios
- Checkpoints at tasks 7 and 12 ensure incremental validation of the implementation
- All code should follow Python best practices and PEP 8 style guidelines
- The implementation uses Flask for HTTP handling and Hypothesis for property-based testing
- Docker image is optimized for production with Alpine base and multi-stage build
- CI/CD pipeline uses OIDC for secure AWS authentication without static credentials
