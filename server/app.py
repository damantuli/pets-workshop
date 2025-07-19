import os
from typing import Dict, List, Any, Optional
from flask import Flask, jsonify, Response, request
from models import init_db, db, Dog, Breed

# Get the server directory path
base_dir: str = os.path.abspath(os.path.dirname(__file__))

app: Flask = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(base_dir, "dogshelter.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database with the app
init_db(app)

@app.route('/api/dogs', methods=['GET'])
def get_dogs() -> Response:
    status_filter: Optional[str] = request.args.get('status')
    name_filter: Optional[str] = request.args.get('name')
    query = db.session.query(
        Dog.id, 
        Dog.name, 
        Breed.name.label('breed'),
        Dog.status
    ).join(Breed, Dog.breed_id == Breed.id)
    
    if status_filter == "available":
        query = query.filter(Dog.status == "AVAILABLE")  # If Enum, use .name

    if name_filter:
        query = query.filter(Dog.name.ilike(f"%{name_filter}%"))

    dogs_query = query.all()
    
    # Convert the result to a list of dictionaries
    dogs_list: List[Dict[str, Any]] = [
        {
            'id': dog.id,
            'name': dog.name,
            'breed': dog.breed
        }
        for dog in dogs_query
    ]
    
    return jsonify(dogs_list)

@app.route('/api/dogs/<int:id>', methods=['GET'])
def get_dog(id: int) -> tuple[Response, int] | Response:
    # Query the specific dog by ID and join with breed to get breed name
    dog_query = db.session.query(
        Dog.id,
        Dog.name,
        Breed.name.label('breed'),
        Dog.age,
        Dog.description,
        Dog.gender,
        Dog.status
    ).join(Breed, Dog.breed_id == Breed.id).filter(Dog.id == id).first()
    
    # Return 404 if dog not found
    if not dog_query:
        return jsonify({"error": "Dog not found"}), 404
    
    # Convert the result to a dictionary
    dog: Dict[str, Any] = {
        'id': dog_query.id,
        'name': dog_query.name,
        'breed': dog_query.breed,
        'age': dog_query.age,
        'description': dog_query.description,
        'gender': dog_query.gender,
        'status': dog_query.status.name
    }
    
    return jsonify(dog)

@app.route('/api/breeds', methods=['GET'])
def get_breeds() -> Response:
    breeds_query = db.session.query(Breed).all()
    breeds_list = [{'id': breed.id, 'name': breed.name} for breed in breeds_query]
    return jsonify(breeds_list)

def validate_dog_age(age: int) -> None:
    """
    Validates that the dog's age is between 0 and 20 (inclusive).

    Args:
        age (int): The age of the dog.

    Raises:
        ValueError: If age is not between 0 and 20.
    """
    if not (0 <= age <= 20):
        raise ValueError("Dog age must be between 0 and 20 (inclusive).")

if __name__ == '__main__':
    app.run(debug=True, port=5100) # Port 5100 to avoid macOS conflicts