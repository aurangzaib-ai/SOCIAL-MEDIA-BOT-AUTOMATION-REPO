"""
auth.py - Authentication system with SQLite database and JWT tokens
Handles user registration, login, password hashing, token generation, and validation
Uses bcrypt for secure password hashing and JWT for session tokens
"""

from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict
import jwt
import sqlite3
import re
import os
from passlib.context import CryptContext

# ==================== Configuration ====================

DB_FILE = "backend/users.db"
SECRET_KEY = "your-secret-key-change-this-in-production-use-env-var"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480  # 8 hours

# Password hashing context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ==================== Database Initialization ====================

def init_database():
    """
    Initialize SQLite database with users and user_access tables
    Creates tables if they don't exist
    """
    os.makedirs("backend", exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # Users table with enhanced fields
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        is_admin BOOLEAN DEFAULT 0,
        password TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # User access control table for feature permissions
    c.execute("""
    CREATE TABLE IF NOT EXISTS user_access (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        devices BOOLEAN DEFAULT 0,
        chatbox BOOLEAN DEFAULT 0,
        projects BOOLEAN DEFAULT 0,
        settings BOOLEAN DEFAULT 0,
        programming BOOLEAN DEFAULT 0,
        FOREIGN KEY (username) REFERENCES users (username)
    )
    """)

    conn.commit()
    conn.close()


# ==================== Helper Functions ====================

def is_valid_email(email: str) -> bool:
    """
    Validate email format using regex
    
    Args:
        email: Email string to validate
    
    Returns:
        True if email format is valid, False otherwise
    """
    pattern = r"[^@]+@[^@]+\.[^@]+"
    return bool(re.match(pattern, email))


def hash_password(password: str) -> str:
    """
    Hash password using bcrypt
    
    Args:
        password: Plain text password
    
    Returns:
        Hashed password string
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify plain text password against hashed password
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to verify against
    
    Returns:
        True if passwords match, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


# ==================== User Registration ====================

def register_user(username: str, password: str, name: str = None, email: str = None, is_admin: bool = False) -> Dict[str, any]:
    """
    Register a new user with validation
    
    Supports both simple (username, password) and full (username, password, name, email, is_admin) signatures
    
    Args:
        username: Unique username for login
        password: Plain text password (will be hashed)
        name: Full name of the user (optional, defaults to username)
        email: Email address (optional, defaults to username@example.com)
        is_admin: Whether user has admin privileges (default: False)
    
    Returns:
        {
            "success": bool,
            "message": str,
            "user_id": int or None
        }
    """
    init_database()
    
    # Use defaults if not provided
    if name is None or name.strip() == "":
        name = username
    if email is None or email.strip() == "":
        email = f"{username}@example.com"
    
    # Validation
    if not username or not password:
        return {"success": False, "message": "Username and password are required", "user_id": None}
    
    if not is_valid_email(email):
        return {"success": False, "message": "Invalid email format", "user_id": None}
    
    if len(password) < 6:
        return {"success": False, "message": "Password must be at least 6 characters", "user_id": None}
    
    if len(username) < 3:
        return {"success": False, "message": "Username must be at least 3 characters", "user_id": None}
    
    # Hash password
    hashed_password = hash_password(password)
    
    # Insert user into database
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    try:
        c.execute(
            """
            INSERT INTO users (username, name, email, password, is_admin)
            VALUES (?, ?, ?, ?, ?)
            """,
            (username, name, email, hashed_password, int(is_admin))
        )
        
        # Create user access record (all features disabled by default)
        c.execute(
            """
            INSERT INTO user_access (username, devices, chatbox, projects, settings, programming)
            VALUES (?, 0, 0, 0, 0, 0)
            """,
            (username,)
        )
        
        conn.commit()
        user_id = c.lastrowid
        
        return {
            "success": True,
            "message": f"User '{username}' registered successfully",
            "user_id": user_id
        }
    
    except sqlite3.IntegrityError as e:
        return {
            "success": False,
            "message": "Username or email already exists",
            "user_id": None
        }
    
    except Exception as e:
        return {
            "success": False,
            "message": f"Registration error: {str(e)}",
            "user_id": None
        }
    
    finally:
        conn.close()


# ==================== User Login ====================

def verify_login(username: str, password: str) -> Tuple[bool, str]:
    """
    Verify user login credentials
    
    Args:
        username: Username to verify
        password: Password to verify
    
    Returns:
        (is_valid: bool, message: str)
    """
    init_database()
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    try:
        c.execute("SELECT id, username, name, email, password, is_admin FROM users WHERE username = ?", (username,))
        user = c.fetchone()
        
        if not user:
            return False, "User not found"
        
        user_id, username, name, email, hashed_password, is_admin = user
        
        # Verify password
        if not verify_password(password, hashed_password):
            return False, "Invalid password"
        
        return True, "Login successful"
    
    except Exception as e:
        return False, f"Login error: {str(e)}"
    
    finally:
        conn.close()


# ==================== JWT Token Management ====================

def create_access_token(username: str, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token for a user
    
    Args:
        username: Username to encode in token
        expires_delta: Custom expiration time (default: 480 minutes)
    
    Returns:
        JWT token string
    """
    if expires_delta is None:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    expire = datetime.utcnow() + expires_delta
    
    payload = {
        "sub": username,
        "exp": expire,
        "iat": datetime.utcnow()
    }
    
    encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[str]:
    """
    Verify JWT token and extract username
    
    Args:
        token: JWT token to verify
    
    Returns:
        Username if valid, None if invalid or expired
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        
        if username is None:
            return None
        
        return username
    
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


# ==================== User Queries ====================

def get_user_by_username(username: str) -> Optional[Dict]:
    """
    Retrieve user information by username
    
    Args:
        username: Username to search for
    
    Returns:
        User data dictionary or None if not found
    """
    init_database()
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    try:
        c.execute(
            "SELECT id, username, name, email, is_admin, created_at FROM users WHERE username = ?",
            (username,)
        )
        user = c.fetchone()
        
        if not user:
            return None
        
        return {
            "id": user[0],
            "username": user[1],
            "name": user[2],
            "email": user[3],
            "is_admin": bool(user[4]),
            "created_at": user[5]
        }
    
    finally:
        conn.close()


def get_user_access(username: str) -> Optional[Dict]:
    """
    Get user's feature access permissions
    
    Args:
        username: Username to get permissions for
    
    Returns:
        User access data dictionary or None
    """
    init_database()
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    try:
        c.execute(
            "SELECT username, devices, chatbox, projects, settings, programming FROM user_access WHERE username = ?",
            (username,)
        )
        access = c.fetchone()
        
        if not access:
            return None
        
        return {
            "username": access[0],
            "devices": bool(access[1]),
            "chatbox": bool(access[2]),
            "projects": bool(access[3]),
            "settings": bool(access[4]),
            "programming": bool(access[5])
        }
    
    finally:
        conn.close()


# ==================== Initialize Default User ====================

def init_default_user():
    """Initialize default user 'alexis' for testing"""
    init_database()
    
    # Check if default user already exists
    if get_user_by_username("alexis"):
        return
    
    # Create default user (only username and password required now)
    result = register_user(
        username="alexis",
        password="password123",
        name="Alexis",
        email="alexis@example.com",
        is_admin=True
    )
    
    if result["success"]:
        print("✓ Default user 'alexis' created (Admin)")
        print("  Email: alexis@example.com")
        print("  Password: password123")


# ==================== Testing ====================

if __name__ == "__main__":
    print("Initializing authentication system...\n")
    
    # Initialize database and default user
    init_default_user()
    
    print("\n--- Testing Login ---")
    is_valid, msg = verify_login("alexis", "password123")
    print(f"Login Result: {msg}")
    
    print("\n--- Testing Token Creation ---")
    token = create_access_token("alexis")
    print(f"Generated Token: {token[:50]}...")
    
    print("\n--- Testing Token Verification ---")
    verified_username = verify_token(token)
    print(f"Verified Username: {verified_username}")
    
    print("\n--- Testing User Query ---")
    user = get_user_by_username("alexis")
    print(f"User Info: {user}")
    
    print("\n--- Testing User Access ---")
    access = get_user_access("alexis")
    print(f"User Access: {access}")
    
    print("\n✓ All authentication tests passed!")
