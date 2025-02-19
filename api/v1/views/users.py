#!/usr/bin/python3
"""View for users to handle API
"""

from api.v1.views import app_views
from flask import jsonify, abort, request
from models import storage


@app_views.route('/users', methods=['GET', 'POST'], strict_slashes=False)
@app_views.route('/users/<user_id>', methods=['GET', 'DELETE', 'PUT'],
                 strict_slashes=False)
def users_method(user_id=None):
    """if id is none manipulate the
    user object
    """
    from models.user import User
    users = storage.all(User)

    # GETTING THE REQUESTS
    if request.method == 'GET':
        if not user_id:  # return all if theres no user
            return jsonify([obj.to_dict() for obj in users.values()])

        key = 'User.' + user_id
        try:  # from obj to dict to json if user exist in the dic
            return jsonify(users[key].to_dict())
        except KeyError:
            abort(404)  # if the User doesnt exist

    # DELETTING THE REQUESTS
    elif request.method == 'DELETE':
        try:
            key = 'User.' + user_id
            storage.delete(users[key])
            storage.save()
            return jsonify({}), 200
        except:
            abort(404)

    # POSTTING THE REQUESTS
    elif request.method == 'POST':
        # JSON to dict
        if request.is_json:
            body_request = request.get_json()
        else:
            abort(400, 'Not a JSON')

        # missing attributes
        if 'email' not in body_request:
            abort(400, 'Missing email')
        elif 'password' not in body_request:
            abort(400, 'Missing password')
        # STORE OR RETURN new User object
        else:
            new_user = User(**body_request)
            storage.new(new_user)
            storage.save()
            return jsonify(new_user.to_dict()), 201

    # PUTting the REQUESTS
    elif request.method == 'PUT':
        key = 'User.' + user_id
        try:
            user = users[key]

            # JSON to dict
            if request.is_json:
                body_request = request.get_json()
            else:
                abort(400, 'Not a JSON')

            for key, val in body_request.items():
                if key != 'id' and key != 'email' and key != 'created_at'\
                   and key != 'updated_at':
                    setattr(user, key, val)

            storage.save()
            return jsonify(user.to_dict()), 200

        except KeyError:
            abort(404)

    # UNSUPPORTing
    else:
        abort(501)
