from project_db import SessionLocal, Service


db = SessionLocal()


services = [
    Service(
        name="Веб-розробка",
        description="Створення сучасних вебсайтів, інтернет-магазинів, вебзастосунків та адміністративних панелей.",
        price=5000,
        category="Веб-розробка"
    ),

    Service(
        name="Розробка програмного забезпечення",
        description="Створення програм, backend-систем, REST API та індивідуальних програмних рішень.",
        price=7000,
        category="Програмне забезпечення"
    ),

    Service(
        name="Telegram-боти",
        description="Розробка Telegram-ботів для бізнесу, автоматизації, замовлень та взаємодії з користувачами.",
        price=3000,
        category="Telegram"
    ),

    Service(
        name="Автоматизація",
        description="Автоматизація рутинних операцій, обробки даних, web scraping та інтеграції різних сервісів.",
        price=4000,
        category="Автоматизація"
    ),

    Service(
        name="AI-рішення",
        description="Інтеграція можливостей штучного інтелекту у вебсайти, програми, ботів та автоматизовані системи.",
        price=5000,
        category="AI"
    ),

    Service(
        name="Підтримка та доопрацювання",
        description="Виправлення помилок, додавання нових функцій, оптимізація та технічна підтримка існуючих проєктів.",
        price=1500,
        category="Підтримка"
    )
]


for service in services:
    db.add(service)


db.commit()
db.close()

print("Усі послуги успішно додані!")