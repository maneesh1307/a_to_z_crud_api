from flask import Flask, json, request
from pymongo import MongoClient
from bson import ObjectId,json_util
app = Flask(__name__)

client = MongoClient('localhost:27017')
db = client['maneesh_backend_services']
collection = db['user_info']

@app.route('/healthcheck', methods=['POST'])
def healthcheck():
    try:
        return 'success'
    except Exception as e:
        return {'status': False, 'error_description': str(e), 'statusCode': 500}, 500

@app.route('/user-list', methods=['GET'])
def user_list():
    try:
        users = list(collection.find())
        for user in users:
            user['_id'] = str(user['_id'])
        return {'status': True, 'response': users, 'statusCode': 200}, 200
    except Exception as e:
        return {'status': False, 'error_description': str(e), 'statusCode': 500}, 500

@app.route('/single_user', methods=['POST'])
def single_user():
    try:
        user_id = request.values.get('user_id')
        print(user_id,'kkkkkkk')
        
        if not user_id:
            return {'status': False, 'error_description': "Missing user_id parameter", 'statusCode': 400}, 400
        
        db_user = collection.find_one({"_id": ObjectId(user_id)})
        if db_user:
            response = {'status': True, 'response': json.loads(json_util.dumps(db_user)), 'statusCode': 200}
            return response, 200
        else:
            return {'status': False, 'error_description': "User not found for this user_id", 'statusCode': 404}, 404
    except Exception as e:
        return {'status': False, 'error_description': str(e), 'statusCode': 500}, 500


@app.route('/delete-user', methods=['DELETE'])
def user_delete():
    try:
        user_id = request.values.get('user_id')
        db_user = collection.find_one({'_id': ObjectId(user_id)})
        if db_user:
            deleted_user = collection.delete_one({'_id': ObjectId(user_id)})
            return {'status': True, 'response': user_id, 'statusCode': 200}, 200
        else:
            return {'status': False, 'error_description': "User not found for this user_id", 'statusCode': 400}, 400
    except Exception as e:
        return {'status': False, 'error_description': str(e), 'statusCode': 500}, 500



@app.route('/create-user', methods=['POST'])
def create_user():
    try:
        username = request.values.get('username')
        existing_user = collection.find_one({'username': username})
        if existing_user:
            return {'status': False, 'error_description': 'User with the same username already exists', 'statusCode': 400}, 400
        
        user_data = {
            'username': username,
            'password': request.values.get('password'),
            'mobile': request.values.get('mobile'),
            'address': request.values.get('address'),
            'email': request.values.get('email')
        }
        inserted_data = collection.insert_one(user_data)
        if inserted_data:
            return {'status': True,'inserted_id':str(inserted_data.inserted_id), 'response': 'User created successfully', 'statusCode': 200}, 200
        else:
            return {'status': False, 'error_description': "User creation failed", 'statusCode': 400}, 400
    except Exception as e:
        return {'status': False, 'error_description': str(e), 'statusCode': 500}, 500



@app.route('/update-user', methods=['POST'])
def update_user():
    try:
        user_id = request.values.get('user_id')
        updated_data = {
            'username': request.values.get('username'),
            'password': request.values.get('password'),
            'mobile': request.values.get('mobile'),
            'address': request.values.get('address'),
            'email': request.values.get('email')
        }
        db_user = collection.find_one({'_id': ObjectId(user_id)})
        if db_user:
            updated_user = collection.update_one({'_id': ObjectId(user_id)}, {'$set': updated_data})
            if updated_user.modified_count > 0:
                return {'status': True, 'response': 'User updated successfully', 'statusCode': 200}, 200
            else:
                return {'status': False, 'error_description': 'Failed to update user', 'statusCode': 400}, 400
        else:
            return {'status': False, 'error_description': 'User not found for this user_id', 'statusCode': 400}, 400
    except Exception as e:
        return {'status': False, 'error_description': str(e), 'statusCode': 500}, 500

if __name__ == '__main__':
    app.run(debug=True)
