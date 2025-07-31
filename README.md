# NoSQL Injection Exploitation: Leak Unreleased Products

A practical challenge that demonstrates how a poorly filtered NoSQL query parameter enables attackers to enumerate and leak sensitive product information from a MongoDB-backed e-commerce site.

## Objectives

- Detect and confirm NoSQL injection via error-based probing
- Exploit boolean logic injections to bypass category filters
- Extract sensitive, unreleased product data from the application

## Difficulty

Intermediate

## Estimated Time

45 minutes

## Prerequisites

- Burp Suite or an intercepting proxy
- Basic knowledge of JavaScript and MongoDB query syntax
- Familiarity with web application testing

## Skills Learned

- Detecting and confirming NoSQL injections
- Constructing and encoding MongoDB operator payloads
- Leveraging injections to access unauthorized data

## Project Structure

```
├── build/           # Application source code
├── deploy/          # Docker deployment files
├── test/            # Automated tests
├── docs/            # Documentation
├── README.md        # This file
└── .gitignore       # Git ignore rules
```

## Quick Start

### Prerequisites

Docker and Docker Compose installed on your machine.

### Installation

1. Clone the repository
2. Run `docker-compose up --build` in the project directory
3. Access the lab interface at http://localhost:3206

## Docker Hub Deployment

This project includes automated Docker Hub deployment via GitHub Actions. The workflow will build and push the Docker image to Docker Hub on every push to main/master branch or when tags are created.

### Setup GitHub Secrets

To enable Docker Hub deployment, you need to configure the following secrets in your GitHub repository:

1. Go to your repository Settings → Secrets and variables → Actions
2. Add the following repository secrets:

- `DOCKER_USER`: Your Docker Hub username
- `DOCKER_PAT`: Your Docker Hub Personal Access Token (not your password)

### How to Create a Docker Hub Personal Access Token

1. Log in to [Docker Hub](https://hub.docker.com/)
2. Go to Account Settings → Security
3. Click "New Access Token"
4. Give it a name (e.g., "GitHub Actions")
5. Copy the token and save it as the `DOCKER_PAT` secret

### Using the Deployed Image

Once the workflow runs successfully, you can pull and run the image:

```bash
docker pull your-dockerhub-username/nosql_injection_lab_flask:latest
docker run -p 3206:5000 your-dockerhub-username/nosql_injection_lab_flask:latest
```

Note: You'll still need to run MongoDB separately or use the docker-compose file for the complete setup.

## Issue Tracker

https://github.com/example-org/nosql-injection-lab/issues

---

*This is a deliberately vulnerable lab designed solely for educational purposes.* 