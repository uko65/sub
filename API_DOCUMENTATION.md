# Child Subscription API Documentation

## Overview
This API provides endpoints for managing child subscriptions, packages, users, and geographic data. It supports both authenticated and public access for registration and data retrieval.

---

## Authentication

- **POST /api/auth/register**
  - Register a new user (admin only)
  - Request: `{ "username": str, "email": str, "password": str, "role": str }`
  - Response: `{ "message": str, "user_id": str }`
  - Example:
    ```bash
    curl -X POST http://localhost:5000/api/auth/register \
      -H "Content-Type: application/json" \
      -d '{"username":"admin","email":"admin@example.com","password":"adminpass","role":"admin"}'
    ```


- **POST /api/auth/login**
  - Login and receive JWT tokens
  - Request: `{ "username": str, "password": str }`
  - Response: `{ "message": str, "access_token": str, "refresh_token": str, "user": {...} }`
  - Example:
    ```bash
    curl -X POST http://localhost:5000/api/auth/login \
      -H "Content-Type: application/json" \
      -d '{"username":"admin","password":"adminpass"}'
    ```


- **POST /api/auth/refresh**
  - Refresh access token (JWT required)
  - Request: `{}`
  - Response: `{ "access_token": str }`
  - Example:
    ```bash
    curl -X POST http://localhost:5000/api/auth/refresh \
      -H "Authorization: Bearer <refresh_token>"
    ```

---

## Packages

- **GET /api/public/packages**
  - Get all packages (public)
  - Response: `{ "packages": [ ... ] }`
  - Example:
    ```bash
    curl http://localhost:5000/api/public/packages
    ```


- **POST /api/packages**
  - Create new package (admin only)
  - Request: `{ "name": str, "price": float, ... }`
  - Response: `{ ... }`
  - Example:
    ```bash
    curl -X POST http://localhost:5000/api/packages \
      -H "Authorization: Bearer <access_token>" \
      -H "Content-Type: application/json" \
      -d '{"name":"Basic","price":10.0}'
    ```


- **GET /api/packages**
  - Get all packages (JWT required)
  - Response: `{ "packages": [ ... ] }`
  - Example:
    ```bash
    curl http://localhost:5000/api/packages \
      -H "Authorization: Bearer <access_token>"
    ```

---

## Subscriptions

- **GET /api/public/users.json**
  - Export all users as JSON (public)
  - Example:
    ```bash
    curl http://localhost:5000/api/public/users.json
    ```

- **GET /api/public/packages.json**
  - Export all packages as JSON (public)
  - Example:
    ```bash
    curl http://localhost:5000/api/public/packages.json
    ```

- **GET /api/public/subscriptions.json**
  - Export all subscriptions as JSON (public)
  - Example:
    ```bash
    curl http://localhost:5000/api/public/subscriptions.json
    ```

- **POST /api/public/subscriptions**
  - Create new subscription (public)
  - Request: `{ "phone_number": str, "email": str, "child_name": str, "parent_name": str, "agreed_refused": str, "package": str, "date_of_subscription": str, "area": str, "location": str, "cell": str, "payment_status": str }`
  - Response: `{ ... }`
  - Example:
    ```bash
    curl -X POST http://localhost:5000/api/public/subscriptions \
      -H "Content-Type: application/json" \
      -d '{"phone_number":"+250781234567","email":"parent@example.com","child_name":"Alice","parent_name":"ParentA","agreed_refused":"Agreed","package":"Basic","date_of_subscription":"2025-07-26","area":"Gasabo","location":"Remera","cell":"Cell1","payment_status":"Paid"}'
    ```


- **GET /api/public/subscriptions**
  - Get all subscriptions (public)
  - Query params: `page`, `per_page`
  - Response: `{ ... }`
  - Example:
    ```bash
    curl "http://localhost:5000/api/public/subscriptions?page=1&per_page=20"
    ```


- **POST /api/subscriptions**
  - Create new subscription (JWT required)
  - Request: same as public
  - Response: `{ ... }`
  - Example:
    ```bash
    curl -X POST http://localhost:5000/api/subscriptions \
      -H "Authorization: Bearer <access_token>" \
      -H "Content-Type: application/json" \
      -d '{"phone_number":"+250781234567","email":"parent@example.com","child_name":"Alice","parent_name":"ParentA","agreed_refused":"Agreed","package":"Basic","date_of_subscription":"2025-07-26","area":"Gasabo","location":"Remera","cell":"Cell1","payment_status":"Paid"}'
    ```


- **GET /api/subscriptions**
  - Get all subscriptions (JWT required)
  - Query params: `agreed_refused`, `payment_status`, `area`, `package`, `page`, `per_page`
  - Response: `{ ... }`
  - Example:
    ```bash
    curl "http://localhost:5000/api/subscriptions?area=Gasabo&page=1&per_page=20" \
      -H "Authorization: Bearer <access_token>"
    ```


- **GET /api/subscriptions/<subscription_id>**
  - Get subscription by ID (JWT required)
  - Response: `{ "subscription": { ... } }`
  - Example:
    ```bash
    curl http://localhost:5000/api/subscriptions/<subscription_id> \
      -H "Authorization: Bearer <access_token>"
    ```


- **PUT /api/subscriptions/<subscription_id>**
  - Update subscription (JWT required)
  - Request: `{ ... }`
  - Response: `{ ... }`
  - Example:
    ```bash
    curl -X PUT http://localhost:5000/api/subscriptions/<subscription_id> \
      -H "Authorization: Bearer <access_token>" \
      -H "Content-Type: application/json" \
      -d '{"payment_status":"Paid"}'
    ```


- **DELETE /api/subscriptions/<subscription_id>**
  - Delete subscription (admin only)
  - Response: `{ ... }`
  - Example:
    ```bash
    curl -X DELETE http://localhost:5000/api/subscriptions/<subscription_id> \
      -H "Authorization: Bearer <access_token>"
    ```

---

## Geographic Data

- **GET /api/public/districts**
  - Get list of districts (public)
  - Response: `{ "districts": [ ... ] }`
  - Example:
    ```bash
    curl http://localhost:5000/api/public/districts
    ```


- **GET /api/public/sectors/<district>**
  - Get sectors for a district (public)
  - Response: `{ "district": str, "sectors": [ ... ] }`
  - Example:
    ```bash
    curl http://localhost:5000/api/public/sectors/Gasabo
    ```


- **GET /api/public/cells/<district>/<sector>**
  - Get cells for a sector (public)
  - Response: `{ "district": str, "sector": str, "cells": [ ... ] }`
  - Example:
    ```bash
    curl http://localhost:5000/api/public/cells/Gasabo/Remera
    ```

---

## Reports & Analytics

- **GET /api/reports/subscription-summary**
  - Get subscription analytics (JWT required)
  - Response: `{ ... }`
  - Example:
    ```bash
    curl http://localhost:5000/api/reports/subscription-summary \
      -H "Authorization: Bearer <access_token>"
    ```


- **GET /api/reports/upcoming-renewals**
  - Get subscriptions due for renewal in next 7 days (JWT required)
  - Response: `{ "upcoming_renewals": [ ... ], "total_renewals": int }`
  - Example:
    ```bash
    curl http://localhost:5000/api/reports/upcoming-renewals \
      -H "Authorization: Bearer <access_token>"
    ```

---

## Debug & Health

- **GET /api/health**
  - Health check
  - Response: `{ ... }`
  - Example:
    ```bash
    curl http://localhost:5000/api/health
    ```


- **GET /api/debug/users**
  - List users (admin/debug)
  - Response: `{ ... }`
  - Example:
    ```bash
    curl http://localhost:5000/api/debug/users \
      -H "Authorization: Bearer <access_token>"
    ```


- **GET /api/debug/redis-token/<user_id>**
  - Get Redis token for user
  - Response: `{ ... }`
  - Example:
    ```bash
    curl http://localhost:5000/api/debug/redis-token/<user_id> \
      -H "Authorization: Bearer <access_token>"
    ```


- **GET /api/debug/session-set**
  - Set test session value
  - Response: `{ ... }`
  - Example:
    ```bash
    curl http://localhost:5000/api/debug/session-set
    ```


- **GET /api/debug/session-get**
  - Get test session value
  - Response: `{ ... }`
  - Example:
    ```bash
    curl http://localhost:5000/api/debug/session-get
    ```


- **GET /api/debug/set-cookie**
  - Set test cookie
  - Response: `{ ... }`
  - Example:
    ```bash
    curl http://localhost:5000/api/debug/set-cookie
    ```


- **GET /api/debug/cookies**
  - Show cookies
  - Response: `{ ... }`
  - Example:
    ```bash
    curl http://localhost:5000/api/debug/cookies
    ```

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
