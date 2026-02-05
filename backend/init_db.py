"""
Simple script to initialize the database and create all tables
"""
from app.infrastructure.database import engine
from app.infrastructure import models

# Create all tables
print("Creating database tables...")
models.Base.metadata.create_all(bind=engine)
print("✅ Database tables created successfully!")
print("\nTables created:")
for table in models.Base.metadata.tables.keys():
    print(f"  - {table}")
