import os
import redis
import time

from flask import Flask
from flask import jsonify
from flask import request

app = Flask(__name__)
app.secret_key = b'OL!qJmKmF%nCeGyt'

redis_host = os.environ.get('REDIS', 'localhost')
pool = redis.ConnectionPool(
    host=redis_host, port=6379, db=0, decode_responses=True)
red = redis.Redis(connection_pool=pool)


@app.route('/')
@app.route('/api')
def api():
    response = {'message': 'Success'}
    return jsonify(response), 200


@app.route('/api/auth', methods=['POST'])
def auth():
    """ Verify if the user exists or not
    if username and password matches, return user id
    """
    data = request.get_json()
    print(list(data.keys()))

    username = data['username']
    print(username)
    password = data['password']
    print(password)

    if red.sismember("users", username):
        user = red.hgetall(f"user:{username}")

        if password == user['password']:
            # user_id = user['user_id']
            profile = red.hgetall(f"profile:{user['user_id']}")

            response = {'message': 'Success', 'data': profile}
            return jsonify(response), 200
    else:

        response = {'message': 'Invalid username or password'}
        return jsonify(response), 400


@app.route('/api/user', methods=['POST'])
def create_user():
    """ Create User and user profile """
    data = request.get_json()

    print(list(data.keys()))

    username = data['username']
    print(username)
    password = data['password']
    print(password)

    if red.sismember("users", username):
        response = {
            'message': 'Username is already taken, please choose a different one.'}

        return jsonify(response), 400
    else:
        user_id = red.incr("userid")
        pipe = red.pipeline()
        print(f"userid : {user_id}")
        pipe.sadd("users", username)
        pipe.hset(f"user:{username}", "user_id", user_id)
        pipe.hset(f"user:{username}", "password", password)

        # pipe.hset(f"profile:{user_id}", "nickname", nickname)
        pipe.hset(f"profile:{user_id}", "user_id", user_id)
        pipe.hset(f"profile:{user_id}", "follower", 0)
        pipe.hset(f"profile:{user_id}", "following", 0)
        pipe.hset(f"profile:{user_id}", "post", 0)
        pipe.hset(f"profile:{user_id}", "creation_dt", time.time())

        pipe.execute()

        response = {'message': 'Success'}
        return jsonify(response), 201


@app.route('/api/user/<_id>', methods=['GET'])
def get_profile_by_id(_id):
    """Get a user profile based on provided id"""
    profile = red.hgetall(f"profile:{_id}")
    response = {'message': 'Success', 'data': profile}
    return jsonify(response), 200


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8081)
