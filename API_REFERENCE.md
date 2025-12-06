🔌 API REFERENCE GUIDE
======================

Quick reference for all backend API endpoints after improvements.

═══════════════════════════════════════════════════════════════════════════════════

🔐 AUTHENTICATION ENDPOINTS

1. LOGIN
   POST /login
   
   Body:
   {
     "username": "string",
     "password": "string"
   }
   
   Response (200):
   {
     "success": true,
     "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
     "message": "Login successful"
   }
   
   Response (401):
   {
     "detail": "Invalid password" or "User not found"
   }


2. REGISTER
   POST /register
   
   Body:
   {
     "username": "string",
     "password": "string"
   }
   
   Response (200):
   {
     "success": true,
     "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
     "message": "User 'username' registered successfully"
   }
   
   Response (400):
   {
     "detail": "Username already exists" or "Password must be at least 6 characters"
   }

═══════════════════════════════════════════════════════════════════════════════════

🔑 API KEY MANAGEMENT ENDPOINTS
(All require Authorization header)

3. SAVE OPENAI KEY
   POST /save-openai-key
   
   Headers:
   Authorization: Bearer <token>
   
   Body:
   {
     "api_key": "sk-..."
   }
   
   Response (200):
   {
     "success": true,
     "message": "OpenAI key saved successfully"
   }


4. SAVE SOCIAL MEDIA KEYS
   POST /save-social-keys
   
   Headers:
   Authorization: Bearer <token>
   
   Body:
   {
     "platform": "facebook",  // or "instagram", "twitter"
     "keys": {
       "access_token": "...",
       "page_id": "..."
     }
   }
   
   Response (200):
   {
     "success": true,
     "message": "Facebook keys saved successfully"
   }


5. GET USER KEYS
   GET /user-keys
   
   Headers:
   Authorization: Bearer <token>
   
   Response (200):
   {
     "success": true,
     "keys": {
       "openai_key": "sk-...",
       "facebook_keys": {"access_token": "...", "page_id": "..."},
       "instagram_keys": null,
       "twitter_keys": null
     }
   }


6. DELETE OPENAI KEY
   DELETE /delete-openai-key
   
   Headers:
   Authorization: Bearer <token>
   
   Response (200):
   {
     "success": true,
     "message": "OpenAI key deleted successfully"
   }


7. DELETE SOCIAL MEDIA KEYS
   DELETE /delete-social-keys/{platform}
   
   Headers:
   Authorization: Bearer <token>
   
   Parameters:
   platform: "facebook" | "instagram" | "twitter"
   
   Response (200):
   {
     "success": true,
     "message": "Facebook keys deleted successfully"
   }

═══════════════════════════════════════════════════════════════════════════════════

✨ CONTENT GENERATION ENDPOINTS
(All require Authorization header)

8. GENERATE CAPTION
   POST /generate-caption
   
   Headers:
   Authorization: Bearer <token>
   
   Body:
   {
     "topic": "New product launch",
     "style": "professional",        // optional: professional|casual|funny|inspirational
     "include_hashtags": true,       // optional
     "num_hashtags": 5              // optional
   }
   
   Response (200):
   {
     "success": true,
     "caption": "Introducing our latest innovation...",
     "hashtags": ["#innovation", "#launch", "#AI", "#future", "#tech"],
     "full_text": "Introducing our latest innovation...\n\n#innovation #launch #AI #future #tech"
   }
   
   Fallback (without API key):
   {
     "success": true,
     "caption": "[Demo] New product launch - OpenAI not installed",
     "hashtags": ["#demo", "#placeholder"],
     "full_text": "[Demo] New product launch\n\n#demo #placeholder"
   }


9. GENERATE IMAGE
   POST /generate-image
   
   Headers:
   Authorization: Bearer <token>
   
   Body:
   {
     "prompt": "A futuristic AI robot workspace",
     "size": "1024x1024",           // optional: 1024x1024|1024x1792|1792x1024
     "style": "natural"             // optional: natural|vivid
   }
   
   Response (200):
   {
     "success": true,
     "image_url": "https://oaidalleapiprodscus.blob.core.windows.net/...",
     "local_path": "backend/generated_images/generated_image_1234.png",
     "base64": null,
     "message": "Image generated successfully"
   }
   
   Response (400) - No API key:
   {
     "success": false,
     "image_url": null,
     "local_path": null,
     "base64": null,
     "message": "No OpenAI API key configured"
   }

═══════════════════════════════════════════════════════════════════════════════════

📤 SOCIAL MEDIA POSTING ENDPOINT
(Requires Authorization header)

10. POST TO PLATFORMS
    POST /post
    
    Headers:
    Authorization: Bearer <token>
    
    Body:
    {
      "caption": "Check out our new AI tool! #innovation #AI",
      "image_url": "https://example.com/image.jpg",  // optional
      "platforms": ["facebook", "instagram", "twitter"]  // optional
    }
    
    Response (200):
    {
      "success": true,
      "results": {
        "facebook": {
          "success": true,
          "post_id": "fb_post_5234",
          "message": "Posted to Facebook successfully (Post ID: fb_post_5234)"
        },
        "instagram": {
          "success": true,
          "post_id": "ig_post_7291",
          "message": "Posted to Instagram successfully (Media ID: ig_post_7291)"
        },
        "twitter": {
          "success": true,
          "post_id": "tw_9847203",
          "message": "Posted to Twitter successfully (Tweet ID: tw_9847203)"
        }
      },
      "message": "Posted to all selected platforms"
    }
    
    Response (400) - Missing credentials:
    {
      "success": false,
      "results": {
        "facebook": {
          "success": false,
          "post_id": null,
          "message": "Missing Facebook credentials"
        },
        ...
      }
    }

═══════════════════════════════════════════════════════════════════════════════════

💚 HEALTH CHECK ENDPOINT

11. HEALTH CHECK
    GET /health
    
    Response (200):
    {
      "status": "healthy",
      "service": "AI Social Media Automation Bot API"
    }


12. ROOT
    GET /
    
    Response (200):
    {
      "name": "AI Social Media Automation Bot",
      "version": "1.0.0",
      "description": "AI-powered social media posting system",
      "endpoints": {
        "auth": ["/login", "/register"],
        "keys": ["/save-openai-key", "/save-social-keys", "/user-keys"],
        "generation": ["/generate-caption", "/generate-image"],
        "posting": ["/post"],
        "health": ["/health"]
      }
    }

═══════════════════════════════════════════════════════════════════════════════════

🔑 DEFAULT TEST CREDENTIALS

Username: alexis
Password: password123
Email: alexis@example.com
Admin: Yes

These are created automatically on first run.

═══════════════════════════════════════════════════════════════════════════════════

⚠️ COMMON ERRORS & SOLUTIONS

401 Unauthorized - "Missing authorization header"
├─ Fix: Add header: Authorization: Bearer <token>

401 Unauthorized - "Invalid or expired token"
├─ Fix: Login again to get fresh token
└─ Note: Tokens expire after 480 minutes (8 hours)

400 Bad Request - "Username already exists"
├─ Fix: Use different username or login instead

400 Bad Request - "Password must be at least 6 characters"
├─ Fix: Use longer password (minimum 6 chars)

400 Bad Request - "No OpenAI API key configured"
├─ Fix: POST to /save-openai-key with valid API key first

═══════════════════════════════════════════════════════════════════════════════════

📝 CURL EXAMPLES

# Login
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"alexis","password":"password123"}'

# Save OpenAI Key
curl -X POST http://localhost:8000/save-openai-key \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"api_key":"sk-..."}'

# Generate Caption
curl -X POST http://localhost:8000/generate-caption \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"topic":"AI for everyone","style":"professional"}'

# Post to Platforms
curl -X POST http://localhost:8000/post \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "caption":"Check this out!",
    "platforms":["facebook","instagram","twitter"]
  }'

═══════════════════════════════════════════════════════════════════════════════════
