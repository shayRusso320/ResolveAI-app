# Python Calculator API

A simple Flask API that provides basic arithmetic operations (add, subtract, multiply, divide) and a health check endpoint.

## Quick Start

### Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the app:
```bash
python -m flask run --host=0.0.0.0 --port=5000
```

The API will be available at `http://localhost:5000`

### Docker

Build and run:
```bash
docker build -t calculator-api .
docker run -p 5000:5000 calculator-api
```

## API Endpoints

### POST /add
```bash
curl -X POST http://localhost:5000/add -H "Content-Type: application/json" -d '{"a": 5, "b": 3}'
```
Response: `{"result": 8}`

### POST /subtract
```bash
curl -X POST http://localhost:5000/subtract -H "Content-Type: application/json" -d '{"a": 5, "b": 3}'
```
Response: `{"result": 2}`

### POST /multiply
```bash
curl -X POST http://localhost:5000/multiply -H "Content-Type: application/json" -d '{"a": 5, "b": 3}'
```
Response: `{"result": 15}`

### POST /divide
```bash
curl -X POST http://localhost:5000/divide -H "Content-Type: application/json" -d '{"a": 6, "b": 2}'
```
Response: `{"result": 3.0}`

### GET /health
```bash
curl http://localhost:5000/health
```
Response: `{"status": "healthy"}`

## GitHub Actions Setup

The CI/CD pipeline automatically builds and pushes Docker images to Amazon ECR on every push to the main branch.

### Required Repository Secrets

Add these secrets to your GitHub repository (Settings → Secrets and variables → Actions):

| Secret Name | Value | Example |
|-------------|-------|---------|
| `AWS_ACCOUNT_ID` | Your AWS account ID | `123456789012` |

### Required Environment Variables

Set these in your GitHub Actions workflow or repository settings:

| Variable | Value |
|----------|-------|
| `AWS_REGION` | AWS region for ECR | `us-east-1` |
| `ECR_REPOSITORY` | ECR repository name | `python-calculator-api` |

### Required AWS Setup

1. Create an OIDC provider in AWS:
```bash
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --client-id-list sts.amazonaws.com \
  --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1
```

2. Create an IAM role for GitHub Actions:
```bash
aws iam create-role \
  --role-name github-actions-role \
  --assume-role-policy-document '{
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
            "token.actions.githubusercontent.com:sub": "repo:YOUR_ORG/YOUR_REPO:*"
          }
        }
      }
    ]
  }'
```

3. Attach ECR permissions to the role:
```bash
aws iam put-role-policy \
  --role-name github-actions-role \
  --policy-name ecr-push \
  --policy-document '{
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
  }'
```

4. Create an ECR repository:
```bash
aws ecr create-repository --repository-name python-calculator-api --region us-east-1
```

## Deployment

Push to main branch to trigger the GitHub Actions workflow, which will:
1. Build the Docker image
2. Push to Amazon ECR with commit SHA and `latest` tags
