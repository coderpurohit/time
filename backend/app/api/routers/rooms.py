
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..schemas import Room, RoomCreate
from ...infrastructure.database import get_db
from ...infrastructure import models

router = APIRouter()

@router.post("/", response_model=Room)
def create_room(room: RoomCreate, db: Session = Depends(get_db)):
    # Check for duplicate room name
    existing = db.query(models.Room).filter(models.Room.name == room.name).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Room with name {room.name} already exists")
    
    db_room = models.Room(
        name=room.name, 
        capacity=room.capacity,
        type=room.type,
        resources=room.resources
    )
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    return db_room

@router.get("/", response_model=List[Room])
def read_rooms(
    skip: int = 0, 
    limit: int = 100,
    room_type: Optional[str] = Query(None, description="Filter by room type"),
    min_capacity: Optional[int] = Query(None, description="Minimum capacity"),
    db: Session = Depends(get_db)
):
    query = db.query(models.Room)
    
    # Apply filters
    if room_type:
        query = query.filter(models.Room.type == room_type)
    
    if min_capacity is not None:
        query = query.filter(models.Room.capacity >= min_capacity)
    
    rooms = query.offset(skip).limit(limit).all()
    return rooms

@router.get("/{room_id}", response_model=Room)
def get_room(room_id: int, db: Session = Depends(get_db)):
    room = db.query(models.Room).filter(models.Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail=f"Room with id {room_id} not found")
    return room

@router.put("/{room_id}", response_model=Room)
def update_room(room_id: int, room: RoomCreate, db: Session = Depends(get_db)):
    db_room = db.query(models.Room).filter(models.Room.id == room_id).first()
    if not db_room:
        raise HTTPException(status_code=404, detail=f"Room with id {room_id} not found")
    
    # Check name uniqueness if changing
    if room.name != db_room.name:
        existing = db.query(models.Room).filter(models.Room.name == room.name).first()
        if existing:
            raise HTTPException(status_code=400, detail=f"Room with name {room.name} already exists")
    
    db_room.name = room.name
    db_room.capacity = room.capacity
    db_room.type = room.type
    db_room.resources = room.resources
    
    db.commit()
    db.refresh(db_room)
    return db_room

@router.delete("/{room_id}")
def delete_room(room_id: int, db: Session = Depends(get_db)):
    db_room = db.query(models.Room).filter(models.Room.id == room_id).first()
    if not db_room:
        raise HTTPException(status_code=404, detail=f"Room with id {room_id} not found")
    
    db.delete(db_room)
    db.commit()
    return {"message": f"Room {room_id} deleted successfully"}
