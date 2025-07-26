"""
Swagger API documentation specifications
"""

# Authentication endpoints
auth_login_spec = {
    "tags": ["Authentication"],
    "summary": "User login",
    "description": "Authenticate user and receive JWT tokens for API access. Returns both access and refresh tokens.",
    "parameters": [
        {
            "name": "credentials",
            "in": "body",
            "required": True,
            "description": "User login credentials",
            "schema": {
                "$ref": "#/definitions/AuthRequest"
            }
        }
    ],
    "responses": {
        "200": {
            "description": "Login successful",
            "schema": {
                "$ref": "#/definitions/AuthResponse"
            },
            "examples": {
                "application/json": {
                    "message": "Login successful",
                    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                    "user": {
                        "username": "admin",
                        "email": "admin@example.com",
                        "role": "admin"
                    }
                }
            }
        },
        "400": {
            "description": "Bad request - Missing required fields",
            "schema": {
                "$ref": "#/definitions/Error"
            }
        },
        "401": {
            "description": "Unauthorized - Invalid credentials",
            "schema": {
                "$ref": "#/definitions/Error"
            }
        }
    }
}

auth_register_spec = {
    "tags": ["Authentication"],
    "summary": "Register new user (Admin only)",
    "description": "Create a new user account. This endpoint requires admin privileges.",
    "security": [{"Bearer": []}],
    "parameters": [
        {
            "name": "user_data",
            "in": "body",
            "required": True,
            "description": "New user information",
            "schema": {
                "type": "object",
                "required": ["username", "email", "password"],
                "properties": {
                    "username": {
                        "type": "string",
                        "minLength": 3,
                        "maxLength": 50,
                        "description": "Unique username"
                    },
                    "email": {
                        "type": "string",
                        "format": "email",
                        "description": "User's email address"
                    },
                    "password": {
                        "type": "string",
                        "minLength": 6,
                        "description": "User password"
                    },
                    "role": {
                        "type": "string",
                        "enum": ["admin", "user"],
                        "default": "user",
                        "description": "User role"
                    }
                }
            }
        }
    ],
    "responses": {
        "201": {
            "description": "User created successfully",
            "schema": {
                "type": "object",
                "properties": {
                    "message": {"type": "string"},
                    "user_id": {"type": "string"}
                }
            }
        },
        "400": {
            "description": "Bad request - Username or email already exists",
            "schema": {"$ref": "#/definitions/Error"}
        },
        "403": {
            "description": "Forbidden - Admin access required",
            "schema": {"$ref": "#/definitions/Error"}
        }
    }
}

# Subscription endpoints
subscription_create_spec = {
    "tags": ["Subscriptions"],
    "summary": "Create new subscription",
    "description": "Create a new subscription record with comprehensive validation for geographic data and package existence.",
    "security": [{"Bearer": []}],
    "parameters": [
        {
            "name": "subscription_data",
            "in": "body",
            "required": True,
            "description": "Subscription information",
            "schema": {
                "type": "object",
                "required": [
                    "phone_number", "email", "child_name", "parent_name",
                    "agreed_refused", "package", "date_of_subscription",
                    "area", "location"
                ],
                "properties": {
                    "phone_number": {
                        "type": "string",
                        "pattern": "^\\+250[0-9]{9}$",
                        "description": "Phone number in Rwanda format",
                        "example": "+250781234567"
                    },
                    "email": {
                        "type": "string",
                        "format": "email",
                        "description": "Parent's email address"
                    },
                    "child_name": {
                        "type": "string",
                        "minLength": 2,
                        "maxLength": 100,
                        "description": "Name of the child"
                    },
                    "parent_name": {
                        "type": "string",
                        "minLength": 2,
                        "maxLength": 100,
                        "description": "Name of the parent/guardian"
                    },
                    "agreed_refused": {
                        "type": "string",
                        "enum": ["Agreed", "Refused"],
                        "description": "Subscription agreement status"
                    },
                    "package": {
                        "type": "string",
                        "description": "Name of the subscription package"
                    },
                    "date_of_subscription": {
                        "type": "string",
                        "format": "date",
                        "description": "Subscription start date (YYYY-MM-DD)"
                    },
                    "area": {
                        "type": "string",
                        "enum": ["Gasabo", "Kicukiro", "Nyarugenge"],
                        "description": "Kigali district"
                    },
                    "location": {
                        "type": "string",
                        "description": "Sector within the district"
                    },
                    "cell": {
                        "type": "string",
                        "description": "Cell within the sector (optional)"
                    }
                }
            }
        }
    ],
    "responses": {
        "201": {
            "description": "Subscription created successfully",
            "schema": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "subscription_id": {"type": "string"}
                }
            }
        },
        "400": {
            "description": "Bad request - Validation errors",
            "schema": {"$ref": "#/definitions/Error"}
        }
    }
}

# Health check endpoint
health_check_spec = {
    "tags": ["System"],
    "summary": "API health check",
    "description": "Check the health status of the API and its dependencies including database connectivity.",
    "responses": {
        "200": {
            "description": "System is healthy",
            "schema": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["healthy"]
                    },
                    "timestamp": {
                        "type": "string",
                        "format": "date-time"
                    },
                    "database": {
                        "type": "string",
                        "enum": ["connected"]
                    }
                }
            },
            "examples": {
                "application/json": {
                    "status": "healthy",
                    "timestamp": "2024-01-15T10:30:00.000Z",
                    "database": "connected"
                }
            }
        },
        "500": {
            "description": "System is unhealthy",
            "schema": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["unhealthy"]
                    },
                    "timestamp": {
                        "type": "string",
                        "format": "date-time"
                    },
                    "database": {
                        "type": "string",
                        "enum": ["disconnected"]
                    },
                    "error": {
                        "type": "string"
                    }
                }
            }
        }
    }
}

# Search endpoints
subscription_search_spec = {
    "tags": ["Subscriptions"],
    "summary": "Search subscriptions",
    "description": "Search subscriptions across multiple fields including phone number, email, names, and location data.",
    "security": [{"Bearer": []}],
    "parameters": [
        {
            "name": "q",
            "in": "query",
            "required": True,
            "type": "string",
            "minLength": 1,
            "description": "Search query string"
        },
        {
            "name": "page",
            "in": "query",
            "type": "integer",
            "minimum": 1,
            "default": 1,
            "description": "Page number for pagination"
        },
        {
            "name": "per_page",
            "in": "query",
            "type": "integer",
            "minimum": 1,
            "maximum": 100,
            "default": 20,
            "description": "Number of items per page"
        }
    ],
    "responses": {
        "200": {
            "description": "Search results retrieved successfully",
            "schema": {
                "allOf": [
                    {"$ref": "#/definitions/PaginatedResponse"},
                    {
                        "type": "object",
                        "properties": {
                            "subscriptions": {
                                "type": "array",
                                "items": {"$ref": "#/definitions/Subscription"}
                            }
                        }
                    }
                ]
            }
        },
        "400": {
            "description": "Bad request - Search query required",
            "schema": {"$ref": "#/definitions/Error"}
        }
    }
}

subscription_list_spec = {
    "tags": ["Subscriptions"],
    "summary": "Get all subscriptions with filtering",
    "description": "Retrieve a paginated list of subscriptions with optional filtering by various criteria.",
    "security": [{"Bearer": []}],
    "parameters": [
        {
            "name": "page",
            "in": "query",
            "type": "integer",
            "minimum": 1,
            "default": 1,
            "description": "Page number for pagination"
        },
        {
            "name": "per_page",
            "in": "query",
            "type": "integer",
            "minimum": 1,
            "maximum": 100,
            "default": 20,
            "description": "Number of items per page"
        },
        {
            "name": "agreed_refused",
            "in": "query",
            "type": "string",
            "enum": ["Agreed", "Refused"],
            "description": "Filter by agreement status"
        },
        {
            "name": "payment_status",
            "in": "query",
            "type": "string",
            "enum": ["Pending", "Paid", "Failed"],
            "description": "Filter by payment status"
        },
        {
            "name": "area",
            "in": "query",
            "type": "string",
            "enum": ["Gasabo", "Kicukiro", "Nyarugenge"],
            "description": "Filter by district"
        },
        {
            "name": "package",
            "in": "query",
            "type": "string",
            "description": "Filter by package name"
        }
    ],
    "responses": {
        "200": {
            "description": "Subscriptions retrieved successfully",
            "schema": {
                "allOf": [
                    {"$ref": "#/definitions/PaginatedResponse"},
                    {
                        "type": "object",
                        "properties": {
                            "subscriptions": {
                                "type": "array",
                                "items": {"$ref": "#/definitions/Subscription"}
                            }
                        }
                    }
                ]
            }
        }
    }
}

# Package endpoints
package_create_spec = {
    "tags": ["Packages"],
    "summary": "Create new package (Admin only)",
    "description": "Create a new subscription package with features and pricing information.",
    "security": [{"Bearer": []}],
    "parameters": [
        {
            "name": "package_data",
            "in": "body",
            "required": True,
            "description": "Package information",
            "schema": {
                "type": "object",
                "required": ["name", "price"],
                "properties": {
                    "name": {
                        "type": "string",
                        "minLength": 2,
                        "maxLength": 100,
                        "description": "Package name (must be unique)"
                    },
                    "description": {
                        "type": "string",
                        "maxLength": 500,
                        "description": "Package description"
                    },
                    "price": {
                        "type": "number",
                        "minimum": 0,
                        "description": "Package price in RWF"
                    },
                    "duration_days": {
                        "type": "integer",
                        "minimum": 1,
                        "default": 30,
                        "description": "Package duration in days"
                    },
                    "features": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of package features"
                    }
                }
            }
        }
    ],
    "responses": {
        "201": {
            "description": "Package created successfully",
            "schema": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "package_id": {"type": "string"}
                }
            }
        },
        "400": {
            "description": "Bad request - Package name already exists",
            "schema": {"$ref": "#/definitions/Error"}
        },
        "403": {
            "description": "Forbidden - Admin access required",
            "schema": {"$ref": "#/definitions/Error"}
        }
    }
}

# Geography endpoints
geography_districts_spec = {
    "tags": ["Geography"],
    "summary": "Get Kigali districts",
    "description": "Retrieve list of all districts in Kigali province for location selection.",
    "security": [{"Bearer": []}],
    "responses": {
        "200": {
            "description": "Districts retrieved successfully",
            "schema": {
                "type": "object",
                "properties": {
                    "districts": {
                        "type": "array",
                        "items": {"type": "string"},
                        "example": ["Gasabo", "Kicukiro", "Nyarugenge"]
                    }
                }
            }
        }
    }
}

geography_sectors_spec = {
    "tags": ["Geography"],
    "summary": "Get sectors by district",
    "description": "Retrieve list of sectors within a specific district.",
    "security": [{"Bearer": []}],
    "parameters": [
        {
            "name": "district",
            "in": "path",
            "required": True,
            "type": "string",
            "enum": ["Gasabo", "Kicukiro", "Nyarugenge"],
            "description": "District name"
        }
    ],
    "responses": {
        "200": {
            "description": "Sectors retrieved successfully",
            "schema": {
                "type": "object",
                "properties": {
                    "district": {"type": "string"},
                    "sectors": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                }
            }
        },
        "400": {
            "description": "Invalid district",
            "schema": {"$ref": "#/definitions/Error"}
        }
    }
}

# Reports endpoints  
reports_analytics_spec = {
    "tags": ["Reports"],
    "summary": "Get subscription analytics",
    "description": "Comprehensive analytics including subscription counts, agreement rates, payment status, geographic distribution, and package popularity.",
    "security": [{"Bearer": []}],
    "responses": {
        "200": {
            "description": "Analytics retrieved successfully",
            "schema": {"$ref": "#/definitions/Analytics"},
            "examples": {
                "application/json": {
                    "total_subscriptions": 150,
                    "total_agreed": 105,
                    "total_refused": 45,
                    "agreement_breakdown": [
                        {"_id": "Agreed", "count": 105},
                        {"_id": "Refused", "count": 45}
                    ],
                    "payment_status": [
                        {"_id": "Paid", "count": 80},
                        {"_id": "Pending", "count": 20},
                        {"_id": "Failed", "count": 5}
                    ],
                    "popular_packages": [
                        {"_id": "Basic Plan", "count": 60},
                        {"_id": "Premium Plan", "count": 30},
                        {"_id": "Family Plan", "count": 15}
                    ],
                    "area_distribution": [
                        {"_id": "Gasabo", "count": 70},
                        {"_id": "Kicukiro", "count": 45},
                        {"_id": "Nyarugenge", "count": 35}
                    ],
                    "upcoming_renewals": 12
                }
            }
        }
    }
}

reports_dashboard_spec = {
    "tags": ["Reports"],
    "summary": "Get dashboard statistics",
    "description": "Key metrics for dashboard display including current month statistics and renewal information.",
    "security": [{"Bearer": []}],
    "responses": {
        "200": {
            "description": "Dashboard stats retrieved successfully",
            "schema": {
                "type": "object",
                "properties": {
                    "total_subscriptions": {"type": "integer"},
                    "total_agreed": {"type": "integer"},
                    "total_refused": {"type": "integer"},
                    "success_rate": {"type": "number", "format": "float"},
                    "this_month_subscriptions": {"type": "integer"},
                    "upcoming_renewals": {"type": "integer"},
                    "payment_breakdown": {
                        "type": "object",
                        "properties": {
                            "paid": {"type": "integer"},
                            "pending": {"type": "integer"},
                            "failed": {"type": "integer"}
                        }
                    }
                }
            }
        }
    }
}

# Public endpoints
public_packages_spec = {
    "tags": ["Public"],
    "summary": "Get all packages (Public)",
    "description": "Retrieve all available subscription packages without authentication. Used for public package selection.",
    "responses": {
        "200": {
            "description": "Packages retrieved successfully",
            "schema": {
                "type": "object",
                "properties": {
                    "packages": {
                        "type": "array",
                        "items": {"$ref": "#/definitions/Package"}
                    }
                }
            }
        }
    }
}

public_subscription_create_spec = {
    "tags": ["Public"],
    "summary": "Create subscription (Public)",
    "description": "Create a new subscription without authentication. This is the main public endpoint for subscription creation.",
    "parameters": [
        {
            "name": "subscription_data",
            "in": "body",
            "required": True,
            "description": "Subscription information",
            "schema": {
                "type": "object",
                "required": [
                    "phone_number", "email", "child_name", "parent_name",
                    "agreed_refused", "package", "date_of_subscription",
                    "area", "location"
                ],
                "properties": {
                    "phone_number": {
                        "type": "string",
                        "pattern": "^\\+250[0-9]{9}$",
                        "description": "Phone number in Rwanda format",
                        "example": "+250781234567"
                    },
                    "email": {
                        "type": "string",
                        "format": "email",
                        "description": "Parent's email address"
                    },
                    "child_name": {
                        "type": "string",
                        "minLength": 2,
                        "maxLength": 100,
                        "description": "Name of the child" 
                    },
                    "parent_name": {
                        "type": "string",
                        "minLength": 2,
                        "maxLength": 100,
                        "description": "Name of the parent/guardian"
                    },
                    "agreed_refused": {
                        "type": "string",
                        "enum": ["Agreed", "Refused"],
                        "description": "Subscription agreement status"
                    },
                    "package": {
                        "type": "string",
                        "description": "Name of the subscription package"
                    },
                    "date_of_subscription": {
                        "type": "string",
                        "format": "date",
                        "description": "Subscription start date (YYYY-MM-DD)"
                    },
                    "area": {
                        "type": "string",
                        "enum": ["Gasabo", "Kicukiro", "Nyarugenge"],
                        "description": "Kigali district" 
                    },
                    "location": {
                        "type": "string",
                        "description": "Sector within the district"
                    },
                    "cell": {
                        "type": "string",
                        "description": "Cell within the sector (optional)"
                    }
                }
            }
        }
    ],

    "responses": {
        "201": {
            "description": "Subscription created successfully",
            "schema": {

                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "subscription_id": {"type": "string"}
                }
            }
        },

        "400": {
            "description": "Bad request - Validation errors",
            "schema": {"$ref": "#/definitions/Error"}
        },
        "500": {
            "description": "Internal server error",
            "schema": {
                "type": "object",
                "properties": {
                    "error": {
                        "type": "string",
                        "description": "Error message"
                    }
                }
            }
        }
    }
}