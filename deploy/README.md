# NoSQL Injection Lab

A deliberately vulnerable e-commerce application demonstrating NoSQL injection vulnerabilities in MongoDB query parameters.

## Quick Start

```bash
docker pull cyberctf/nosql-injection-lab:latest
docker run -p 3206:5000 cyberctf/nosql-injection-lab:latest
```

Access the application at: http://localhost:3206

## Description

This lab simulates a TargetCorp e-commerce platform with a vulnerable product filtering system. The application uses MongoDB for data storage and contains unreleased product information that can be accessed through NoSQL injection attacks.

## Learning Objectives

- Detect NoSQL injection vulnerabilities
- Exploit boolean logic injections
- Extract sensitive data from MongoDB
- Understand NoSQL injection prevention

## Target

The vulnerable endpoint is located at `/api/products` and accepts a `category` parameter that is directly injected into MongoDB queries without proper sanitization.

## Difficulty

Intermediate

## Estimated Time

45 minutes

---

*This is a deliberately vulnerable lab designed solely for educational purposes.* 