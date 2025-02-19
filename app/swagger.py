template = {
    "swagger": "2.0",
    "info": {
        "title": "AgriTechPro API",
        "description": "API pour la gestion des exploitations agricoles",
        "version": "1.0.0"
    },
    "basePath": "/api/v1",
    "schemes": [
        "http",
        "https"
    ],
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT Authorization header using the Bearer scheme. Example: \"Authorization: Bearer {token}\""
        }
    },
    "paths": {
        "/fields": {
            "get": {
                "tags": ["Champs"],
                "summary": "Liste tous les champs de l'utilisateur",
                "responses": {
                    "200": {
                        "description": "Liste des champs récupérée avec succès"
                    }
                }
            },
            "post": {
                "tags": ["Champs"],
                "summary": "Crée un nouveau champ",
                "parameters": [
                    {
                        "name": "body",
                        "in": "body",
                        "required": True,
                        "schema": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "area": {"type": "number"},
                                "crop_type": {"type": "string"}
                            }
                        }
                    }
                ],
                "responses": {
                    "201": {
                        "description": "Champ créé avec succès"
                    }
                }
            }
        },
        "/fields/{field_id}": {
            "get": {
                "tags": ["Champs"],
                "summary": "Récupère un champ spécifique",
                "parameters": [
                    {
                        "name": "field_id",
                        "in": "path",
                        "required": True,
                        "type": "integer"
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Champ récupéré avec succès"
                    },
                    "404": {
                        "description": "Champ non trouvé"
                    }
                }
            },
            "put": {
                "tags": ["Champs"],
                "summary": "Met à jour un champ",
                "parameters": [
                    {
                        "name": "field_id",
                        "in": "path",
                        "required": True,
                        "type": "integer"
                    },
                    {
                        "name": "body",
                        "in": "body",
                        "required": True,
                        "schema": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "area": {"type": "number"},
                                "crop_type": {"type": "string"},
                                "status": {"type": "string"}
                            }
                        }
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Champ mis à jour avec succès"
                    },
                    "404": {
                        "description": "Champ non trouvé"
                    }
                }
            },
            "delete": {
                "tags": ["Champs"],
                "summary": "Supprime un champ",
                "parameters": [
                    {
                        "name": "field_id",
                        "in": "path",
                        "required": True,
                        "type": "integer"
                    }
                ],
                "responses": {
                    "204": {
                        "description": "Champ supprimé avec succès"
                    },
                    "404": {
                        "description": "Champ non trouvé"
                    }
                }
            }
        }
    }
}
