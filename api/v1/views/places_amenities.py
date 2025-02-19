#!/usr/bin/python3
"""Views for API place and amenity
"""

from api.v1.views import app_views
from flask import jsonify, abort, request
from models import storage
from models.place import Place
from models.amenity import Amenity
from os import getenv


@app_views.route('/places/<place_id>/amenities',
                 methods=['GET'],
                 strict_slashes=False)
@app_views.route('places/<place_id>/amenities/<amenity_id>',
                 methods=['GET', 'DELETE', 'POST'],
                 strict_slashes=False)
def place_amenity_requests(place_id=None, amenity_id=None):
    """serving API for place
    amenity
    """
    mode = getenv('HBNB_TYPE_STORAGE')

    # GETTING REQUESTS
    if request.method == 'GET':
        # searching place
        place = storage.get(Place, place_id)
        if place is None:
            abort(404)

        amenity_list = [amenity.to_dict() for amenity in place.amenities]
        return jsonify(amenity_list)

    # DELETING THE REQUESTS
    elif request.method == 'DELETE':
        # validating amenity and place
        place = storage.get(Place, place_id)
        amenity = storage.get(Amenity, amenity_id)
        if place is None or amenity is None:
            abort(404)

        if amenity not in place.amenities:
            abort(404)

        if mode != 'db':  # mode of the storage
            place.amenity_ids.remove('Amenity.' + amenity_id)

        storage.delete(amenity)
        storage.save()

        return jsonify({}), 200

    # POSTTING THE REQUESTS
    elif request.method == 'POST':
        # amenity to place matching
        place = storage.get(Place, place_id)
        amenity = storage.get(Amenity, amenity_id)
        if place is None or amenity is None:
            abort(404)

        # existing relations
        if amenity in place.amenities:
            return jsonify(amenity.to_dict()), 200

        if mode == 'db':  # mode of storage DB
            place.amenities.append(amenity)

        else:  # storage of the file
            place.amenity_ids.append('Amenity.' + amenity_id)

        storage.save()
        return jsonify(amenity.to_dict()), 201

    # UNSUPPORting
    else:
        abort(501)
