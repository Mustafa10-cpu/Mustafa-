
from flask import Flask, request, redirect, url_for, session, flash, render_template_string
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "mustafa-football-secret-2026"

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mustafa_football.db")


# =============== VERİTABANI ===============

def connect():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con


def init_db():
    con = connect()
    con.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS players (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        position TEXT NOT NULL,
        number INTEGER NOT NULL
    );

    CREATE TABLE IF NOT EXISTS matches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        opponent TEXT NOT NULL,
        match_date TEXT NOT NULL,
        venue TEXT,
        score TEXT DEFAULT 'Henüz oynanmadı'
    );

    CREATE TABLE IF NOT EXISTS tactics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        formation TEXT NOT NULL,
        details TEXT
    );

    CREATE TABLE IF NOT EXISTS notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL
    );
    """)
    con.commit()
    con.close()


init_db()


# =============== KULLANICI İŞLEMLERİ ===============

def get_user():
    uid = session.get("user_id")
    if not uid:
        return None
    con = connect()
    user = con.execute(
        "SELECT * FROM users WHERE id=?", (uid,)
    ).fetchone()
    con.close()
    return user


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not get_user():
            return redirect(url_for("login"))
        return func(*args, **kwargs)
    return wrapper


def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user = get_user()
        if not user:
            return redirect(url_for("login"))
        if user["role"] != "admin":
            flash("Bu bölüm yalnızca yöneticilere açıktır.")
            return redirect(url_for("home"))
        return func(*args, **kwargs)
    return wrapper


# =============== TASARIM ===============

STYLE = """
<style>
*{box-sizing:border-box}
body{
 margin:0;color:white;font-family:Arial,sans-serif;
 background:radial-gradient(circle at top,#123d28,transparent 42%),
 linear-gradient(145deg,#020713,#07131c 65%,#020509);
 min-height:100vh
}
header{
 text-align:center;padding:24px 10px;
 background:linear-gradient(135deg,#071326,#020609);
 border-bottom:2px solid #20ed50
}
.logo{font-size:38px}
header h1{margin:7px;font-size:29px}
header h1 span{color:#22f34e}
header p{color:#b9c7d2;margin:5px}
nav{
 display:flex;flex-wrap:wrap;justify-content:center;
 gap:8px;padding:13px 7px;background:#07101b
}
nav a{
 color:white;text-decoration:none;background:#172536;
 padding:10px 12px;border-radius:12px;font-size:13px
}
nav a:hover{background:#087b35}
main{max-width:850px;margin:auto;padding:18px 14px 35px}
h2{color:#35ef65}
.welcome,.panel{
 background:linear-gradient(120deg,#10251d,#091321);
 border:1px solid #20e94c70;border-radius:18px;
 padding:19px;margin-bottom:17px
}
.grid{
 display:grid;grid-template-columns:repeat(2,minmax(0,1fr));
 gap:13px
}
.card{
 min-height:135px;padding:17px 10px;border-radius:18px;
 text-decoration:none;color:white;border:1px solid #ffffff35;
 display:flex;flex-direction:column;justify-content:center;
 align-items:center;text-align:center
}
.card .icon{font-size:36px;margin-bottom:8px}
.card h3{margin:3px 0;font-size:17px}
.card p{margin:5px 0;color:#d0d8e4;font-size:12px}
.green{background:linear-gradient(140deg,#087b27,#092519)}
.blue{background:linear-gradient(140deg,#0759bd,#101d3e)}
.purple{background:linear-gradient(140deg,#7900bb,#25103f)}
.orange{background:linear-gradient(140deg,#b95b00,#38200c)}
.red{background:linear-gradient(140deg,#bd001c,#3b0713)}
.gray{background:linear-gradient(140deg,#435b80,#101b2d)}
form,.item{
 background:#101d2b;border:1px solid #ffffff20;
 border-radius:14px;padding:15px;margin:12px 0
}
input,textarea,select{
 width:100%;padding:13px;margin:7px 0 12px;
 border-radius:9px;border:1px solid #405064;
 background:#07111d;color:white;font-size:15px
}
textarea{min-height:90px}
button,.button{
 display:inline-block;border:0;border-radius:10px;
 background:#13c947;color:#001b09;padding:12px 17px;
 font-weight:bold;text-decoration:none;cursor:pointer;margin:4px 2px
}
.delete{background:#d83b4b;color:white}
.notice{
 background:#243b29;border:1px solid #35ef65;
 border-radius:10px;padding:12px;margin:10px 0
}
small{color:#b9c7d2}
footer{text-align:center;padding:20px;color:#84939f;font-size:12px}
@media(max-width:350px){.grid{grid-template-columns:1fr}}
</style>
"""


def page(title, content):
    user = get_user()
    nav = ""
    if user:
        nav = """
        <nav>
        <a href="/">🏠 Ana Sayfa</a>
        <a href="/players">👥 Kadro</a>
        <a href="/matches">📅 Maçlar</a>
        <a href="/tactics">🧠 Taktikler</a>
        <a href="/notes">📢 Duyurular</a>
        """
        if user["role"] == "admin":
            nav += '<a href="/management">⚙️ Yönetim</a>'
        nav += '<a href="/logout">🚪 Çıkış</a></nav>'

    return render_template_string("""
    <!DOCTYPE html>
    <html lang="tr">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <title>{{title}} - Mustafa Football</title>
    """ + STYLE + """
    </head>
    <body>
    <header>
      <div class="logo">👑⚽</div>
      <h1>Mustafa <span>Football</span></h1>
      <p>Futbolun Kalbi Burada</p>
    </header>
    """ + nav + """
    <main>
    {% for msg in messages %}
      <div class="notice">{{msg}}</div>
    {% endfor %}
    """ + content + """
    </main>
    <footer>MUSTAFA FOOTBALL © 2026<br>Birlikte kazanırız! ⚽</footer>
    </body></html>
    """, title=title, messages=get_flashed_messages())


def get_flashed_messages():
    from flask import get_flashed_messages as messages
    return messages()


# =============== KURULUM ===============

@app.route("/ilk-kurulum", methods=["GET", "POST"])
def setup():
    con = connect()
    count = con.execute(
        "SELECT COUNT(*) FROM users WHERE role='admin'"
    ).fetchone()[0]

    if count:
        con.close()
        return page("Kurulum", """
        <div class="panel">
        <h2>Yönetici zaten oluşturulmuş.</h2>
        <a class="button" href="/login">Giriş Yap</a>
        </div>
        """)

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if len(username) < 3 or len(password) < 6:
            flash("Kullanıcı adı en az 3, şifre en az 6 karakter olmalı.")
        else:
            try:
                con.execute(
                    "INSERT INTO users(username,password,role) VALUES(?,?,?)",
                    (username, generate_password_hash(password), "admin")
                )
                con.commit()
                con.close()
                flash("Yönetici hesabı oluşturuldu.")
                return redirect("/login")
            except sqlite3.IntegrityError:
                flash("Bu kullanıcı adı zaten kullanılıyor.")

    con.close()
    return page("İlk Kurulum", """
    <div class="panel">
    <h2>👑 İlk Yönetici Hesabı</h2>
    <form method="post">
    Kullanıcı adı
    <input name="username" required minlength="3">
    Şifre
    <input name="password" type="password" required minlength="6">
    <button>Yönetici Oluştur</button>
    </form>
    </div>
    """)


# =============== GİRİŞ ===============

@app.route("/login", methods=["GET", "POST"])
def login():
    if get_user():
        return redirect("/")

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        con = connect()
        user = con.execute(
            "SELECT * FROM users WHERE username=?", (username,)
        ).fetchone()
        con.close()

        if user and check_password_hash(user["password"], password):
            session.clear()
            session["user_id"] = user["id"]
            return redirect("/")
        flash("Kullanıcı adı veya şifre hatalı.")

    return page("Giriş", """
    <div class="panel">
    <h2>⚽ Mustafa Football'a Giriş</h2>
    <form method="post">
    Kullanıcı adı
    <input name="username" required>
    Şifre
    <input name="password" type="password" required>
    <button>Giriş Yap</button>
    </form>
    <a class="button" href="/ilk-kurulum">İlk Yönetici Kurulumu</a>
    </div>
    """)


@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect("/login")


# =============== ANA SAYFA ===============

@app.route("/")
@login_required
def home():
    user = get_user()
    management = ""
    if user["role"] == "admin":
        management = """
        <a class="card gray" href="/management">
        <div class="icon">⚙️</div>
        <h3>Yönetim Paneli</h3>
        <p>Takımını yönet</p></a>
        """

    return page("Ana Sayfa", """
    <section class="welcome">
    <h2>Merhaba {{username}}! 👋</h2>
    <p>Mustafa Football'a hoş geldin. Takımını yönetmeye hazır mısın?</p>
    </section>
    <section class="grid">
    <a class="card green" href="/"><div class="icon">🏠</div>
    <h3>Ana Sayfa</h3><p>Takımının son durumunu gör</p></a>

    <a class="card blue" href="/players"><div class="icon">👥</div>
    <h3>Kadro</h3><p>Oyuncuları görüntüle</p></a>

    <a class="card purple" href="/matches"><div class="icon">📅</div>
    <h3>Maçlar</h3><p>Maç programını takip et</p></a>

    <a class="card orange" href="/tactics"><div class="icon">🧠</div>
    <h3>Taktikler</h3><p>Takım taktiklerini incele</p></a>

    <a class="card red" href="/notes"><div class="icon">📢</div>
    <h3>Duyurular</h3><p>Takım duyurularını gör</p></a>
    """ + management + """
    </section>
    """.replace("{{username}}", user["username"]))


# =============== KADRO ===============

@app.route("/players", methods=["GET", "POST"])
@login_required
def players():
    user = get_user()
    con = connect()

    if request.method == "POST" and user["role"] == "admin":
        name = request.form.get("name", "").strip()
        position = request.form.get("position", "").strip()
        number = request.form.get("number", "").strip()

        if name and position and number.isdigit():
            con.execute(
                "INSERT INTO players(name,position,number) VALUES(?,?,?)",
                (name, position, int(number))
            )
            con.commit()
            flash("Oyuncu eklendi.")
        else:
            flash("Oyuncu bilgilerini kontrol et.")

    rows = con.execute("SELECT * FROM players ORDER BY number").fetchall()
    con.close()

    form = ""
    if user["role"] == "admin":
        form = """
        <form method="post">
        <h3>➕ Oyuncu Ekle</h3>
        İsim<input name="name" required>
        Mevki<input name="position" placeholder="Kaleci, Defans..." required>
        Forma numarası<input name="number" type="number" required>
        <button>Oyuncu Ekle</button>
        </form>
        """

    items = "".join(
        f'<div class="item">👕 <b>#{r["number"]} {r["name"]}</b><br><small>{r["position"]}</small></div>'
        for r in rows
    ) or "<p>Henüz oyuncu eklenmedi.</p>"

    return page("Kadro", "<h2>👥 Takım Kadrosu</h2>" + form + items)


# =============== MAÇLAR ===============

@app.route("/matches", methods=["GET", "POST"])
@login_required
def matches():
    user = get_user()
    con = connect()

    if request.method == "POST" and user["role"] == "admin":
        opponent = request.form.get("opponent", "").strip()
        date = request.form.get("date", "").strip()
        venue = request.form.get("venue", "").strip()

        if opponent and date:
            con.execute(
                "INSERT INTO matches(opponent,match_date,venue) VALUES(?,?,?)",
                (opponent, date, venue)
            )
            con.commit()
            flash("Maç eklendi.")

    if request.method == "POST" and user["role"] == "admin" and request.form.get("score_id"):
        con.execute(
            "UPDATE matches SET score=? WHERE id=?",
            (request.form.get("score", ""), request.form.get("score_id"))
        )
        con.commit()
        flash("Maç sonucu güncellendi.")

    rows = con.execute(
        "SELECT * FROM matches ORDER BY match_date"
    ).fetchall()
    con.close()

    form = ""
    if user["role"] == "admin":
        form = """
        <form method="post">
        <h3>➕ Maç Ekle</h3>
        Rakip takım<input name="opponent" required>
        Tarih ve saat<input name="date" placeholder="22.11.2026 18:00" required>
        Saha<input name="venue">
        <button>Maç Ekle</button>
        </form>
        """

    items = ""
    for r in rows:
        items += f"""
        <div class="item">
        <h3>⚽ Mustafa FC - {r['opponent']}</h3>
        📅 {r['match_date']}<br>
        🏟️ {r['venue'] or 'Belirtilmedi'}<br>
        <b>Skor: {r['score']}</b>
        """
        if user["role"] == "admin":
            items += f"""
            <form method="post">
            <input type="hidden" name="score_id" value="{r['id']}">
            Yeni skor<input name="score" placeholder="2-1" required>
            <button>Skoru Güncelle</button>
            </form>
            """
        items += "</div>"

    return page("Maçlar", "<h2>📅 Maç Takvimi</h2>" + form + (items or "<p>Henüz maç yok.</p>"))


# =============== TAKTİKLER ===============

@app.route("/tactics", methods=["GET", "POST"])
@login_required
def tactics():
    user = get_user()
    con = connect()

    if request.method == "POST" and user["role"] == "admin":
        title = request.form.get("title", "").strip()
        formation = request.form.get("formation", "").strip()
        details = request.form.get("details", "").strip()

        if title and formation:
            con.execute(
                "INSERT INTO tactics(title,formation,details) VALUES(?,?,?)",
                (title, formation, details)
            )
            con.commit()
            flash("Taktik eklendi.")

    rows = con.execute("SELECT * FROM tactics ORDER BY id DESC").fetchall()
    con.close()

    form = ""
    if user["role"] == "admin":
        form = """
        <form method="post">
        <h3>➕ Taktik Ekle</h3>
        Taktik adı<input name="title" required>
        Diziliş<input name="formation" placeholder="4-3-3" required>
        Açıklama<textarea name="details"></textarea>
        <button>Taktik Ekle</button>
        </form>
        """

    items = "".join(
        f'<div class="item"><h3>🧠 {r["title"]}</h3><b>Diziliş: {r["formation"]}</b><p>{r["details"]}</p></div>'
        for r in rows
    ) or "<p>Henüz taktik yok.</p>"

    return page("Taktikler", "<h2>🧠 Takım Taktikleri</h2>" + form + items)


# =============== DUYURULAR ===============

@app.route("/notes", methods=["GET", "POST"])
@login_required
def notes():
    user = get_user()
    con = connect()

    if request.method == "POST" and user["role"] == "admin":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()

        if title and content:
            con.execute(
                "INSERT INTO notes(title,content) VALUES(?,?)",
                (title, content)
            )
            con.commit()
            flash("Duyuru yayınlandı.")

    rows = con.execute("SELECT * FROM notes ORDER BY id DESC").fetchall()
    con.close()

    form = ""
    if user["role"] == "admin":
        form = """
        <form method="post">
        <h3>➕ Duyuru Yayınla</h3>
        Başlık<input name="title" required>
        Mesaj<textarea name="content" required></textarea>
        <button>Yayınla</button>
        </form>
        """

    items = "".join(
        f'<div class="item"><h3>📢 {r["title"]}</h3><p>{r["content"]}</p></div>'
        for r in rows
    ) or "<p>Henüz duyuru yok.</p>"

    return page("Duyurular", "<h2>📢 Takım Duyuruları</h2>" + form + items)


# =============== YÖNETİM PANELİ ===============

@app.route("/management", methods=["GET", "POST"])
@admin_required
def management():
    con = connect()

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        role = request.form.get("role", "player")

        total = con.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        admins = con.execute(
            "SELECT COUNT(*) FROM users WHERE role='admin'"
        ).fetchone()[0]

        if total >= 10:
            flash("En fazla 10 kullanıcı oluşturulabilir.")
        elif role not in ("admin", "player"):
            flash("Geçersiz kullanıcı türü.")
        elif role == "admin" and admins >= 2:
            flash("En fazla 2 yönetici olabilir.")
        elif len(username) < 3 or len(password) < 6:
            flash("Kullanıcı adı en az 3, şifre en az 6 karakter olmalı.")
        else:
            try:
                con.execute(
                    "INSERT INTO users(username,password,role) VALUES(?,?,?)",
                    (username, generate_password_hash(password), role)
                )
                con.commit()
                flash("Kullanıcı oluşturuldu.")
            except sqlite3.IntegrityError:
                flash("Bu kullanıcı adı zaten kullanılıyor.")

    users = con.execute(
        "SELECT id,username,role FROM users ORDER BY id"
    ).fetchall()
    con.close()

    items = "".join(
        f'<div class="item">👤 <b>{u["username"]}</b> — {u["role"]}</div>'
        for u in users
    )

    return page("Yönetim", """
    <h2>⚙️ Yönetim Paneli</h2>
    <div class="panel">
    <h3>Yeni Kullanıcı Oluştur</h3>
    <form method="post">
    Kullanıcı adı<input name="username" required minlength="3">
    Şifre<input name="password" type="password" required minlength="6">
    Kullanıcı türü
    <select name="role">
      <option value="player">Oyuncu</option>
      <option value="admin">Yönetici</option>
    </select>
    <button>Hesap Oluştur</button>
    </form>
    </div>
    <h3>Mevcut Kullanıcılar</h3>
    """ + items)


# =============== ÇALIŞTIR ===============

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
