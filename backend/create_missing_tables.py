from app.infrastructure.database import engine
from app.infrastructure.models import Base

print("Creating missing tables...")
Base.metadata.create_all(bind=engine)
print("Done.")
