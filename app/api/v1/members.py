"""Member management API endpoints."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database.database import get_db
from app.models.member import Member, SocialProfile
from app.models.schemas import (
    MemberCreate, MemberUpdate, Member as MemberSchema,
    MemberWithProfiles, SocialProfileCreate, SocialProfileUpdate,
    SocialProfile as SocialProfileSchema
)

router = APIRouter()


@router.post("/", response_model=MemberSchema, status_code=status.HTTP_201_CREATED)
def create_member(member: MemberCreate, db: Session = Depends(get_db)):
    """Create a new team member."""
    # Check if email already exists
    existing_member = db.query(Member).filter(Member.email == member.email).first()
    if existing_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    db_member = Member(**member.dict())
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member


@router.get("/", response_model=List[MemberSchema])
def get_members(
    skip: int = 0, 
    limit: int = 100, 
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """Get list of team members."""
    query = db.query(Member)
    if active_only:
        query = query.filter(Member.is_active == True)
    
    members = query.offset(skip).limit(limit).all()
    return members


@router.get("/{member_id}", response_model=MemberWithProfiles)
def get_member(member_id: int, db: Session = Depends(get_db)):
    """Get a specific team member with their social profiles."""
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )
    return member


@router.put("/{member_id}", response_model=MemberSchema)
def update_member(
    member_id: int, 
    member_update: MemberUpdate, 
    db: Session = Depends(get_db)
):
    """Update a team member."""
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )
    
    # Update only provided fields
    update_data = member_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(member, field, value)
    
    db.commit()
    db.refresh(member)
    return member


@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_member(member_id: int, db: Session = Depends(get_db)):
    """Delete a team member (soft delete by setting is_active=False)."""
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )
    
    member.is_active = False
    db.commit()
    return None


# Social Profile endpoints
@router.post("/{member_id}/social-profiles", response_model=SocialProfileSchema, status_code=status.HTTP_201_CREATED)
def create_social_profile(
    member_id: int, 
    profile: SocialProfileCreate, 
    db: Session = Depends(get_db)
):
    """Add a social profile to a team member."""
    try:
        # Verify member exists
        member = db.query(Member).filter(Member.id == member_id).first()
        if not member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Member not found"
            )
        
        # Check if profile already exists for this platform
        existing_profile = db.query(SocialProfile).filter(
            SocialProfile.member_id == member_id,
            SocialProfile.platform == profile.platform
        ).first()
        
        if existing_profile:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Social profile for {profile.platform} already exists for this member"
            )
        
        # Create profile with member_id from URL
        profile_data = profile.dict()
        profile_data['member_id'] = member_id
        # Convert HttpUrl to string for database storage
        if 'profile_url' in profile_data and hasattr(profile_data['profile_url'], '__str__'):
            profile_data['profile_url'] = str(profile_data['profile_url'])
        db_profile = SocialProfile(**profile_data)
        db.add(db_profile)
        db.commit()
        db.refresh(db_profile)
        return db_profile
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create social profile: {str(e)}"
        )


@router.get("/{member_id}/social-profiles", response_model=List[SocialProfileSchema])
def get_member_social_profiles(member_id: int, db: Session = Depends(get_db)):
    """Get all social profiles for a team member."""
    # Verify member exists
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )
    
    profiles = db.query(SocialProfile).filter(
        SocialProfile.member_id == member_id
    ).all()
    return profiles


@router.put("/{member_id}/social-profiles/{profile_id}", response_model=SocialProfileSchema)
def update_social_profile(
    member_id: int,
    profile_id: int,
    profile_update: SocialProfileUpdate,
    db: Session = Depends(get_db)
):
    """Update a social profile."""
    profile = db.query(SocialProfile).filter(
        SocialProfile.id == profile_id,
        SocialProfile.member_id == member_id
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Social profile not found"
        )
    
    # Update only provided fields
    update_data = profile_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)
    
    db.commit()
    db.refresh(profile)
    return profile


@router.delete("/{member_id}/social-profiles/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_social_profile(member_id: int, profile_id: int, db: Session = Depends(get_db)):
    """Delete a social profile."""
    profile = db.query(SocialProfile).filter(
        SocialProfile.id == profile_id,
        SocialProfile.member_id == member_id
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Social profile not found"
        )
    
    db.delete(profile)
    db.commit()
    return None 