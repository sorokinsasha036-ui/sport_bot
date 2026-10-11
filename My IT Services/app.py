from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
)
import os
from sqlalchemy import or_
from flask_login import (
    LoginManager,
    current_user,
    login_user,
    logout_user,
    login_required,
)
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import joinedload

from project_db import (
    init_db,
    User,
    Service,
    Request,
    Review,
    SessionLocal,
)


app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY",
    "dev-only-change-me"
)
init_db()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

login_manager.login_message = (
    "Будь ласка, увійдіть в акаунт, щоб переглянути цю сторінку."
)
login_manager.login_message_category = "error"

@login_manager.user_loader
def load_user(user_id):
    db = SessionLocal()
    try:
        return db.query(User).filter_by(id=int(user_id)).first()
    finally:
        db.close()


# =========================
# Головна
# =========================

@app.route("/")
def index():
    db = SessionLocal()

    try:
        services = db.query(Service).all()

        reviews = (
            db.query(Review)
            .options(
                joinedload(Review.user),
                joinedload(Review.request).joinedload(Request.service),
            )
            .filter_by(is_published=True)
            .order_by(Review.created_at.desc())
            .limit(10)
            .all()
        )

        return render_template(
            "index.html",
            title="Головна",
            services=services,
            reviews=reviews,
        )

    finally:
        db.close()


# =========================
# Про мене
# =========================

@app.route("/about")
def about():
    return render_template("about.html", title="Про мене")



# =========================
# ПОСЛУГИ — ПОШУК І ФІЛЬТРАЦІЯ
# =========================

@app.route("/services")
def services():
    db = SessionLocal()

    try:
        # Отримуємо параметри з форми пошуку.
        search_query = request.args.get("q", "").strip()
        selected_category = request.args.get("category", "").strip()
        sort_by = request.args.get("sort", "").strip()

        # Початковий запит до бази даних.
        query = db.query(Service)

        # Пошук за назвою, описом або категорією.
        if search_query:
            search_pattern = f"%{search_query}%"

            query = query.filter(
                or_(
                    Service.name.ilike(search_pattern),
                    Service.description.ilike(search_pattern),
                    Service.category.ilike(search_pattern),
                )
            )

        # Фільтр за категорією.
        if selected_category:
            query = query.filter(
                Service.category == selected_category
            )

        # Сортування результатів.
        if sort_by == "price_asc":
            query = query.order_by(Service.price.asc())

        elif sort_by == "price_desc":
            query = query.order_by(Service.price.desc())

        elif sort_by == "name":
            query = query.order_by(Service.name.asc())

        else:
            query = query.order_by(Service.id.desc())

        services_list = query.all()

        # Список категорій, які вже є в базі даних.
        categories = [
            row[0]
            for row in (
                db.query(Service.category)
                .distinct()
                .order_by(Service.category)
                .all()
            )
        ]

        return render_template(
            "services.html",
            title="Послуги",
            services=services_list,
            categories=categories,
            search_query=search_query,
            selected_category=selected_category,
            sort_by=sort_by,
        )

    finally:
        db.close()


@app.route("/services/<int:service_id>")
def service_page(service_id):
    db = SessionLocal()
    try:
        service = db.query(Service).filter_by(id=service_id).first()

        if not service:
            return "Послугу не знайдено", 404

        return render_template(
            "service_page.html",
            title=service.name,
            service=service,
        )
    finally:
        db.close()


# =========================
# Вхід
# =========================

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    if request.method == "POST":
        email = request.form["email"].strip()
        password = request.form["password"]

        db = SessionLocal()
        try:
            user = db.query(User).filter_by(email=email).first()

            if not user or not check_password_hash(
                user.password_hash, password
            ):
                return render_template(
                    "login.html",
                    title="Вхід",
                    error="Неправильний email або пароль.",
                )

            login_user(user)
            role = user.role
        finally:
            db.close()

        if role == "admin":
            return redirect(url_for("admin_dashboard"))

        return redirect(url_for("index"))

    return render_template("login.html", title="Вхід")


# =========================
# Реєстрація
# =========================

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    if request.method == "POST":
        username = request.form["username"].strip()
        email = request.form["email"].strip()
        password = request.form["password"]
        password_confirm = request.form["password_confirm"]

        if password != password_confirm:
            return render_template(
                "register.html",
                title="Реєстрація",
                error="Паролі не співпадають.",
            )

        db = SessionLocal()
        try:
            if db.query(User).filter_by(username=username).first():
                return render_template(
                    "register.html",
                    title="Реєстрація",
                    error="Це ім'я користувача вже зайняте.",
                )

            if db.query(User).filter_by(email=email).first():
                return render_template(
                    "register.html",
                    title="Реєстрація",
                    error="Користувач з таким email вже існує.",
                )

            new_user = User(
                username=username,
                email=email,
                password_hash=generate_password_hash(password),
                role="user",
            )

            db.add(new_user)
            db.commit()
            login_user(new_user)

            return redirect(url_for("index"))
        finally:
            db.close()

    return render_template("register.html", title="Реєстрація")


# =========================
# АДМІН-ПАНЕЛЬ
# =========================

@app.route("/admin")
@login_required
def admin_dashboard():
    if current_user.role != "admin":
        return "Доступ заборонено", 403

    db = SessionLocal()
    try:
        services_count = db.query(Service).count()

        orders_count = db.query(Request).filter(
            Request.status.in_(
                ["accepted", "in_progress", "completed"]
            )
        ).count()

        requests_count = db.query(Request).filter_by(
            status="pending"
        ).count()

        users_count = db.query(User).count()

        reviews_count = db.query(Review).count()

        return render_template(
            "admin/index.html",
            services_count=services_count,
            orders_count=orders_count,
            requests_count=requests_count,
            users_count=users_count,
            reviews_count=reviews_count,
        )
    finally:
        db.close()


# =========================
# АДМІН — ПОСЛУГИ
# =========================

@app.route("/admin/services")
@login_required
def admin_services():
    if current_user.role != "admin":
        return "Доступ заборонено", 403

    db = SessionLocal()
    try:
        services = db.query(Service).all()
        return render_template("admin/services.html", services=services)
    finally:
        db.close()


@app.route("/admin/services/add", methods=["GET", "POST"])
@login_required
def admin_service_add():
    if current_user.role != "admin":
        return "Доступ заборонено", 403

    if request.method == "POST":
        name = request.form["name"].strip()
        category = request.form["category"].strip()
        description = request.form["description"].strip()
        price = request.form["price"]

        try:
            price = float(price)
            if price < 0:
                raise ValueError
        except ValueError:
            return render_template(
                "admin/service_form.html",
                title="Додати послугу",
                service=None,
                error="Введіть коректну ціну.",
            )

        db = SessionLocal()
        try:
            service = Service(
                name=name,
                category=category,
                description=description,
                price=price,
            )
            db.add(service)
            db.commit()
        finally:
            db.close()

        return redirect(url_for("admin_services"))

    return render_template(
        "admin/service_form.html",
        title="Додати послугу",
        service=None,
    )


@app.route(
    "/admin/services/<int:service_id>/edit",
    methods=["GET", "POST"],
)
@login_required
def admin_service_edit(service_id):
    if current_user.role != "admin":
        return "Доступ заборонено", 403

    db = SessionLocal()
    try:
        service = db.query(Service).filter_by(id=service_id).first()

        if not service:
            return "Послугу не знайдено", 404

        if request.method == "POST":
            service.name = request.form["name"].strip()
            service.category = request.form["category"].strip()
            service.description = request.form["description"].strip()

            try:
                price = float(request.form["price"])
                if price < 0:
                    raise ValueError
            except ValueError:
                return render_template(
                    "admin/service_form.html",
                    title="Редагувати послугу",
                    service=service,
                    error="Введіть коректну ціну.",
                )

            service.price = price
            db.commit()
            return redirect(url_for("admin_services"))

        return render_template(
            "admin/service_form.html",
            title="Редагувати послугу",
            service=service,
        )
    finally:
        db.close()


@app.route("/admin/services/<int:service_id>/delete", methods=["POST"])
@login_required
def admin_service_delete(service_id):
    if current_user.role != "admin":
        return "Доступ заборонено", 403

    db = SessionLocal()
    try:
        service = db.query(Service).filter_by(id=service_id).first()

        if not service:
            return "Послугу не знайдено", 404

        if db.query(Request).filter_by(service_id=service_id).first():
            return "Не можна видалити послугу, для якої є заявки.", 400

        db.delete(service)
        db.commit()
        return redirect(url_for("admin_services"))
    finally:
        db.close()


# =========================
# АДМІН — ЗАМОВЛЕННЯ
# =========================

@app.route("/admin/orders")
@login_required
def admin_orders():
    if current_user.role != "admin":
        return "Доступ заборонено", 403

    db = SessionLocal()

    try:
        orders = (
            db.query(Request)
            .options(
                joinedload(Request.user),
                joinedload(Request.service)
            )
            .filter(
                Request.status.in_([
                    "accepted",
                    "in_progress",
                    "completed"
                ])
            )
            .order_by(Request.id.desc())
            .all()
        )

        return render_template(
            "admin/orders.html",
            title="Замовлення",
            orders=orders
        )
    finally:
        db.close()


@app.route(
    "/admin/orders/<int:request_id>/status",
    methods=["POST"],
)
@login_required
def admin_order_update_status(request_id):
    if current_user.role != "admin":
        return "Доступ заборонено", 403

    allowed_statuses = {"accepted", "in_progress", "completed"}
    new_status = request.form.get("status", "")

    if new_status not in allowed_statuses:
        return "Некоректний статус замовлення", 400

    db = SessionLocal()
    try:
        order = db.query(Request).filter_by(id=request_id).first()

        if order is None:
            return "Замовлення не знайдено", 404

        if order.status not in allowed_statuses:
            return "Це замовлення ще не прийняте", 400

        order.status = new_status
        db.commit()
        return redirect(url_for("admin_orders"))
    finally:
        db.close()


# =========================
# АДМІН — ЗАЯВКИ
# =========================

@app.route("/admin/requests")
@login_required
def admin_requests():
    if current_user.role != "admin":
        return "Доступ заборонено", 403

    db = SessionLocal()
    try:
        requests_list = (
            db.query(Request)
            .options(
                joinedload(Request.user),
                joinedload(Request.service),
            )
            .filter(Request.status.in_(["pending", "rejected"]))
            .order_by(Request.created_at.desc())
            .all()
        )

        return render_template(
            "admin/requests.html",
            requests=requests_list,
        )
    finally:
        db.close()


@app.route("/admin/requests/<int:request_id>/accept", methods=["POST"])
@login_required
def admin_request_accept(request_id):
    if current_user.role != "admin":
        return "Доступ заборонено", 403

    db = SessionLocal()

    try:
        request_item = db.query(Request).filter_by(
            id=request_id
        ).first()

        if not request_item:
            return "Заявку не знайдено", 404

        if request_item.status != "pending":
            return redirect(url_for("admin_requests"))

        request_item.status = "accepted"
        db.commit()

        return redirect(url_for("admin_orders"))

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


@app.route(
    "/admin/requests/<int:request_id>/reject",
    methods=["POST"],
)
@login_required
def admin_request_reject(request_id):
    if current_user.role != "admin":
        return "Доступ заборонено", 403

    db = SessionLocal()
    try:
        request_item = db.query(Request).filter_by(id=request_id).first()

        if request_item is None:
            return "Заявку не знайдено", 404

        if request_item.status != "pending":
            return "Ця заявка вже опрацьована", 400

        request_item.status = "rejected"
        db.commit()
        return redirect(url_for("admin_requests"))
    finally:
        db.close()


# =========================
# АДМІН — КОРИСТУВАЧІ
# =========================

@app.route("/admin/users")
@login_required
def admin_users():
    if current_user.role != "admin":
        return "Доступ заборонено", 403

    db = SessionLocal()
    try:
        users = db.query(User).all()
        return render_template("admin/users.html", users=users)
    finally:
        db.close()


# =========================
# АДМІН — ВІДГУКИ
# =========================

@app.route("/admin/reviews")
@login_required
def admin_reviews():
    if current_user.role != "admin":
        return "Доступ заборонено", 403

    db = SessionLocal()

    try:
        reviews = (
            db.query(Review)
            .options(
                joinedload(Review.user),
                joinedload(Review.request).joinedload(Request.service),
            )
            .order_by(Review.created_at.desc())
            .all()
        )

        return render_template(
            "admin/reviews.html",
            title="Відгуки",
            reviews=reviews,
        )

    finally:
        db.close()


@app.route(
    "/admin/reviews/<int:review_id>/publish",
    methods=["POST"],
)
@login_required
def admin_review_publish(review_id):
    if current_user.role != "admin":
        return "Доступ заборонено", 403

    db = SessionLocal()

    try:
        review = db.query(Review).filter_by(id=review_id).first()

        if review is None:
            return "Відгук не знайдено", 404

        review.is_published = True
        db.commit()

        return redirect(url_for("admin_reviews"))

    finally:
        db.close()


@app.route(
    "/admin/reviews/<int:review_id>/hide",
    methods=["POST"],
)
@login_required
def admin_review_hide(review_id):
    if current_user.role != "admin":
        return "Доступ заборонено", 403

    db = SessionLocal()

    try:
        review = db.query(Review).filter_by(id=review_id).first()

        if review is None:
            return "Відгук не знайдено", 404

        review.is_published = False
        db.commit()

        return redirect(url_for("admin_reviews"))

    finally:
        db.close()


# =========================
# Вихід
# =========================

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


# =========================
# Створення заявки
# =========================

@app.route(
    "/services/<int:service_id>/request",
    methods=["GET", "POST"],
)
@login_required
def create_request(service_id):
    db = SessionLocal()
    try:
        service = db.query(Service).filter_by(id=service_id).first()

        if not service:
            return "Послугу не знайдено", 404

        if request.method == "POST":
            description = request.form.get("description", "").strip()

            if not description:
                return render_template(
                    "request_form.html",
                    title="Замовити послугу",
                    service=service,
                    error="Будь ласка, опишіть ваше завдання.",
                )

            new_request = Request(
                user_id=current_user.id,
                service_id=service.id,
                description=description,
                status="pending",
            )

            db.add(new_request)
            db.commit()
            return redirect(url_for("my_requests"))

        return render_template(
            "request_form.html",
            title="Замовити послугу",
            service=service,
        )
    finally:
        db.close()


# =========================
# Мої заявки та замовлення
# =========================

@app.route("/my-requests")
@login_required
def my_requests():
    db = SessionLocal()
    try:
        requests_list = (
            db.query(Request)
            .options(joinedload(Request.service))
            .filter_by(user_id=current_user.id)
            .order_by(Request.created_at.desc())
            .all()
        )

        return render_template(
            "my_requests.html",
            title="Мої заявки",
            requests=requests_list,
        )
    finally:
        db.close()


# =========================
# СКАСУВАННЯ ЗАМОВЛЕННЯ КЛІЄНТОМ
# =========================

@app.route(
    "/my-requests/<int:request_id>/cancel",
    methods=["POST"],
)
@login_required
def cancel_request(request_id):
    db = SessionLocal()

    try:
        order = db.query(Request).filter_by(
            id=request_id,
            user_id=current_user.id,
        ).first()

        if order is None:
            flash("Замовлення не знайдено.", "error")

        elif order.status != "pending":
            flash(
                "Скасувати можна лише заявку, "
                "яку адміністратор ще не прийняв.",
                "error",
            )

        else:
            order.status = "cancelled"
            db.commit()

            flash("Заявку успішно скасовано.", "success")

        return redirect(url_for("my_requests"))

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()

# =========================
# ОСОБИСТИЙ КАБІНЕТ
# =========================

@app.route("/profile")
@login_required
def profile():
    db = SessionLocal()

    try:
        profile_user = db.query(User).filter_by(
            id=current_user.id
        ).first()

        if profile_user is None:
            return "Користувача не знайдено", 404

        user_requests = db.query(Request).filter_by(
            user_id=current_user.id
        )

        total_requests = user_requests.count()

        pending_requests = user_requests.filter_by(
            status="pending"
        ).count()

        active_requests = user_requests.filter(
            Request.status.in_(["accepted", "in_progress"])
        ).count()

        completed_requests = user_requests.filter_by(
            status="completed"
        ).count()

        recent_requests = (
            db.query(Request)
            .options(joinedload(Request.service))
            .filter_by(user_id=current_user.id)
            .order_by(Request.created_at.desc())
            .limit(5)
            .all()
        )

        return render_template(
            "profile.html",
            title="Особистий кабінет",
            profile_user=profile_user,
            total_requests=total_requests,
            pending_requests=pending_requests,
            active_requests=active_requests,
            completed_requests=completed_requests,
            recent_requests=recent_requests,
        )

    finally:
        db.close()

# =========================
# ВІДГУКИ — СТВОРЕННЯ
# =========================

@app.route(
    "/my-requests/<int:request_id>/review",
    methods=["GET", "POST"],
)
@login_required
def create_review(request_id):
    db = SessionLocal()

    try:
        order = (
            db.query(Request)
            .options(
                joinedload(Request.service),
                joinedload(Request.review),
            )
            .filter_by(
                id=request_id,
                user_id=current_user.id,
            )
            .first()
        )

        if order is None:
            return "Замовлення не знайдено", 404

        if order.status != "completed":
            return "Відгук можна залишити лише після виконання замовлення.", 400

        existing_review = (
            db.query(Review)
            .filter_by(request_id=order.id)
            .first()
        )

        if existing_review:
            return "Ви вже залишили відгук на це замовлення.", 400

        if request.method == "POST":
            try:
                rating = int(request.form.get("rating", "0"))
            except ValueError:
                rating = 0

            comment = request.form.get("comment", "").strip()

            if rating not in range(1, 6):
                return render_template(
                    "review_form.html",
                    title="Залишити відгук",
                    order=order,
                    error="Оберіть оцінку від 1 до 5 зірок.",
                )

            if not comment or len(comment) > 2000:
                return render_template(
                    "review_form.html",
                    title="Залишити відгук",
                    order=order,
                    error="Коментар має містити від 1 до 2000 символів.",
                )

            review = Review(
                user_id=current_user.id,
                request_id=order.id,
                rating=rating,
                comment=comment,
                is_published=False,
            )

            db.add(review)
            db.commit()

            return redirect(url_for("my_requests"))

        return render_template(
            "review_form.html",
            title="Залишити відгук",
            order=order,
        )

    finally:
        db.close()


# =========================
# Запуск
# =========================

if __name__ == "__main__":
    app.run(debug=True)