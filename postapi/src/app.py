import os
import redis
import time

from flask import Flask
from flask import jsonify
from flask import request

app = Flask(__name__)
app.secret_key = b'ZhX9r^c$dUps6jlI'

redis_host = os.environ.get('REDIS', 'localhost')
pool = redis.ConnectionPool(
    host=redis_host, port=6379, db=1, decode_responses=True)
red = redis.Redis(connection_pool=pool)

ITEM_PER_PAGE = 6


@app.route('/')
@app.route('/api')
def api():
    response = {'message': 'Success'}
    return jsonify(response), 200


@app.route('/api/posts', methods=['GET'])
def get_posts():
    """Return all the latest posts"""

    page = request.args.get("page")
    # page = request.args.get("numperpage")

    if page:
        print('page is ', page)
        postlist = red.zrevrange(
            'postlist', 0 + ITEM_PER_PAGE * (int(page) - 1), 0 + ITEM_PER_PAGE * int(page) - 1)
    else:

        postlist = red.zrevrange('postlist', 0, ITEM_PER_PAGE - 1)
    print(postlist)

    posts = []

    for post_id in postlist:
        post = red.hgetall(f'post:{post_id}')
        print(post)
        posts.append(post)

    response = {'message': 'Success', 'data': posts}
    return jsonify(response), 200


@app.route('/api/posts/<post_id>', methods=['GET'])
def get_post_by_id(post_id):
    """Get post details and all the related comments by post id"""
    post = red.hgetall(f'post:{post_id}')
    print(post)

    commentids = red.zrevrange(f'comments:{post_id}', 0, -1)
    comments = []
    for comment_id in commentids:
        comments.append(red.hgetall(f'comment:{comment_id}'))

    data = {'post': post, 'comments': comments}

    response = {'message': 'Success', 'data': data}
    return jsonify(response), 200



@app.route('/api/posts/<post_id>/comments', methods=['POST'])
def create_comment(post_id):

    print(post_id)

    data = request.get_json()

    print(list(data.keys()))

    user_id = data['user_id']
    print(user_id)

    # print('Post>>>>')
    # post_id = data['post_id']
    # print(post_id)
    username = data['username']
    print(username)
    message = data['message']
    print(message)
    # creation_dt = data['creation_dt']
    # print(creation_dt)

    creation_dt = time.time()
    comment_id = red.incr('commentid')

    pipe = red.pipeline()
    pipe.hset(f'comment:{comment_id}', 'comments', comment_id)
    pipe.hset(f'comment:{comment_id}', 'post_id', post_id)
    pipe.hset(f'comment:{comment_id}', 'user_id', user_id)
    pipe.hset(f'comment:{comment_id}', 'username', username)
    pipe.hset(f'comment:{comment_id}', 'message', message)
    pipe.hset(f'comment:{comment_id}', 'creation_dt', creation_dt)

    mapping = {comment_id: creation_dt}
    # pipe.zadd('postlist', mapping)
    # pipe.zadd(f'userpostlist:{user_id}', mapping)
    pipe.zadd(f'comments:{post_id}', mapping)

    pipe.hincrby(f'post:{post_id}', 'comments', 1)

    # TODO: updated post list for followers

    #     followers = red.zrevrange(f"follower:{user_id}", 0, -1)
    #     for follower in followers:
    #         pipe.zadd(f'upostlist:{follower}', mapping)

    pipe.execute()

    result = {'post_id': post_id}

    response = {'message': 'Success', 'data': result}

    return jsonify(response), 201


@app.route('/api/userposts/<uid>', methods=['GET'])
def get_posts_by_user(uid):
    """Return all the latest posts by user"""
    postlist = red.zrevrange(f'upostlist:{uid}', 0, -1)
    print(postlist)

    posts = []

    for post_id in postlist:
        post = red.hgetall(f'post:{post_id}')
        print(post)
        posts.append(post)

    response = {'message': 'Success', 'data': posts}
    return jsonify(response), 200


@app.route('/api/posts', methods=['POST'])
def create_post():
    """ Create a post, and update the post list.
    return HTTP 201 if created sucessfully
    """
    data = request.get_json()

    print(list(data.keys()))

    user_id = data['user_id']
    print(user_id)
    username = data['username']
    print(username)
    message = data['message']
    print(message)
    # creation_dt = data['creation_dt']
    # print(creation_dt)

    creation_dt = time.time()
    post_id = red.incr('postid')

    pipe = red.pipeline()
    pipe.hset(f'post:{post_id}', 'post_id', post_id)
    pipe.hset(f'post:{post_id}', 'user_id', user_id)
    pipe.hset(f'post:{post_id}', 'username', username)
    pipe.hset(f'post:{post_id}', 'message', message)
    pipe.hset(f'post:{post_id}', 'likes', 0)
    pipe.hset(f'post:{post_id}', 'comments', 0)
    pipe.hset(f'post:{post_id}', 'creation_dt', creation_dt)

    mapping = {post_id: creation_dt}
    pipe.zadd('postlist', mapping)
    pipe.zadd(f'userpostlist:{user_id}', mapping)
    pipe.zadd(f'upostlist:{user_id}', mapping)

    # TODO: update use profile
    # Update post count in user profile

    # TODO: updated post list for followers

    #     followers = red.zrevrange(f"follower:{user_id}", 0, -1)
    #     for follower in followers:
    #         pipe.zadd(f'upostlist:{follower}', mapping)

    pipe.execute()

    result = {'post_id': post_id}

    response = {'message': 'Success', 'data': result}

    return jsonify(response), 201




if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8082)
