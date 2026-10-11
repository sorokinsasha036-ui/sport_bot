

from project_db import SessionLocal, User, Request

session = SessionLocal()

try:
    # Знаходимо всіх користувачів, крім адміністраторів
    test_users = session.query(User).filter(
        User.role != "admin"
    ).all()

    if not test_users:
        print("Тестових користувачів не знайдено.")
    else:
        user_ids = [user.id for user in test_users]

        # Видаляємо заявки тестових користувачів
        session.query(Request).filter(
            Request.user_id.in_(user_ids)
        ).delete(synchronize_session=False)

        # Видаляємо тестові акаунти
        for user in test_users:
            session.delete(user)

        session.commit()

        print(f"Видалено користувачів: {len(test_users)}")
        print("Адміністратори залишилися в базі.")

except Exception as error:
    session.rollback()
    print(f"Помилка: {error}")

finally:
    session.close()
