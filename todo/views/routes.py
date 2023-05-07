import json

from flask import Blueprint, jsonify
from flask import Blueprint, jsonify, request
from todo.models import db
from todo.models.todo import Todo
from todo.models.concerts import Concert
from todo.models.tickets import Ticket

from datetime import datetime

from todo.models.users import User
import uuid

api = Blueprint('api', __name__, url_prefix='/api/v1')

with open("users.json", "r") as f:
    users = json.load(f)

    
@api.route('/health')
def health():
    return jsonify({"status": "ok"})





# @api.route('/todos/<int:id>', methods=['GET'])
# def get_todo(todo_id):
#     todo = Todo.query.get(todo_id)
#     if todo is None:
#         return jsonify({'error': 'Todo not found'}), 404
#     return jsonify(todo.to_dict())


@api.route('/todos', methods=['POST'])
def create_todo():
    todo = Todo(
        title=request.json.get('title'),
        description=request.json.get('description'),
        completed=request.json.get('completed', False),
    )
    if 'deadline_at' in request.json:
        todo.deadline_at = datetime.fromisoformat(request.json.get('deadline_at'))
    # Adds a new record to the database or will update an existing record
    db.session.add(todo)
    # Commits the changes to the database, this must be called for the changes to be saved

    db.session.commit()
    return jsonify(todo.to_dict()), 201


# @api.route('/todos/<int:id>', methods=['PUT'])
# def update_todo(todo_id):
#     todo = Todo.query.get(todo_id)
#     if todo is None:
#         return jsonify({'error': 'Todo not found'}), 404
#     todo.title = request.json.get('title', todo.title)
#     todo.description = request.json.get('description', todo.description)
#     todo.completed = request.json.get('completed', todo.completed)
#     todo.deadline_at = request.json.get('deadline_at', todo.deadline_at)
#     db.session.commit()
#     return jsonify(todo.to_dict())


# @api.route('/todos/<int:id>', methods=['DELETE'])
# def delete_todo(todo_id):
#     todo = Todo.query.get(todo_id)
#     if todo is None:
#         return jsonify({}), 200
#     db.session.delete(todo)
#     db.session.commit()
#     return jsonify(todo.to_dict()), 200


@api.route('/concerts/health')
def concerts_health():
    return jsonify({"status": "ok"})



@api.route('/concerts', methods=['GET'])
def get_all_concerts():
    concerts = Concert.query.all()
    return jsonify([concert.to_dict() for concert in concerts])


@api.route('/concerts/<string:id>', methods=['GET'])
def get_concert(id):
    concert = Concert.query.filter_by(id=id).first()
    if concert:
        return jsonify(concert.to_dict())
    else:
        return jsonify({"error": "The concert does not exist."}), 404


@api.route('/concerts', methods=['POST'])
def register_concert():
    
    try:
        concert = Concert(
        id = str(uuid.uuid1()),
        name=request.json.get('name'),
        venue=request.json.get('venue'),
        date = request.json.get('date'),
        capacity=request.json.get('capacity'),
        status=request.json.get('status'),
        )

        # Validate capacity
        if not isinstance(concert.capacity, int) or concert.capacity <= 0 or concert.capacity > 150000:
            return jsonify({'error': 'Capacity must be an integer between 1 and 150000.'}), 400

        # Create new concert object
        # concert = Concert(name=name, venue=venue, date=date, capacity=capacity, status=status)

        # Add new concert to database
        db.session.add(concert)
        # Commits the changes to the database, this must be called for the changes to be saved

        db.session.commit()

        # Return success response
        return jsonify({'message': 'Concert registered successfully.'}), 201

    except Exception as e:
        # Return error response
        return jsonify({'error': str(e)}), 500




@api.route('/todos/<int:id>', methods=['PUT'])
def update_todo(todo_id):
    todo = Todo.query.get(todo_id)
    if todo is None:
        return jsonify({'error': 'Todo not found'}), 404
    todo.title = request.json.get('title', todo.title)
    todo.description = request.json.get('description', todo.description)
    todo.completed = request.json.get('completed', todo.completed)
    todo.deadline_at = request.json.get('deadline_at', todo.deadline_at)
    db.session.commit()
    return jsonify(todo.to_dict())

@api.route('/concerts/<string:id>', methods=['PUT'])
def update_concert(id):
    try:
        # Get concert from database
        concert = Concert.query.filter_by(id=id).first()

        # Check if concert exists
        if not concert:
            return jsonify({'error': 'Concert not found.'}), 404

        # Parse request body
        name = request.json.get('name', concert.name)
        venue = request.json.get('venue', concert.venue)
        date = request.json.get('date', concert.date)
        status = request.json.get('status', concert.status)

        # Validate status
        if not status or status not in ['ACTIVE', 'CANCELLED', 'SOLD_OUT']:
            return jsonify({'error': 'Invalid status.'}), 400

        # Update concert attributes
        concert.name = name
        concert.venue = venue
        concert.date = date
        concert.status = status
        # TODO
        # Remove existing tickets
        concert.tickets = []

        # Commit changes to database
        db.session.commit()

        # Return success response
        return jsonify({'message': 'Concert details updated successfully.'}), 200

    except Exception as e:
        # Return error response
        return jsonify({'error': str(e)}), 500


@api.route('/tickets', methods=['GET'])
def get_tickets():
    user_id = request.args.get('user_id')
    concert_id = request.args.get('concert_id')

    tickets = Ticket.query

    if user_id:
        tickets = tickets.filter_by(user_id=user_id)

    if concert_id:
        tickets = tickets.filter_by(concert_id=concert_id)

    tickets = tickets.all()

    if not tickets:
        return jsonify({'error': 'No tickets found matching the provided filters.'}), 404

    return jsonify({'tickets': [ticket.to_dict() for ticket in tickets]}), 200


@api.route('/tickets', methods=['POST'])
def purchase_ticket():
    try:
        data = request.get_json()
        id = str(uuid.uuid1())
        concert_id = data['concert_id']
        user_id = None

        # Check if the concert exists
        concert = Concert.query.get(concert_id)
        if concert is None:
            return jsonify({'error': 'Concert not found.'}), 400

        # Check if the user exists
        for user in users:
            if user["id"] == data['user_id']:
                user_id = data['user_id']
                break

        if user_id is None:
            return jsonify({'error': 'User not found.'}), 400

        # Check if there are available tickets
        if len(Ticket.query.filter_by(concert_id=concert_id, print_status='NOT_PRINTED').all()) >= concert.capacity:
            return jsonify({'error': 'No tickets available for this concert.'}), 422

        # Create a new ticket
        ticket = Ticket(ticket_id = id, concert_id=concert_id, user_id=user_id, print_status='NOT_PRINTED')
        db.session.add(ticket)
        db.session.commit()

        return jsonify(ticket.to_dict()), 201

    except KeyError:
        return jsonify({'error': 'Malformed or invalid request body.'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500




@api.route('/users/health')
def user_health():
    return jsonify({"status": "ok"})


@api.route("/users", methods=["GET"])
def get_users():
    # Return list of all users
    return jsonify(users), 200




@api.route("/users/<string:user_id>", methods=["GET"])
def get_user(user_id):
    # Find user with matching ID
    for user in users:
        if user["id"] == user_id:
            return jsonify(user)
    # If no matching user was found, return 404 error
    return jsonify({"error": "User not found"}), 404
