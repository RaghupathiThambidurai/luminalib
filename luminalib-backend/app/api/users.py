"""User routes"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List
from app.domain.entities import User, UserCreate
from app.services.user_service import UserService
from app.core.exceptions import NotFoundError, ValidationError

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


# Dependency to get UserService (will be injected)
async def get_user_service() -> UserService:
    """Get user service instance"""
    from app.core.di import DIContainer
    return DIContainer.get("user_service")


@router.post("/", response_model=User, status_code=201)
async def create_user(
    user_data: UserCreate,
    service: UserService = Depends(get_user_service)
):
    """Create a new user"""
    try:
        user = await service.create_user(
            user_data.username,
            user_data.email,
            user_data.password,
            user_data.full_name
        )
        return user
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}", response_model=User)
async def get_user(user_id: str, service: UserService = Depends(get_user_service)):
    """Get user by ID"""
    try:
        user = await service.get_user(user_id)
        return user
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: str,
    full_name: str = None,
    is_active: bool = None,
    service: UserService = Depends(get_user_service)
):
    """Update user"""
    try:
        updates = {}
        if full_name is not None:
            updates['full_name'] = full_name
        if is_active is not None:
            updates['is_active'] = is_active
        
        user = await service.update_user(user_id, **updates)
        return user
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: str, service: UserService = Depends(get_user_service)):
    """Delete user"""
    try:
        await service.delete_user(user_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/", response_model=List[User])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    service: UserService = Depends(get_user_service)
):
    """List users"""
    users = await service.list_users(skip, limit)
    return users
