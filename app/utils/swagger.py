from flask import Flask
from flasgger import Swagger, swag_from
import os

def init_swagger(app: Flask):
    """Initialize Swagger documentation for the Flask app"""
    
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec',
                "route": '/apispec.json',
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/api/docs/"
    }

    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": "Subscription Management API",
            "description": "A comprehensive REST API for managing subscription services with user authentication, geographic data management, and analytics.",
            "contact": {
                "name": "API Support",
                "email": "support@subscription-api.com",
                "url": "https://subscription-api.com/support"
            },
            "license": {
                "name": "MIT",
                "url": "https://opensource.org/licenses/MIT"
            },
            "version": "1.0.0",
            "termsOfService": "https://subscription-api.com/terms"
        },
        "host": os.environ.get('API_HOST', 'localhost:5000'),
        "basePath": "/api",
        "schemes": [
            "http",
            "https"
        ],
        "consumes": [
            "application/json"
        ],
        "produces": [
            "application/json"
        ],
        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "JWT Authorization header using the Bearer scheme. Example: 'Authorization: Bearer {token}'"
            }
        },
        "security": [
            {
                "Bearer": []
            }
        ],
        "tags": [
            {
                "name": "Authentication",
                "description": "User authentication and authorization operations"
            },
            {
                "name": "Subscriptions",
                "description": "Subscription management operations"
            },
            {
                "name": "Packages",
                "description": "Package management operations"
            },
            {
                "name": "Geography",
                "description": "Geographic data operations for Rwanda/Kigali"
            },
            {
                "name": "Reports",
                "description": "Analytics and reporting operations"
            },
            {
                "name": "Public",
                "description": "Public endpoints that don't require authentication"
            },
            {
                "name": "System",
                "description": "System health and utility operations"
            }
        ],
        "definitions": {
            "User": {
                "type": "object",
                "required": ["username", "email", "role"],
                "properties": {
                    "_id": {
                        "type": "string",
                        "description": "Unique identifier for the user"
                    },
                    "username": {
                        "type": "string",
                        "description": "Unique username",
                        "minLength": 3,
                        "maxLength": 50
                    },
                    "email": {
                        "type": "string",
                        "format": "email",
                        "description": "User's email address"
                    },
                    "role": {
                        "type": "string",
                        "enum": ["admin", "user"],
                        "description": "User role"
                    },
                    "created_at": {
                        "type": "string",
                        "format": "date-time",
                        "description": "User creation timestamp"
                    },
                    "is_active": {
                        "type": "boolean",
                        "description": "Whether the user is active"
                    }
                }
            },
            "Subscription": {
                "type": "object",
                "required": [
                    "phone_number", "email", "child_name", "parent_name",
                    "agreed_refused", "package", "date_of_subscription",
                    "area", "location"
                ],
                "properties": {
                    "_id": {
                        "type": "string",
                        "description": "Unique identifier for the subscription"
                    },
                    "phone_number": {
                        "type": "string",
                        "pattern": "^\\+250[0-9]{9}$",
                        "description": "Phone number in Rwanda format (+250XXXXXXXXX)",
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
                        "description": "Whether the subscription was agreed to or refused"
                    },
                    "package": {
                        "type": "string",
                        "description": "Name of the subscription package"
                    },
                    "date_of_subscription": {
                        "type": "string",
                        "format": "date",
                        "description": "Date when the subscription was created (YYYY-MM-DD)"
                    },
                    "renew_subscription_by": {
                        "type": "string",
                        "format": "date",
                        "description": "Date when the subscription should be renewed"
                    },
                    "payment_status": {
                        "type": "string",
                        "enum": ["Pending", "Paid", "Failed"],
                        "description": "Current payment status"
                    },
                    "area": {
                        "type": "string",
                        "enum": ["Gasabo", "Kicukiro", "Nyarugenge"],
                        "description": "Kigali district where the subscriber is located"
                    },
                    "location": {
                        "type": "string",
                        "description": "Sector within the district"
                    },
                    "cell": {
                        "type": "string",
                        "description": "Cell within the sector (optional)"
                    },
                    "created_at": {
                        "type": "string",
                        "format": "date-time",
                        "description": "Subscription creation timestamp"
                    },
                    "updated_at": {
                        "type": "string",
                        "format": "date-time",
                        "description": "Last update timestamp"
                    },
                    "is_active": {
                        "type": "boolean",
                        "description": "Whether the subscription is active"
                    }
                }
            },
            "Package": {
                "type": "object",
                "required": ["name", "price"],
                "properties": {
                    "_id": {
                        "type": "string",
                        "description": "Unique identifier for the package"
                    },
                    "name": {
                        "type": "string",
                        "minLength": 2,
                        "maxLength": 100,
                        "description": "Package name"
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
                        "items": {
                            "type": "string"
                        },
                        "description": "List of package features"
                    },
                    "is_active": {
                        "type": "boolean",
                        "description": "Whether the package is active"
                    },
                    "created_at": {
                        "type": "string",
                        "format": "date-time",
                        "description": "Package creation timestamp"
                    },
                    "updated_at": {
                        "type": "string",
                        "format": "date-time",
                        "description": "Last update timestamp"
                    }
                }
            },
            "AuthRequest": {
                "type": "object",
                "required": ["username", "password"],
                "properties": {
                    "username": {
                        "type": "string",
                        "minLength": 3,
                        "maxLength": 50,
                        "description": "Username for authentication"
                    },
                    "password": {
                        "type": "string",
                        "minLength": 6,
                        "maxLength": 100,
                        "description": "Password for authentication"
                    }
                }
            },
            "AuthResponse": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "Response message"
                    },
                    "access_token": {
                        "type": "string",
                        "description": "JWT access token"
                    },
                    "refresh_token": {
                        "type": "string",
                        "description": "JWT refresh token"
                    },
                    "user": {
                        "$ref": "#/definitions/User"
                    }
                }
            },
            "Analytics": {
                "type": "object",
                "properties": {
                    "total_subscriptions": {
                        "type": "integer",
                        "description": "Total number of active subscriptions"
                    },
                    "total_agreed": {
                        "type": "integer",
                        "description": "Number of agreed subscriptions"
                    },
                    "total_refused": {
                        "type": "integer",
                        "description": "Number of refused subscriptions"
                    },
                    "agreement_breakdown": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "_id": {
                                    "type": "string"
                                },
                                "count": {
                                    "type": "integer"
                                }
                            }
                        }
                    },
                    "payment_status": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "_id": {
                                    "type": "string"
                                },
                                "count": {
                                    "type": "integer"
                                }
                            }
                        }
                    },
                    "popular_packages": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "_id": {
                                    "type": "string"
                                },
                                "count": {
                                    "type": "integer"
                                }
                            }
                        }
                    },
                    "area_distribution": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "_id": {
                                    "type": "string"
                                },
                                "count": {
                                    "type": "integer"
                                }
                            }
                        }
                    },
                    "upcoming_renewals": {
                        "type": "integer",
                        "description": "Number of subscriptions due for renewal in the next 7 days"
                    }
                }
            },
            "Error": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "Error message"
                    },
                    "error_code": {
                        "type": "string",
                        "description": "Error code (optional)"
                    }
                }
            },
            "PaginatedResponse": {
                "type": "object",
                "properties": {
                    "total": {
                        "type": "integer",
                        "description": "Total number of items"
                    },
                    "page": {
                        "type": "integer",
                        "description": "Current page number"
                    },
                    "per_page": {
                        "type": "integer",
                        "description": "Items per page"
                    },
                    "total_pages": {
                        "type": "integer",
                        "description": "Total number of pages"
                    }
                }
            }
        }
    }

    swagger = Swagger(app, config=swagger_config, template=swagger_template)
    return swagger