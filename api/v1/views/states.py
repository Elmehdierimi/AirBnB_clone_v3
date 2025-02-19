#!/usr/bin/python3
"""View for states to handles the api
"""

from api.v1.views import app_views
from flask import jsonify, abort, request
from models import storage


@app_views.route('/states', methods=['GET', 'POST'], strict_slashes=False)
@app_views.route('/states/<state_id>', methods=['GET', 'DELETE', 'PUT'],
                 strict_slashes=False)
def states_get(state_id=None):
    """if state id is none manipulate
    state id
    """
    from models.state import State
    states = storage.all(State)

    # GETTING REQUESTS
    if request.method == 'GET':
        if not state_id:  # No return all
            return jsonify([obj.to_dict() for obj in states.values()])

        key = 'State.' + state_id
        try:  # convert from obj to dict to json
            return jsonify(states[key].to_dict())
        except KeyError:
            abort(404)  # if stateid doesnt exist

    # DELETTING REQUESTS
    elif request.method == 'DELETE':
        try:
            key = 'State.' + state_id
            storage.delete(states[key])
            storage.save()
            return jsonify({}), 200
        except:
            abort(404)

    # POSTTING REQUESTS
    elif request.method == 'POST':
        # JSON to dict
        if request.is_json:
            body_request = request.get_json()
        else:
            abort(400, 'Not a JSON')

        # return new State object
        if 'name' in body_request:
            new_state = State(**body_request)
            storage.new(new_state)
            storage.save()
            return jsonify(new_state.to_dict()), 201
        else:  # if it doesnt contain attribute
            abort(400, 'Missing name')

    # PUTTING REQUESTS
    elif request.method == 'PUT':
        key = 'State.' + state_id
        try:
            state = states[key]

            # JSON to dict
            if request.is_json:
                body_request = request.get_json()
            else:
                abort(400, 'Not a JSON')

            for key, val in body_request.items():
                if key != 'id' and key != 'created_at' and key != 'updated_at':
                    setattr(state, key, val)

            storage.save()
            return jsonify(state.to_dict()), 200

        except KeyError:
            abort(404)

    # UNSUPPORTTING
    else:
        abort(501)
