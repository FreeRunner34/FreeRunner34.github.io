import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.orm import sessionmaker, declarative_base, scoped_session

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "app.db")

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")

# --- Database setup (SQLite) ---
engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
SessionLocal = scoped_session(sessionmaker(bind=engine, autoflush=False, autocommit=False))
Base = declarative_base()

class WorkOrder(Base):
    __tablename__ = "work_orders"
    id = Column(Integer, primary_key=True)
    customer_name = Column(String(120), nullable=False)
    vehicle = Column(String(120), nullable=False)  # e.g., '2013 Infiniti G37S'
    complaint = Column(Text, nullable=False)       # primary customer concern
    status = Column(String(40), nullable=False, default="Open")  # Open, In Progress, Closed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

Base.metadata.create_all(bind=engine)

def get_session():
    return SessionLocal()


from functools import wraps
from flask import session, Response

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin")

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("logged_in"):
            flash("Please log in first.", "error")
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)
    return wrapped

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        password = request.form.get("password", "")
        if password == ADMIN_PASSWORD:
            session["logged_in"] = True
            flash("Logged in.", "success")
            next_url = request.args.get("next") or url_for("index")
            return redirect(next_url)
        else:
            flash("Invalid password.", "error")
            return redirect(url_for("login"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out.", "success")
    return redirect(url_for("index"))

@app.route("/export.csv")
@login_required
def export_csv():
    session_db = get_session()
    items = session_db.query(WorkOrder).order_by(WorkOrder.created_at.desc()).all()
    def generate():
        yield "id,customer_name,vehicle,status,created_at,updated_at,complaint\n"
        for wo in items:
            row = [
                wo.id,
                '"' + (wo.customer_name or "").replace('"','""') + '"',
                '"' + (wo.vehicle or "").replace('"','""') + '"',
                '"' + (wo.status or "").replace('"','""') + '"',
                wo.created_at.strftime("%Y-%m-%d %H:%M:%S") if wo.created_at else "",
                wo.updated_at.strftime("%Y-%m-%d %H:%M:%S") if wo.updated_at else "",
                '"' + (wo.complaint or "").replace('"','""').replace("\n"," ").replace("\r"," ") + '"',
            ]
            yield ",".join(map(str, row)) + "\n"
    return Response(generate(), mimetype="text/csv",
                    headers={"Content-Disposition": "attachment; filename=work_orders.csv"})

@app.route("/seed-demo")
@login_required
def seed_demo():
    session_db = get_session()
    samples = [
        ("Amara J.", "2013 Infiniti G37S", "Hard top won't close; HYD pump noise; DTC B23XX", "Open"),
        ("Archer R.", "2015 Chevy Suburban 5.3L", "Intermittent no crank; suspect starter/grounds", "In Progress"),
        ("Athena R.", "2020 Nissan Pathfinder", "Sunroof drains clogged; wet headliner", "Open"),
        ("Nik R.", "2017 Ford F-150 3.5 EB", "Underboost under load; P0299; smoke test needed", "Closed"),
    ]
    for c,v,comp,st in samples:
        session_db.add(WorkOrder(customer_name=c, vehicle=v, complaint=comp, status=st))
    session_db.commit()
    flash("Demo data seeded.", "success")
    return redirect(url_for("index"))
@app.teardown_appcontext
def remove_session(exception=None):
    SessionLocal.remove()

# --- Routes ---
@app.route("/")
def index():
    session = get_session()
    q = request.args.get("q", "").strip()
    if q:
        items = session.query(WorkOrder).filter(
            (WorkOrder.customer_name.ilike(f"%{q}%")) | 
            (WorkOrder.vehicle.ilike(f"%{q}%")) |
            (WorkOrder.status.ilike(f"%{q}%")) |
            (WorkOrder.complaint.ilike(f"%{q}%"))
        ).order_by(WorkOrder.created_at.desc()).all()
    else:
        items = session.query(WorkOrder).order_by(WorkOrder.created_at.desc()).all()
    return render_template("index.html", items=items, q=q)

@app.route("/new", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "POST":
        customer_name = request.form.get("customer_name", "").strip()
        vehicle = request.form.get("vehicle", "").strip()
        complaint = request.form.get("complaint", "").strip()
        status = request.form.get("status", "Open").strip() or "Open"
        if not customer_name or not vehicle or not complaint:
            flash("Customer name, vehicle, and complaint are required.", "error")
            return redirect(url_for("create"))
        session = get_session()
        wo = WorkOrder(customer_name=customer_name, vehicle=vehicle, complaint=complaint, status=status)
        session.add(wo)
        session.commit()
        flash("Work order created.", "success")
        return redirect(url_for("index"))
    return render_template("create.html")

@app.route("/wo/<int:wo_id>")
def detail(wo_id):
    session = get_session()
    wo = session.query(WorkOrder).get(wo_id)
    if not wo:
        flash("Work order not found.", "error")
        return redirect(url_for("index"))
    return render_template("detail.html", wo=wo)

@app.route("/wo/<int:wo_id>/edit", methods=["GET", "POST"])
@login_required
def edit(wo_id):
    session = get_session()
    wo = session.query(WorkOrder).get(wo_id)
    if not wo:
        flash("Work order not found.", "error")
        return redirect(url_for("index"))
    if request.method == "POST":
        wo.customer_name = request.form.get("customer_name", wo.customer_name).strip()
        wo.vehicle = request.form.get("vehicle", wo.vehicle).strip()
        wo.complaint = request.form.get("complaint", wo.complaint).strip()
        wo.status = request.form.get("status", wo.status).strip()
        session.commit()
        flash("Work order updated.", "success")
        return redirect(url_for("detail", wo_id=wo.id))
    return render_template("edit.html", wo=wo)

@app.route("/wo/<int:wo_id>/delete", methods=["POST"])
@login_required
def delete(wo_id):
    session = get_session()
    wo = session.query(WorkOrder).get(wo_id)
    if wo:
        session.delete(wo)
        session.commit()
        flash("Work order deleted.", "success")
    else:
        flash("Work order not found.", "error")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
