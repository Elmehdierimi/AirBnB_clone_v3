#!/usr/bin/python3
"""views of amanitites related to API
"""

from api.v1.views import app_views
from flask import jsonify, abort, request
from models import storage


@app_views.route('/amenities', methods=['GET', 'POST'], strict_slashes=False)
@app_views.route('/amenities/<amenity_id>', methods=['GET', 'DELETE', 'PUT'],
                 strict_slashes=False)
def amenity_methods(amenity_id=None):
    """handling requests to API
    """
    from models.amenity import Amenity
    amenities = storage.all(Amenity)

    # GETTING REQUESTS
    if request.method == 'GET':
        if not amenity_id:  # if no return all
            return jsonify([obj.to_dict() for obj in amenities.values()])

        key = 'Amenity.' + amenity_id
        try:  # if yes convert from obj to dict to json
            return jsonify(amenities[key].to_dict())
        except KeyError:
            abort(404)  # amenity_id doesnt exist

    # DELETING THE REQUESTS
    elif request.method == 'DELETE':
        try:
            key = 'Amenity.' + amenity_id
            storage.delete(amenities[key])
            storage.save()
            return jsonify({}), 200
        except:
            abort(404)

    # POSTING THE REQUESTS
    elif request.method == 'POST':
        # jSON to dict
        if request.is_json:
            body_request = request.get_json()
        else:
            abort(400, 'Not a JSON')

        # instantiating store return new Amenity
        if 'name' in body_request:
            new_amenity = Amenity(**body_request)
            storage.new(new_amenity)
            storage.save()
            return jsonify(new_amenity.to_dict()), 201
        else:  # request doesnt contain attribute
            abort(400, 'Missing name')

    # PUTTING THE REQUESTS
    elif request.method == 'PUT':
        key = 'Amenity.' + amenity_id
        try:
            amenity = amenities[key]

            # JSON to dict
            if request.is_json:
                body_request = request.get_json()
            else:
                abort(400, 'Not a JSON')

            for key, val in body_request.items():
                if key != 'id' and key != 'created_at' and key != 'updated_at':
                    setattr(amenity, key, val)

            storage.save()
            return jsonify(amenity.to_dict()), 200
        except KeyError:
            abort(404)

    # UNSUPPORTED
    else:
        abort(501)
