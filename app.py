from datetime import datetime, date
from smtplib import SMTP
# *Lines 4-38 from distribution code (Harvard's CS50)*
import os
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required, lookup, usd


# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


# Using my personal key if it's needed to set api key
if not os.environ.get("API_KEY"):
    os.environ["API_KEY"] = os.getenv('API_KEY')

# Gets day and time
def day_time():
    '''Returns perfectly formated day and time'''

    day = date.today().strftime("%b-%d-%Y")
    time = datetime.now().strftime("%H:%M:%S")
    return f"{day} {time}"

# Validates password strength
"""
def strong_enough(password):
    '''Checks if the password has any number, any letter, any especial character and if it's long enough (8 digits)'''
    special_char = "!@#$%^&*()-+?_=,<>/'}\|""=[]{`´"

    if any(char.isdigit() for char in password) and any(char.isalpha() for char in password) and any(char in special_char for char in password) and len(password) >= 8:
        return True
    else:
        return False
"""


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    user_id = session.get('user_id')
    table_name = f'stocks_user{user_id}'
    db.execute("CREATE TABLE IF NOT EXISTS ? (stock_symbol TEXT NOT NULL, shares NUMBER NOT NULL, price NUMBER NOT NULL, time TEXT NOT NULL)", table_name)
    money = db.execute("SELECT dinheiro FROM users WHERE id = ?", user_id)[0]['dinheiro']
    total_value_in_stocks = 0

    rows = db.execute('SELECT DISTINCT stock_symbol FROM ? WHERE NOT stock_symbol="DINHEIRO" GROUP BY stock_symbol HAVING SUM(shares) >= 1', table_name)
    for row in rows:
        row["company_name"] = lookup(row["stock_symbol"])['name']
        row["price_stock"] = lookup(row["stock_symbol"])['price']
        row["shares"] = db.execute("SELECT SUM(shares) FROM ? WHERE stock_symbol = ?", table_name, row["stock_symbol"])[0]["SUM(shares)"]
        total_value_in_stocks += row["shares"] * row["price_stock"]

    portfolio_value = total_value_in_stocks + money

    return render_template('index.html', rows=rows, money=money, portfolio_value=portfolio_value)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    if request.method == 'GET':
        return render_template('buy.html')

    elif request.method == 'POST':
        try:
            shares = int(request.form.get('shares'))
        except:
            return apology('Quantidade de ações não inteira')

        if shares < 0:
            return apology('Quantidade de ações não positiva')
        elif not lookup(request.form.get('symbol')):
            return apology('Código de ação inválido')

        stock_symbol = request.form.get('symbol')
        price = lookup(stock_symbol)['price']
        total_purchase_cost = round((price * shares), 2)
        user_id = session.get('user_id')
        user_money = db.execute('SELECT dinheiro FROM users WHERE id = ?', user_id)[0]['dinheiro']

        if total_purchase_cost > user_money:
            return apology("Dinheiro insuficiente")

        table_name = f'stocks_user{user_id}'
        db.execute("CREATE TABLE IF NOT EXISTS ? (stock_symbol TEXT NOT NULL, shares NUMBER NOT NULL, price NUMBER NOT NULL, time TEXT NOT NULL)", table_name)
        db.execute("INSERT INTO ? (stock_symbol, shares, price, time) VALUES(?, ?, ?, ?)", table_name, stock_symbol, shares, price, day_time())
        db.execute("UPDATE users SET dinheiro = ? WHERE id = ?", (user_money - total_purchase_cost), user_id)

        return redirect('/')


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    user_id = session.get('user_id')
    table_name = f'stocks_user{user_id}'
    rows = db.execute("SELECT * FROM ?", table_name)

    return render_template('history.html', rows=rows)


# *Lines 138-183 from distribution code (Harvard's CS50)*
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure email was submitted
        if not request.form.get("email"):
            return apology("Nenhum e-mail digitado")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("Nenhuma senha digitada")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE email = ?", request.form.get("email"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("Crie uma conta antes!")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        flash('Você entrou com sucesso!')
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    if request.method == "GET":
        return render_template('quote.html')

    elif request.method == "POST":
        stock_symbol = request.form.get('symbol').strip().upper()
        quoted_dict = lookup(stock_symbol)

        if quoted_dict == None:
            return apology('Código de ação inválido')

        else:
            stock = quoted_dict['name']
            symbol = quoted_dict['symbol']
            price = quoted_dict['price']
            quoted_text = f"Uma ação da {stock} ({symbol}) custa"

        return render_template('quoted.html', quoted_text=quoted_text, price=price)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "GET":
        return render_template('register.html')

    elif request.method == "POST":
        all_emails = []
        for row in db.execute('SELECT email FROM users'):
            all_emails.append(row["email"])

        if not request.form.get('username'):
            return apology('Nenhum nome digitado')

        elif not request.form.get('email'):
            return apology('Você não tem e-mail?')

        elif request.form.get('email') in all_emails:
            return apology('E-mail já cadastrado')

        elif not request.form.get('password') or not request.form.get('confirmation'):
            return apology('Digite a senha duas vezes')

        elif request.form.get('password') != request.form.get('confirmation'):
            return apology('As senhas digitadas não correspondem')

        # elif not strong_enough(request.form.get('password')):
            # return apology('Senha curta demais ou sem número/letra/símbolo')

        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        db.execute("INSERT INTO users (username, email, hash) VALUES(?, ?, ?)", username, email, generate_password_hash(password))

        session["user_id"] = db.execute('SELECT id FROM users WHERE username = ?', username)[0]["id"]

        
        texto = f"Parabéns! Você foi registrado com sucesso, {username}!"
        assunto = "Registrado"
        msg_email = (f"Subject: {assunto}\n\n{texto}")
        
        EMAIL_REMETENTE = os.getenv('EMAIL_REMETENTE')
        EMAIL_SENHA = os.getenv('EMAIL_SENHA')

        servidor = SMTP("smtp.gmail.com", 587)
        servidor.starttls()
        servidor.login(EMAIL_REMETENTE, EMAIL_SENHA)
        servidor.sendmail(EMAIL_REMETENTE, email, msg_email.encode("utf8"))

        flash('Você foi cadastrado com sucesso!')

        return redirect('/')


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    if request.method == "GET":
        symbols = []
        table_name = f"stocks_user{session.get('user_id')}"
        rows = db.execute('SELECT DISTINCT stock_symbol FROM ? WHERE NOT stock_symbol="DINHEIRO" GROUP BY stock_symbol HAVING SUM(shares) >= 1', table_name)
        for row in rows:
            symbols.append(row["stock_symbol"])

        return render_template('sell.html', symbols=symbols)

    elif request.method == "POST":
        symbols = []
        table_name = f"stocks_user{session.get('user_id')}"
        rows = db.execute('SELECT DISTINCT stock_symbol FROM ? WHERE NOT stock_symbol="DINHEIRO" GROUP BY stock_symbol HAVING SUM(shares) >= 1', table_name)
        for row in rows:
            symbols.append(row["stock_symbol"])

        if request.form.get("symbol") not in symbols:
            return apology("Código de ação inválido")

        shares = db.execute("SELECT SUM(shares) FROM ? WHERE stock_symbol = ?", table_name, request.form.get("symbol"))[0]["SUM(shares)"]

        if not request.form.get("shares"):
            return apology("Digite a quantidade de ações")

        elif int(request.form.get("shares")) > shares:
            return apology("Você não tem tantas ações")

        elif int(request.form.get("shares")) <= 0:
            return apology("Quantidade de ações não positiva")

        else:
            current_price = lookup(request.form.get("symbol"))['price']
            money_received = current_price * int(request.form.get("shares"))
            db.execute("INSERT INTO ? (stock_symbol, shares, price, time) VALUES(?, ?, ?, ?)", table_name, request.form.get("symbol"), -(int(request.form.get("shares"))), current_price, day_time())
            db.execute("UPDATE users SET dinheiro = dinheiro + ? WHERE id = ?", money_received, session.get("user_id"))

        return redirect('/')


@app.route("/add_money", methods=["GET", "POST"])
@login_required
def add_money():
    """Add some money"""

    if request.method == "GET":
        return render_template('add_money.html')

    elif request.method == "POST":
        current_money = float(db.execute('SELECT dinheiro FROM users WHERE id = ?', session.get('user_id'))[0]['dinheiro'])
        added_money = float(request.form.get('money'))
        new_money = current_money + added_money

        user_id = session.get("user_id")
        table_name = f'stocks_user{user_id}'

        db.execute('UPDATE users SET dinheiro = ? WHERE id = ?', new_money, session.get('user_id'))
        db.execute("INSERT INTO ? (stock_symbol, shares, price, time) VALUES(?, ?, ?, ?)", table_name, "DINHEIRO", 1, added_money, day_time())

        return redirect('/')


@app.route("/remove_money", methods=["GET", "POST"])
@login_required
def remove_money():
    """Remove some money"""

    if request.method == "GET":
        return render_template('remove_money.html')

    elif request.method == "POST":
        current_money = float(db.execute('SELECT dinheiro FROM users WHERE id = ?', session.get('user_id'))[0]['dinheiro'])
        removed_money = float(request.form.get('money'))
        new_money = current_money - removed_money

        user_id = session.get("user_id")
        table_name = f'stocks_user{user_id}'

        db.execute('UPDATE users SET dinheiro = ? WHERE id = ?', new_money, session.get('user_id'))
        db.execute("INSERT INTO ? (stock_symbol, shares, price, time) VALUES(?, ?, ?, ?)", table_name, "DINHEIRO", -1, removed_money, day_time())

        return redirect('/')


# *Lines 354-363 from distribution code (Harvard's CS50)*
def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
