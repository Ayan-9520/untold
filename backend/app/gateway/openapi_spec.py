"""UNTOLD API Gateway — OpenAPI specification."""

OPENAPI_SPEC = {
    "openapi": "3.1.0",
    "info": {
        "title": "UNTOLD API Gateway",
        "version": "1.0.0",
        "description": (
            "Production API Gateway for UNTOLD Studio and public catalog. "
            "Authenticate with `Authorization: Bearer <jwt>` or `X-API-Key: unt_...`. "
            "Set `X-API-Version: v1|v2` for versioned responses."
        ),
        "contact": {"name": "UNTOLD Platform", "url": "https://untold.com"},
    },
    "servers": [{"url": "/gateway", "description": "API Gateway"}],
    "components": {
        "securitySchemes": {
            "BearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"},
            "ApiKeyAuth": {"type": "apiKey", "in": "header", "name": "X-API-Key"},
        },
        "schemas": {
            "Video": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "thumbnail_url": {"type": "string"},
                    "duration_seconds": {"type": "integer"},
                },
            },
            "Project": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "title": {"type": "string"},
                    "stage": {"type": "string"},
                    "updated_at": {"type": "string", "format": "date-time"},
                },
            },
            "V2Envelope": {
                "type": "object",
                "properties": {
                    "data": {},
                    "meta": {
                        "type": "object",
                        "properties": {
                            "version": {"type": "string"},
                            "request_id": {"type": "string"},
                        },
                    },
                },
            },
        },
    },
    "security": [{"BearerAuth": []}, {"ApiKeyAuth": []}],
    "paths": {
        "/v1/me": {
            "get": {
                "summary": "Current authentication context",
                "tags": ["Auth"],
                "responses": {"200": {"description": "Auth context"}},
            }
        },
        "/v1/videos": {
            "get": {
                "summary": "List videos",
                "tags": ["Videos"],
                "parameters": [
                    {"name": "page", "in": "query", "schema": {"type": "integer", "default": 1}},
                    {"name": "page_size", "in": "query", "schema": {"type": "integer", "default": 20}},
                    {"name": "search", "in": "query", "schema": {"type": "string"}},
                ],
                "responses": {"200": {"description": "Paginated video list"}},
            }
        },
        "/v1/videos/{video_id}": {
            "get": {
                "summary": "Get video by ID",
                "tags": ["Videos"],
                "parameters": [{"name": "video_id", "in": "path", "required": True, "schema": {"type": "integer"}}],
                "responses": {"200": {"description": "Video", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Video"}}}}},
            }
        },
        "/v1/projects": {
            "get": {
                "summary": "List studio projects",
                "tags": ["Projects"],
                "parameters": [{"name": "stage", "in": "query", "schema": {"type": "string"}}],
                "responses": {"200": {"description": "Project list"}},
            }
        },
        "/v1/projects/{project_id}": {
            "get": {
                "summary": "Get project by ID",
                "tags": ["Projects"],
                "parameters": [{"name": "project_id", "in": "path", "required": True, "schema": {"type": "integer"}}],
                "responses": {"200": {"description": "Project"}},
            }
        },
        "/v1/analytics/overview": {
            "get": {
                "summary": "Analytics overview",
                "tags": ["Analytics"],
                "responses": {"200": {"description": "Analytics summary"}},
            }
        },
        "/v1/webhooks": {
            "get": {"summary": "List webhooks", "tags": ["Webhooks"], "responses": {"200": {"description": "Webhook list"}}},
            "post": {"summary": "Create webhook", "tags": ["Webhooks"], "responses": {"201": {"description": "Webhook created"}}},
        },
        "/v1/webhooks/{webhook_id}": {
            "delete": {
                "summary": "Delete webhook",
                "tags": ["Webhooks"],
                "parameters": [{"name": "webhook_id", "in": "path", "required": True, "schema": {"type": "integer"}}],
                "responses": {"204": {"description": "Deleted"}},
            }
        },
        "/v2/me": {"get": {"summary": "Current auth (v2 envelope)", "tags": ["Auth v2"], "responses": {"200": {"description": "V2 envelope"}}}},
        "/graphql": {
            "post": {
                "summary": "GraphQL endpoint",
                "tags": ["GraphQL"],
                "description": "POST JSON body `{ query, variables }`",
                "responses": {"200": {"description": "GraphQL response"}},
            }
        },
    },
    "tags": [
        {"name": "Auth", "description": "Authentication context"},
        {"name": "Videos", "description": "Public video catalog"},
        {"name": "Projects", "description": "Studio productions"},
        {"name": "Analytics", "description": "Usage analytics"},
        {"name": "Webhooks", "description": "Outbound event subscriptions"},
        {"name": "GraphQL", "description": "GraphQL query API"},
        {"name": "Auth v2", "description": "Version 2 envelope responses"},
    ],
}
