from fastapi import APIRouter, HTTPException
from firebase_admin import auth, exceptions
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


router = APIRouter()


class UserMetadata(BaseModel):
    creation_timestamp: Optional[datetime]
    last_sign_in_timestamp: Optional[datetime]
    last_refresh_timestamp: Optional[datetime]


class UserRecord(BaseModel):
    """a user record from firebase auth"""

    uid: Optional[str] = None
    email: Optional[str] = None
    email_verified: Optional[bool] = None
    display_name: Optional[str] = None
    photo_url: Optional[str] = None
    phone_number: Optional[str] = None
    disabled: Optional[bool] = None
    user_metadata: Optional[dict] = None
    custom_claims: Optional[dict] = None
    tokens_valid_after_timestamp: Optional[datetime] = None
    provider_data: Optional[list] = None
    provider_id: Optional[str] = None


def user_record_from_user_data(user_data):
    userMetadata = UserMetadata(
        creation_timestamp=user_data.user_metadata.creation_timestamp,
        last_sign_in_timestamp=user_data.user_metadata.last_sign_in_timestamp,
        last_refresh_timestamp=user_data.user_metadata.last_refresh_timestamp,
    )
    userRecord = UserRecord(
        uid=user_data.uid,
        email=user_data.email,
        email_verified=user_data.email_verified,
        display_name=user_data.display_name,
        photo_url=user_data.photo_url,
        phone_number=user_data.phone_number,
        disabled=user_data.disabled,
        user_metadata=userMetadata,
        custom_claims=user_data.custom_claims,
        tokens_valid_after_timestamp=user_data.tokens_valid_after_timestamp,
        provider_data=user_data.provider_data,
        provider_id=user_data.provider_id,
    )
    return userRecord


class UserInfo(UserRecord):
    """
    info of a user passing to firebase auth
    based on UserRecord
    """

    password: Optional[str] = None


@router.post(
    "/create_user",
    summary="Create a new user in Firebase Authentication",
    response_description="JSON object representing the newly created user",
)
async def create_user(user: UserInfo):
    """
    Create a new user in Firebase Authentication.

    :param user: Pydantic model representing the user data to be created.
    :return: Pydantic model representing the newly created user.
    """
    try:
        user_data = auth.create_user(
            uid=user.uid,
            email=user.email,
            password=user.password,
            display_name=user.display_name,
            photo_url=user.photo_url,
            phone_number=user.phone_number,
            disabled=user.disabled,
            email_verified=user.email_verified,
        )
        return user_record_from_user_data(user_data)
    except exceptions.FirebaseError as e:
        raise HTTPException(status_code=400, detail=f"FirebaseError creating user: {e}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Unknown Error creating user: {e}")


@router.post(
    "/read_user",
    summary="Read a user in Firebase Authentication",
    response_description="JSON object representing the requested user",
)
async def read_user(user: UserInfo):
    """
    Read a user in Firebase Authentication.

    :param user: Pydantic model representing the user ID of the user to be retrieved.
    :return: Pydantic model representing the retrieved user.
    """
    try:
        user_data = auth.get_user(user.uid)
        return user_record_from_user_data(user_data)
    except exceptions.FirebaseError as e:
        raise HTTPException(status_code=400, detail=f"FirebaseError reading user: {e}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Unknown Error reading user: {e}")


class UserDeleteRequest(BaseModel):
    uid: str


@router.delete(
    "/delete_user",
    summary="Delete a user in Firebase Authentication",
    response_description="JSON object representing the deleted user",
)
async def delete_user(user: UserDeleteRequest):
    try:
        auth.delete_user(user.uid)
        return {"message": "User deleted successfully"}
    except exceptions.FirebaseError as e:
        raise HTTPException(status_code=400, detail=f"FirebaseError deleting user: {e}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Unknown Error deleting user: {e}")


@router.put(
    "/update_user",
    summary="Update a user in Firebase Authentication",
    response_description="JSON object representing the updated user",
)
async def update_user(user: UserInfo):
    try:
        updated_user = auth.update_user(
            user.uid,
            email=user.email,
            password=user.password,
            display_name=user.display_name,
            photo_url=user.photo_url,
            phone_number=user.phone_number,
            disabled=user.disabled,
            custom_claims=user.custom_claims,
            email_verified=user.email_verified,
        )
        return user_record_from_user_data(updated_user)
    except exceptions.FirebaseError as e:
        raise HTTPException(status_code=400, detail=f"FirebaseError updating user: {e}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Unknown Error updating user: {e}")


class UserEmailRequest(BaseModel):
    email: str

@router.post(
    "/send_verification_email",
    summary="Send a verification email to a user in Firebase Authentication",
    response_description="JSON object representing the user to whom the verification email was sent",
)
async def send_verification_email(user: UserEmailRequest):
    try:
        user = auth.get_user_by_email(user.email)
        auth.generate_email_verification_link(user.email)
        return {"message": f"Verification email sent to {user.email}"}
    except exceptions.FirebaseError as e:
        raise HTTPException(
            status_code=400, detail=f"FirebaseError sending verification email: {e}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Unknown Error sending verification email: {e}"
        )
