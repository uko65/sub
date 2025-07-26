# Child Subscription API Documentation

## Overview
This API provides endpoints for managing child subscriptions, packages, users, and geographic data. It supports both authenticated and public access for registration and data retrieval.

---

## Authentication
- **POST /api/auth/register**
  - Register a new user (admin only)
  - Request: `{ "username": str, "email": str, "password": str, "role": str }`
  - Response: `{ "message": str, "user_id": str }`

- **POST /api/auth/login**
  - Login and receive JWT tokens
  - Request: `{ "username": str, "password": str }`
  - Response: `{ "message": str, "access_token": str, "refresh_token": str, "user": {...} }`

- **POST /api/auth/refresh**
  - Refresh access token (JWT required)
  - Request: `{}`
  - Response: `{ "access_token": str }`

---

## Packages
- **GET /api/public/packages**
  - Get all packages (public)
  - Response: `{ "packages": [ ... ] }`

- **POST /api/packages**
  - Create new package (admin only)
  - Request: `{ "name": str, "price": float, ... }`
  - Response: `{ ... }`

- **GET /api/packages**
  - Get all packages (JWT required)
  - Response: `{ "packages": [ ... ] }`

---

## Subscriptions
- **POST /api/public/subscriptions**
  - Create new subscription (public)
  - Request: `{ "phone_number": str, "email": str, "child_name": str, "parent_name": str, "agreed_refused": str, "package": str, "date_of_subscription": str, "area": str, "location": str, "cell": str, "payment_status": str }`
  - Response: `{ ... }`

- **GET /api/public/subscriptions**
  - Get all subscriptions (public)
  - Query params: `page`, `per_page`
  - Response: `{ ... }`

- **POST /api/subscriptions**
  - Create new subscription (JWT required)
  - Request: same as public
  - Response: `{ ... }`

- **GET /api/subscriptions**
  - Get all subscriptions (JWT required)
  - Query params: `agreed_refused`, `payment_status`, `area`, `package`, `page`, `per_page`
  - Response: `{ ... }`

- **GET /api/subscriptions/<subscription_id>**
  - Get subscription by ID (JWT required)
  - Response: `{ "subscription": { ... } }`

- **PUT /api/subscriptions/<subscription_id>**
  - Update subscription (JWT required)
  - Request: `{ ... }`
  - Response: `{ ... }`

- **DELETE /api/subscriptions/<subscription_id>**
  - Delete subscription (admin only)
  - Response: `{ ... }`

---

## Geographic Data
- **GET /api/public/districts**
  - Get list of districts (public)
  - Response: `{ "districts": [ ... ] }`

- **GET /api/public/sectors/<district>**
  - Get sectors for a district (public)
  - Response: `{ "district": str, "sectors": [ ... ] }`

- **GET /api/public/cells/<district>/<sector>**
  - Get cells for a sector (public)
  - Response: `{ "district": str, "sector": str, "cells": [ ... ] }`

---

## Reports & Analytics
- **GET /api/reports/subscription-summary**
  - Get subscription analytics (JWT required)
  - Response: `{ ... }`

- **GET /api/reports/upcoming-renewals**
  - Get subscriptions due for renewal in next 7 days (JWT required)
  - Response: `{ "upcoming_renewals": [ ... ], "total_renewals": int }`

---

## Debug & Health
- **GET /api/health**
  - Health check
  - Response: `{ ... }`

- **GET /api/debug/users**
  - List users (admin/debug)
  - Response: `{ ... }`

- **GET /api/debug/redis-token/<user_id>**
  - Get Redis token for user
  - Response: `{ ... }`

- **GET /api/debug/session-set**
  - Set test session value
  - Response: `{ ... }`

- **GET /api/debug/session-get**
  - Get test session value
  - Response: `{ ... }`

- **GET /api/debug/set-cookie**
  - Set test cookie
  - Response: `{ ... }`

- **GET /api/debug/cookies**
  - Show cookies
  - Response: `{ ... }`

---

## Error Codes
- 400: Bad request (missing/invalid data)
- 401: Unauthorized (missing/invalid token)
- 403: Forbidden (admin only)
- 404: Not found
- 500: Internal server error

---

## Notes
- All endpoints return JSON.
- Authenticated endpoints require JWT in `Authorization: Bearer <token>` header.
- Pagination is supported for subscription lists.
- Geographic endpoints provide data for dropdowns in registration forms.
