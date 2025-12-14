
import sys
import os

print("Sys Path:", sys.path)
try:
    import app
    print("App package found:", app)
    import app.core.database
    print("Database module found")
    from app.core.database import Base
    print("Base imported")
    import app.models.tenant
    print("Tenant model imported")
    import app.models
    print("Models package imported")
except Exception as e:
    print("ERROR:", e)
    import traceback
    traceback.print_exc()
