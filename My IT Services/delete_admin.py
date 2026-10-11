
from project_db import SessionLocal, User

db = SessionLocal()

user = db.query(User).filter_by(username="admin").first()

if user:
    db.delete(user)
    db.commit()
    print("Адміна видалено!")
else:
    print("Користувача не знайдено")

db.close()