import uuid
from typing import Optional
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin, models
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy
)
from fastapi_users.db import SQLAlchemyUserDatabase
from app.db import User, get_user_db

SECRET = "123456"

class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET
    
    async def on_after_register(self, user: User, request : Optional[Request] = None): # Many built in functions for diferent situations - on_after_forgot_password, on_after_request_verify, etc
        print (f"User {user.id} has registered.")
        
    async def on_after_forgot_password(self, user: User, token: str, request : Optional[Request] = None):
        print (f"User {user.id} has forgot their password. Reset token: {token}")
        
def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):   #UserManager is a class from FastAPI Users where you implement:-password validation, -user creation logic, -hooks like on_after_register, -authentication rules
    yield UserManager(user_db)  #This makes it a dependency with cleanup support.
    
bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")   #defines how the token is sent in HTTP requests. In this case, it's a Bearer token sent in the Authorization header. tokenUrl is the URL where clients can obtain a token.

def get_jwt_strategy():
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)    #defines how JWT tokens are created and validated

auth_backend = AuthenticationBackend(
    name = "jwt",
    transport = bearer_transport,
    get_strategy= get_jwt_strategy
)   #Defines an authentication backend that combines the transport and strategy. This is what FastAPI Users will use to handle authentication.
#FastAPI Users supports multiple backends:Example possibilities: -JWT, -OAuth, -Cookie sessions, -API keys

fastapi_users = FastAPIUsers[User, uuid.UUID](get_user_manager, [auth_backend]) #creates the FastAPI Users engine
current_active_user = fastapi_users.current_user(active=True)    #This creates a dependency that returns the authenticated user.s