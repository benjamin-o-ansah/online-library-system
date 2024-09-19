from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models import Books,BorrowedBook
from datetime import datetime, timedelta

bp = Blueprint('books', __name__, url_prefix='/books')

@bp.route('/', methods=['GET'])
@jwt_required()
def get_books():
    try:
        books = Books.query.all()
        books_list = [{'id': book.id, 'title': book.title, 'author': book.author, 'genre':book.genre,'isbn': book.isbn, 'is_available': book.is_available} for book in books]
        return jsonify(books_list), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "An error occurred while getting books", "error": str(e)}), 500
    except KeyError:
        return jsonify({"msg": "Missing or invalid data"}), 400
    
    
@bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_book(id):
    try:
        book = Books.query.get(id)
        if not book:
            return jsonify({'message': 'Book not found'}), 404
        return jsonify({'id': book.id, 'title': book.title, 'genre':book.genre,'author': book.author, 'isbn': book.isbn, 'is_available': book.is_available}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "An error occurred while getting book", "error": str(e)}), 500
    except KeyError:
        return jsonify({"msg": "Missing or invalid data"}), 400
    
    

@bp.route('/', methods=['POST'])
@jwt_required()
def add_book():
    try:
        data = request.get_json()
        new_book = Books(
        title=data['title'],
        author=data['author'],
        genre=data['genre'],
        isbn=data['isbn'],
        is_available=True
    )
        db.session.add(new_book)
        db.session.commit()
        return jsonify({'message': 'Book added successfully!'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "An error occurred while adding book", "error": str(e)}), 500
    except KeyError:
        return jsonify({"msg": "Missing or invalid data"}), 400
    
    

@bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_book(id):
    try:
        book = Books.query.get(id)
        if not book:
            return jsonify({'message': 'Book not found'}), 404
        data = request.get_json()
        book.title = data.get('title', book.title)
        book.author = data.get('author', book.author)
        book.genre = data.get('genre', book.genre)
        book.isbn = data.get('isbn', book.isbn)
        db.session.commit()
        return jsonify({'message': 'Book updated successfully!'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "An error occurred while updating book", "error": str(e)}), 500
    except KeyError:
        return jsonify({"msg": "Missing or invalid data"}), 400
    
    
    
@bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_book(id):
    try:
        book = Books.query.get(id)
        if not book:
            return jsonify({'message': 'Book not found'}), 404
        db.session.delete(book)
        db.session.commit()
        return jsonify({'message': 'Book deleted successfully!'}), 200
    except KeyError:
        return jsonify({"msg": "Missing or invalid data"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "An error occurred while deleting book", "error": str(e)}), 500

@bp.route('/borrow', methods=['POST'])
@jwt_required()
def borrow_book():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        book_id = data.get('book_id')
        days_to_borrow = data.get('days', 14)  # Default borrowing period is 14 days

    # Check if book is available
        book = Books.query.get(book_id)
        if not book or not book.is_available:
            return jsonify({'error': 'Book is not available or does not exist.'}), 404

    # Calculate due date
        borrow_date = datetime.now()
        due_date = borrow_date + timedelta(days=days_to_borrow)

    # Create BorrowedBook entry
        borrowed_book = BorrowedBook(users_id=user_id, books_id=book_id, borrow_date=borrow_date, due_date=due_date)
        db.session.add(borrowed_book)

    # Update book availability
        book.is_available = False
        db.session.commit()

        return jsonify({'message': 'Book borrowed successfully!', 'due_date': due_date.strftime('%Y-%m-%d')}), 200

    except KeyError:
        return jsonify({"msg": "Missing or invalid data"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "An error occurred while making an attempt to borrow a book", "error": str(e)}), 500
    

@bp.route('/return', methods=['POST'])
@jwt_required()
def return_book():
    try:
        data = request.get_json()
        borrowed_book_id = data.get('borrowed_book_id')

    # Find the borrowed book record
        borrowed_book = BorrowedBook.query.get(borrowed_book_id)
        if not borrowed_book:
            return jsonify({'error': 'Borrowed book record not found.'}), 404

    # Update return date
        borrowed_book.return_date = datetime.now()
        borrowed_book.book.is_available = True  # Mark the book as available again
        db.session.commit()

        return jsonify({'message': 'Book returned successfully!'}), 200
    except KeyError:
        return jsonify({"msg": "Missing or invalid data"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "An error occurred while trying to return a book", "error": str(e)}), 500

@bp.route('/borrowed/<int:users_id>', methods=['GET'])
@jwt_required()
def list_borrowed_books(users_id):
    try:
        borrowed_books = BorrowedBook.query.filter_by(users_id=users_id, return_date=None).all()  # Only unreturned books
        borrowed_books_list = [
        {
            'book_id': borrowed.book_id,
            'title': borrowed.book.title,
            'borrow_date': borrowed.borrow_date.strftime('%Y-%m-%d'),
            'due_date': borrowed.due_date.strftime('%Y-%m-%d'),
        }
        for borrowed in borrowed_books
        ]
        return jsonify(borrowed_books_list), 200
    except KeyError:
        return jsonify({"msg": "Missing or invalid data"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "An error occurred while displaying borrowed books", "error": str(e)}), 500
    
@bp.route('/borrowed', methods=['GET'])
@jwt_required()
def get_borrowedBooks():
    try:
        borrowed_books = BorrowedBook.query.all()
        borrowedList = [{ 'id': borrowed.id, 'users_id': borrowed.users_id,'books_id':borrowed.books_id, 'borrowed_Date': borrowed.borrow_date, 'due_Date':borrowed.due_date,'return_Date': borrowed.return_date, } for borrowed in borrowed_books]
        return jsonify(borrowedList), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "An error occurred while getting borrowed books", "error": str(e)}), 500
    except KeyError:
        return jsonify({"msg": "Missing or invalid data"}), 400    

    
    
