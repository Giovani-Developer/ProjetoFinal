from extensions import db

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(10), nullable=True)
    value = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    date = db.Column(db.Date, nullable=False)

    def __repr__(self):
        return f'<Expense {self.description}>'

    def validate(self):
        if len(self.description ) > 25:
            raise ValueError ("A descrição não pode ter mais do que 25 caracteres.")