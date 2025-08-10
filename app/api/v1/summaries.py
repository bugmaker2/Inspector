"""Summaries API endpoints."""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database.database import get_db
from app.models.member import Summary
from app.models.schemas import Summary as SummarySchema
from app.services.summarizers.llm_summarizer import LLMSummarizer

router = APIRouter()


@router.get("/", response_model=List[SummarySchema])
def get_summaries(
    skip: int = 0,
    limit: int = 20,
    summary_type: str = None,
    language: str = "chinese",
    db: Session = Depends(get_db)
):
    """Get all summaries with optional filtering."""
    query = db.query(Summary)
    
    if summary_type:
        query = query.filter(Summary.summary_type == summary_type)
    
    # Apply language filter based on content field
    if language == "chinese":
        query = query.filter(Summary.content.isnot(None))
    elif language == "english":
        query = query.filter(Summary.content_en.isnot(None))
    
    summaries = query.order_by(Summary.created_at.desc()).offset(skip).limit(limit).all()
    return summaries


@router.get("/{summary_id}", response_model=SummarySchema)
def get_summary(
    summary_id: int,
    language: str = "chinese",
    db: Session = Depends(get_db)
):
    """Get a specific summary by ID."""
    summary = db.query(Summary).filter(Summary.id == summary_id).first()
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Summary not found"
        )
    return summary


@router.post("/", response_model=SummarySchema, status_code=status.HTTP_201_CREATED)
async def create_summary(
    summary_data: dict,
    db: Session = Depends(get_db)
):
    """Create a new summary."""
    try:
        summary = Summary(**summary_data)
        db.add(summary)
        db.commit()
        db.refresh(summary)
        return summary
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create summary: {str(e)}"
        )


@router.post("/generate-daily", response_model=SummarySchema, status_code=status.HTTP_201_CREATED)
async def generate_daily_summary(
    date: str = None,
    db: Session = Depends(get_db)
):
    """Generate daily summary."""
    try:
        summarizer = LLMSummarizer(db)
        summary = await summarizer.generate_daily_summary()
        if not summary:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No activities found for daily summary"
            )
        return summary
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate daily summary: {str(e)}"
        )


@router.post("/generate-weekly", response_model=SummarySchema, status_code=status.HTTP_201_CREATED)
async def generate_weekly_summary(
    start_date: str = None,
    db: Session = Depends(get_db)
):
    """Generate weekly summary."""
    try:
        summarizer = LLMSummarizer(db)
        summary = await summarizer.generate_weekly_summary()
        if not summary:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No activities found for weekly summary"
            )
        return summary
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate weekly summary: {str(e)}"
        )


@router.delete("/{summary_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_summary(
    summary_id: int,
    db: Session = Depends(get_db)
):
    """Delete a summary."""
    summary = db.query(Summary).filter(Summary.id == summary_id).first()
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Summary not found"
        )
    
    db.delete(summary)
    db.commit()
    return None
