from uuid import UUID
from fastapi import APIRouter, status, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from sqlalchemy.exc import IntegrityError
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.models.product import Category
from app.schemas.product_schema import CategoryCreate, CategoryRead, CategoryUpdate
from app.db import get_session

router = APIRouter()

limiter = Limiter(key_func=get_remote_address)

@router.post("/categories", response_model=CategoryRead, status_code=status.HTTP_201_CREATED, summary="Create a new category")
async def create_category(category_in: CategoryCreate, session: AsyncSession = Depends(get_session)):
    category = Category.model_validate(category_in)
    session.add(category)
    try:
        await session.commit()
        await session.refresh(category)
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Category already exists")
    return category

@router.get("/categories", response_model=list[CategoryRead], summary="Get all categories")
# @limiter.limit("10/minute")
async def read_categories(session: AsyncSession = Depends(get_session)):
    categories = await session.exec(select(Category))
    return categories.all()

@router.get("/categories/{category_id}", response_model=CategoryRead, summary="Get a category by ID")
async def read_category(category_id: str, session: AsyncSession = Depends(get_session)):
    try:
        category_id = UUID(category_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid UUID")
    
    category = await session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return category

@router.patch("/categories/{category_id}", response_model=CategoryRead, summary="Update a category by ID")
async def update_category(category_id: str, category_in: CategoryUpdate, session: AsyncSession = Depends(get_session)):
    try:
        category_id = UUID(category_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid UUID")
    
    category = await session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    
    update_data = category_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(category, key, value)
    
    session.add(category)
    await session.commit()
    await session.refresh(category)
    return category

@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a category by ID")
async def delete_category(category_id: str, session: AsyncSession = Depends(get_session)):
    try:
        category_id = UUID(category_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid UUID")
    
    category = await session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    session.delete(category)
    await session.commit()
    return