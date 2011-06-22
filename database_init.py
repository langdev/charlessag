
import database
from database import Base

if not Base.metadata.is_bound():
    Base.metadata.connect(engine)
Base.metadata.create_all()
