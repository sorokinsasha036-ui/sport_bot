
from project_db import SessionLocal, User
from werkzeug.security import generate_password_hash


db = SessionLocal()

admin = User(
    username="Олександр",
    email="sorokinsasha036@gmail.com",
    password_hash=generate_password_hash("Qwerty_2011"),
    role="admin"
)

db.add(admin)
db.commit()

print("Адмін створений!")

db.close()