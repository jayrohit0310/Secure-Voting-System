from flask import Flask, render_template, request, redirect, session, url_for
from ai_model.face_recognition import verify_face
import sqlite3
import random

app = Flask(__name__)
app.secret_key = "secret123"

def get_db():
    return sqlite3.connect("database.db")

def init_db():
    db = get_db()
    db.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)")
    cnt = db.execute("SELECT COUNT(*) FROM settings WHERE key='resultsDeclared'").fetchone()[0]
    if cnt == 0:
        db.execute("INSERT INTO settings (key, value) VALUES ('resultsDeclared', 'false')")

    db.execute("CREATE TABLE IF NOT EXISTS candidates (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, party TEXT, image_url TEXT)")
    cand_cnt = db.execute("SELECT COUNT(*) FROM candidates").fetchone()[0]
    if cand_cnt == 0:
        db.execute("INSERT INTO candidates (name, party, image_url) VALUES ('Narendra Modi', 'Prime Minister of India', '/static/modi.jpg')")
        db.execute("INSERT INTO candidates (name, party, image_url) VALUES ('Rahul Gandhi', 'Indian National Congress Leader', '/static/rahul.jpg')")

    db.commit()
    db.close()

with app.app_context():
    init_db()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/start_voting")
def start_voting():
    if "user" in session:
        return redirect("/vote")
    else:
        return redirect("/login")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        voter_id = request.form["voter_id"]
        email = request.form["email"]

        db = get_db()

        # Check duplicate voter_id
        existing_voter = db.execute(
            "SELECT * FROM users WHERE voter_id=?", (voter_id,)
        ).fetchone()
        if existing_voter:
            db.close()
            return redirect("/register?error=voterid")

        # Check duplicate email
        existing_email = db.execute(
            "SELECT * FROM users WHERE email=?", (email,)
        ).fetchone()
        if existing_email:
            db.close()
            return redirect("/register?error=email")

        db.execute(
            "INSERT INTO users(name,voter_id,email) VALUES(?,?,?)",
            (name, voter_id, email)
        )
        db.commit()
        db.close()

        return redirect("/register?success=1")

    return render_template("register.html")


@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        action = request.form.get("action")
        db = get_db()

        if action == "send_otp":
            email = request.form.get("email")
            user = db.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
            db.close()

            if user:
                otp = str(random.randint(100000, 999999))
                session["otp"] = otp
                session["otp_email"] = email
                print(f"--- OTP for {email} is {otp} ---")
                return render_template("login.html", otp_sent=True, email=email, otp=otp)
            else:
                return redirect("/login?error=notfound")
                
        elif action == "verify_otp":
            email = request.form.get("email")
            entered_otp = request.form.get("otp")
            
            if "otp" in session and session["otp"] == entered_otp and session.get("otp_email") == email:
                user = db.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
                db.close()
                if user:
                    session["user"] = user[0] # Usually voter_id or id
                    session.pop("otp", None)
                    session.pop("otp_email", None)
                    return redirect("/login?success=1")
            
            db.close()
            return render_template("login.html", otp_sent=True, email=email, error="Invalid OTP")

    return render_template("login.html", otp_sent=False)

@app.route("/face_verify", methods=["GET","POST"])
def face_verify():
    if request.method == "POST":
        result = verify_face()
        if result:
            return redirect("/vote")
        else:
            return redirect("/face_verify?error=face_failed")
    return render_template("face_verify.html")

@app.route("/vote", methods=["GET","POST"])
def vote():
    if "user" not in session:
        return redirect("/login")

    db = get_db()

    # Check if already voted
    already = db.execute(
        "SELECT * FROM votes WHERE voter_id=?",
        (session["user"],)
    ).fetchone()

    if already:
        db.close()
        return redirect("/?error=already_voted")

    if request.method == "POST":
        choice = request.form["candidate"]
        db.execute(
            "INSERT INTO votes(candidate, voter_id) VALUES(?,?)",
            (choice, session["user"])
        )
        db.commit()
        db.close()
        session.pop("user", None)
        return redirect("/?success=voted")

    candidates = db.execute("SELECT id, name, party, image_url FROM candidates").fetchall()
    db.close()
    return render_template("vote.html", candidates=candidates)

@app.route("/result")
def result():
    db = get_db()
    settings = db.execute("SELECT value FROM settings WHERE key='resultsDeclared'").fetchone()
    declared = settings and settings[0] == 'true'
    
    data = []
    if declared:
        data = db.execute(
            "SELECT candidate, COUNT(*) FROM votes GROUP BY candidate"
        ).fetchall()
        
    db.close()
    return render_template("result.html", data=data, declared=declared)

@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        admin_id = request.form.get("admin_id")
        password = request.form.get("password")
        if admin_id == "admin123" and password == "admin@123":
            session["admin"] = True
            return redirect("/admin")
        else:
            return redirect("/admin_login?error=invalid")
    return render_template("admin_login.html")

@app.route("/admin")
def admin():
    if not session.get("admin"):
        return redirect("/admin_login")
        
    db = get_db()
    total_users = db.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    total_votes = db.execute("SELECT COUNT(*) FROM votes").fetchone()[0]
    data = db.execute("SELECT candidate, COUNT(*) FROM votes GROUP BY candidate").fetchall()
    
    settings = db.execute("SELECT value FROM settings WHERE key='resultsDeclared'").fetchone()
    declared = settings and settings[0] == 'true'
    candidates = db.execute("SELECT id, name, party, image_url FROM candidates").fetchall()
    db.close()
    
    return render_template("admin.html", total_users=total_users, total_votes=total_votes, data=data, declared=declared, candidates=candidates)

@app.route("/admin/toggle_results", methods=["POST"])
def toggle_results():
    if not session.get("admin"):
        return redirect("/admin_login")
        
    db = get_db()
    settings = db.execute("SELECT value FROM settings WHERE key='resultsDeclared'").fetchone()
    new_val = 'false' if settings and settings[0] == 'true' else 'true'
    
    db.execute("UPDATE settings SET value=? WHERE key='resultsDeclared'", (new_val,))
    db.commit()
    db.close()
    return redirect("/admin")

@app.route("/admin/reset_votes", methods=["POST"])
def reset_votes():
    if not session.get("admin"):
        return redirect("/admin_login")
        
    db = get_db()
    db.execute("DELETE FROM votes")
    db.commit()
    db.close()
    return redirect("/admin?success=reset")

@app.route("/admin/add_candidate", methods=["POST"])
def add_candidate():
    if not session.get("admin"):
        return redirect("/admin_login")
        
    name = request.form.get("name")
    party = request.form.get("party")
    image_url = request.form.get("image_url")
    if not image_url:
        image_url = "/static/modi.jpg"
        
    db = get_db()
    db.execute("INSERT INTO candidates (name, party, image_url) VALUES (?, ?, ?)", (name, party, image_url))
    db.commit()
    db.close()
    return redirect("/admin?success=candidate_added")

@app.route("/admin/delete_candidate", methods=["POST"])
def delete_candidate():
    if not session.get("admin"):
        return redirect("/admin_login")
        
    candidate_id = request.form.get("candidate_id")
    db = get_db()
    db.execute("DELETE FROM candidates WHERE id=?", (candidate_id,))
    db.commit()
    db.close()
    return redirect("/admin?success=candidate_deleted")

@app.route("/logout")
def logout():
    session.pop("user", None)
    session.pop("admin", None)
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
