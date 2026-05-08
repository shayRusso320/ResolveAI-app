# Implementation Plan: Python Calculator API

## Overview

This implementation plan breaks down the Python Calculator API feature into discrete, actionable coding tasks. The implementation is intentionally simple: a Flask API with four arithmetic operations (add, subtract, multiply, divide) and a health check endpoint, containerized with Docker, and deployed via GitHub Actions CI/CD to AWS ECS.

---

## Tasks

- [x] 1. Set up project structure and dependencies
  - Create project directory structure with `calculator/` and `.github/workflows/` directories
  - Create `requirements.txt` with Flask dependency only
  - Create `__init__.py` in `calculator/` directory
  - _Requirements: 7.1, 8.1, 8.2_

- [x] 2. Implement arithmetic operations
  - Create `calculator/app.py` with pure arithmetic functions: `add()`, `subtract()`, `multiply()`, `divide()`
  - Ensure all functions accept float operands and return float results
  - _Requirements: 1.1, 2.1, 3.1, 4.1_

- [x] 3. Implement Flask HTTP handler
  - Create Flask application with POST endpoints for `/add`, `/subtract`, `/multiply`, `/divide`
  - Implement GET `/health` endpoint returning `{"status": "healthy"}` with 200 status code
  - Add JSON request parsing for operands (a and b parameters)
  - Add error handling: log only actual code errors (5XX), not user errors (4XX)
  - _Requirements: 1.1, 2.1, 3.1, 4.1, 5.1, 5.2, 5.3, 6.1, 6.2_

- [x] 4. Create application entry point
  - Create `app.py` at project root that imports and runs the Flask application from `calculator/app.py`
  - Ensure the entry point is compatible with Flask's module discovery
  - _Requirements: 6.1, 6.2_

- [x] 5. Create Dockerfile for containerization
  - Create `Dockerfile` with simple single-stage build using `python:3.11-alpine` base image
  - Copy requirements.txt and install dependencies
  - Copy application code
  - Expose port 5000 for HTTP traffic
  - Set CMD to run Flask application on 0.0.0.0:5000
  - _Requirements: 7.1, 7.2, 7.3_

- [x] 6. Create GitHub Actions CI/CD workflow
  - Create `.github/workflows/build-and-push.yml` workflow file
  - Configure workflow to trigger on push to main branch
  - Add checkout step to retrieve repository code
  - Add AWS credentials configuration step using OIDC (role-to-assume with AWS account ID)
  - Add Amazon ECR login step
  - Add Docker build step with image tagging (commit SHA and latest)
  - Add Docker push step to push both tagged images to ECR
  - Add ECS task definition rendering step with new image
  - Add ECS deployment step (non-blocking with wait-for-service-stability: false)
  - Set appropriate permissions (id-token: write, contents: read)
  - Use environment variables for all configuration (AWS_REGION, ECR_REPOSITORY, IAM_ROLE_NAME, ECS_CLUSTER, ECS_SERVICE, ECS_TASK_DEFINITION, ECS_CONTAINER_NAME)
  - _Requirements: 9.1, 9.2, 9.3_

- [x] 7. Create project documentation (README.md)
  - Create `README.md` with project overview
  - Document API endpoints with curl examples for all four operations
  - Document health check endpoint
  - Include setup instructions for local development
  - Include Docker build and run instructions
  - Document required GitHub Actions secrets and environment variables
  - Include AWS setup instructions for OIDC and IAM role
  - _Requirements: 8.1, 8.2, 10.1, 10.2_

- [x] 8. Final verification
  - Verify Docker image builds successfully
  - Verify application starts and responds to health check
  - Verify all API endpoints work correctly with manual testing
  - Ensure all requirements are satisfied
  - _Requirements: All_

---

## Notes

- Implementation is intentionally simple with no tests, registry pattern, or multi-stage Docker build
- Error logging is configured to only log actual code errors (5XX), not user errors (4XX)
- All configuration uses environment variables for flexibility
- CI/CD pipeline uses OIDC for secure AWS authentication without static credentials
- ECS deployment is non-blocking to allow fast feedback
