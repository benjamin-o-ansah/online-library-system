from datetime import datetime
from app import db

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    borrowed_books = db.relationship('BorrowedBook', backref='users', lazy=True,overlaps="borrowed_book,users")
    
    def __repr__(self):
        return f'<User {self.username}>'

class Books(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    author = db.Column(db.String(120), nullable=False)
    genre = db.Column(db.String(80), nullable=True)
    isbn = db.Column(db.String(13), unique=True, nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    borrowed_books = db.relationship('BorrowedBook', backref='books', lazy=True,overlaps="borrowed_books,users")
    
    def __repr__(self):
        return f'<Book {self.title}>'
    

class BorrowedBook(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    users_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Foreign key to User
    books_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)  # Foreign key to Book
    borrow_date = db.Column(db.DateTime, default=datetime.timestamp, nullable=False)
    due_date = db.Column(db.DateTime, nullable=False)
    return_date = db.Column(db.DateTime, nullable=True)

    # Relationships
    user = db.relationship('Users', backref='borrowed_book', lazy=True,overlaps="borrowed_book,users")
    book = db.relationship('Books', backref='borrowed_book', lazy=True,overlaps="borrowed_book,users")
    
    
    def is_overdue(self):
        if self.return_date is None and datetime.now() > self.due_date:
            return True
        return False
    
    def calculate_fine(self, fine_per_day=1):
        if self.is_overdue():
            overdue_days = (datetime.now() - self.due_date).days
            return overdue_days * fine_per_day
        return 0

    def __repr__(self):
        return f'<BorrowedBook Users: {self.user_id} Books: {self.book_id}>'