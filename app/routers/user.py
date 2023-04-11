from fastapi import APIRouter, HTTPException
from firebase_admin import auth, exceptions
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class UserReadRequest(BaseModel):
    uid: str

class UserReadResponse(BaseModel):
    uid: str
    email: str
    email_verified: bool
    display_name: Optional[str] = None

@router.post(
    "/read_user",
    summary="Read a user in Firebase Authentication",
    response_description="JSON object representing the requested user"
)
async def read_user(user: UserReadRequest):
    """
    Read a user in Firebase Authentication.

    :param user: Pydantic model representing the user ID of the user to be retrieved.
    :return: Pydantic model representing the retrieved user.
    """
    try:
        user_data = auth.get_user(user.uid)
        return UserReadResponse(
            uid=user_data.uid,
            email=user_data.email,
            email_verified=user_data.email_verified,
            display_name=user_data.display_name
        )
    except exceptions.FirebaseError as e:
        raise HTTPException(status_code=400, detail=f"FirebaseError reading user: {e}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Unknown Error reading user: {e}")



class UserCreateRequest(BaseModel):
    email: str
    password: str
    display_name: Optional[str] = None

@router.post(
    "/create_user",
    summary="Create a new user in Firebase Authentication",
    response_description="JSON object representing the newly created user"
)
async def create_user(user: UserCreateRequest):
    """
    Create a new user in Firebase Authentication.

    :param user: Pydantic model representing the user data to be created.
    :return: Pydantic model representing the newly created user.
    """
    try:
        user_data = auth.create_user(
            email=user.email,
            password=user.password,
            display_name=user.display_name
        )
        return user_data.as_dict()
    except exceptions.FirebaseError as e:
        raise HTTPException(status_code=400, detail=f"FirebaseError creating user: {e}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Unknown Error creating user: {e}")




class UserDeleteRequest(BaseModel):
    uid: str

@router.delete(
    "/delete_user",
    summary="Delete a user in Firebase Authentication",
    response_description="JSON object representing the deleted user"
)
async def delete_user(user: UserDeleteRequest):
    try:
        auth.delete_user(user.uid)
        return {"message": "User deleted successfully"}
    except exceptions.FirebaseError as e:
        raise HTTPException(status_code=400, detail=f"FirebaseError deleting user: {e}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Unknown Error deleting user: {e}")



class UserUpdateRequest(BaseModel):
    uid: str
    email: str
    password: str
    display_name: Optional[str] = None

@router.put(
    "/update_user",
    summary="Update a user in Firebase Authentication",
    response_description="JSON object representing the updated user"
)
async def update_user(user: UserUpdateRequest):
    try:
        updated_user = auth.update_user(user.uid, email=user.email, password=user.password, display_name=user.display_name)
        return updated_user.to_dict()
    except exceptions.FirebaseError as e:
        raise HTTPException(status_code=400, detail=f"FirebaseError updating user: {e}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Unknown Error updating user: {e}")



class UserEmailRequest(BaseModel):
    email: str

@router.post(
    "/send_verification_email",
    summary="Send a verification email to a user in Firebase Authentication",
    response_description="JSON object representing the user to whom the verification email was sent"
)
async def send_verification_email(user: UserEmailRequest):
    try:
        user = auth.get_user_by_email(user.email)
        auth.generate_email_verification_link(user.email)
        return {"message": f"Verification email sent to {user.email}"}
    except exceptions.FirebaseError as e:
        raise HTTPException(status_code=400, detail=f"FirebaseError sending verification email: {e}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Unknown Error sending verification email: {e}")
