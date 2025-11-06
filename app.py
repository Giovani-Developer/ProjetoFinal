from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime
from extensions import db
from models import Expense, User




app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'segredo'

# Inicializa o banco com o app
db.init_app(app)

# Cria o banco se não existir
with app.app_context():
    db.create_all()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash('Usuário já existe!', 'danger')
            return redirect(url_for('login'))

        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Conta criada com sucesso! Faça login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Usuário ou senha inválidos.', 'danger')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você saiu da sua conta.', 'info')
    return redirect(url_for('login'))



@app.route('/')
@login_required
def index():
    expenses = Expense.query.order_by(Expense.date.desc()).all()
    total = sum(expense.value for expense in expenses)

    categories = []
    totals = []

    for expense in expenses:
        if expense.category not in categories:
            categories.append(expense.category)
            totals.append(expense.value)
        else:
            i = categories.index(expense.category)
            totals[i] += expense.value 

    return render_template('index.html', expenses=expenses, total=total, categories=categories, totals=totals)

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        description = request.form['description']
        value = float(request.form['value'])
        category = request.form['category']
        date = datetime.strptime(request.form['date'], '%Y-%m-%d')
        new_expense = Expense(description=description, value=value, category=category, date=date)
        try:
            new_expense.validate()
            db.session.add(new_expense)
            db.session.commit()
            flash('Despesa adicionada com sucesso!', 'success')
        except ValueError as e:
            flash(str(e), 'danger')
          
        return redirect(url_for('add'))
    return render_template('add.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    expense = Expense.query.get_or_404(id)
    if request.method == 'POST':
        expense.description = request.form['description']
        expense.value = float(request.form['value'])
        expense.category = request.form['category']
        expense.date = datetime.strptime(request.form['date'], '%Y-%m-%d')
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit.html', expense=expense)

@app.route('/delete/<int:id>')
@login_required
def delete(id):
    expense = Expense.query.get_or_404(id)
    db.session.delete(expense)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/filter')
@login_required
def filter():
    category = request.args.get('category')
    expenses = Expense.query.filter_by(category=category).all()
    return render_template("index.html", expenses=expenses)

if __name__ == '__main__':
    app.run(debug=True)
