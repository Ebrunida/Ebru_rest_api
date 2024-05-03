from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from pymongo import ReturnDocument
import requests

app = Flask(__name__)

# Connect to MongoDB
app.config["MONGO_URI"] = "mongodb://localhost:27017/ebruApiDB"
mongo = PyMongo(app)

@app.route('/student', methods=['POST'])
def create_student():
    data = request.get_json()

    # Validate the data request
    if not all(key in data for key in ("name", "surname", "stdNumber", "grades")):
        return jsonify({"error": "Missing required field"}), 400;

    if not all(isinstance(grade, dict) and 'code' in grade and 'value' in grade for grade in data['grades']):
        return jsonify({"error": "Invalid grades format"}), 400;

    # Calculate the average grade for each course
    course_codes = list(set([grade['code'] for grade in data['grades']]))
    average_grades = [sum([grade['value'] for grade in data['grades'] if grade['code'] == code]) / len([grade for grade in data['grades'] if grade['code'] == code]) for code in course_codes]

    # Calculate the overall average grade
    overall_average_grade = sum(average_grades) / len(average_grades)

    # Create the new student
    student = {
        "name": data['name'],
        "surname": data['surname'],
        "stdNumber": data['stdNumber'],
        "grades": data['grades'],
        "averageGrade": overall_average_grade
    }
    result = mongo.db.students.insert_one(student)

    return {"_id": str(result.inserted_id)}, 201

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404

def main():
    while True:
        print("\n1. Create a new student")
        print("2. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            name = input("Enter the student's name: ")
            surname = input("Enter the student's surname: ")
            stdNumber = input("Enter the student's standard number: ")
            grades = input("Enter the student's grades (format: code:value,code:value): ")

            # Parse the grades
            try:
                grades = [{'code': code, 'value': int(value)} for code, value in (grade.split(':') for grade in grades.split(','))]
            except ValueError:
                print("Invalid grades format. Please try again.")
                continue

            # Create the student
            student = {
                "name": name,
                "surname": surname,
                "stdNumber": stdNumber,
                "grades": grades
            }

            # Send a POST request to the /student endpoint
            response = requests.post("http://localhost:5000/student", json=student)

            if response.status_code == 201:
                print("Student created successfully.")
            else:
                if 'application/json' in response.headers.get('Content-Type', ''):
                    print(f"Failed to create student: {response.json()['error']}")
                else:
                    print(f"Failed to create student. Server responded with status code {response.status_code} and body: {response.text}")

        elif choice == '2':
            print("Exiting...")
            break

        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()