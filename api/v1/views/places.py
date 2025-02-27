#!/usr/bin/python3
"""views for places API
"""

from api.v1.views import app_views
from flask import jsonify, abort, request
from models import storage
from models.state import State
from models.city import City
from models.user import User
from models.place import Place
from models.amenity import Amenity


@app_views.route('/places_search',
                 methods=['POST'],
                 strict_slashes=False)
def places_search():
    """Searching 4 place related to para
    in the body of the request
    """
    # POSTTING THE REQUEST
    if request.is_json:  # if request is valid json
        body = request.get_json()
    else:
        abort(400, 'Not a JSON')

    place_list = []

    # states searching
    if 'states' in body:
        for state_id in body['states']:
            state = storage.get(State, state_id)
            if state is not None:
                for city in state.cities:
                    for place in city.places:
                        place_list.append(place)

    # cities searching
    if 'cities' in body:
        for city_id in body['cities']:
            city = storage.get(City, city_id)
            if city is not None:
                for place in city.places:
                    place_list.append(place)

    # presence of amenities
    if 'amenities' in body and len(body['amenities']) > 0:
        if len(place_list) == 0:
            place_list = [place for place in storage.all(Place).values()]
        del_list = []
        for place in place_list:
            for amenity_id in body['amenities']:
                amenity = storage.get(Amenity, amenity_id)
                if amenity not in place.amenities:
                    del_list.append(place)
                    break
        for place in del_list:
            place_list.remove(place)

    if len(place_list) == 0:
        place_list = [place for place in storage.all(Place).values()]

    # objs to dict/ delete amaneties key
    place_list = [place.to_dict() for place in place_list]
    for place in place_list:
        try:
            del place['amenities']
        except KeyError:
            pass

    return jsonify(place_list)


@app_views.route('/cities/<city_id>/places',
                 methods=['GET', 'POST'],
                 strict_slashes=False)
def places_by_city_requests(city_id):
    """Perform API requests of places by city
    """
    # GETTING REQUESTS
    if request.method == 'GET':
        # retrieving all places related to specific city
        cities = storage.all(City)
        try:
            key = 'City.' + city_id
            city = cities[key]
            place_list = [place.to_dict() for place in city.places]
            return jsonify(place_list)
        except KeyError:
            abort(404)

    # POSTTING THE REQUESTS
    elif request.method == 'POST':
        # new place
        cities = storage.all(City)

        if ('City.' + city_id) not in cities.keys():
            abort(404)

        if request.is_json:  # validing json
            body_request = request.get_json()
        else:
            abort(400, 'Not a JSON')

        # required attributes
        if 'name' not in body_request:
            abort(400, 'Missing name')
        if 'user_id' not in body_request:
            abort(400, 'Missing user_id')

        # verifying the user_id
        users = storage.all(User)
        if ('User.' + body_request['user_id']) not in users.keys():
            abort(404)

        # instantiating store return new State
        body_request.update({'city_id': city_id})
        new_place = Place(**body_request)
        storage.new(new_place)
        storage.save()
        return jsonify(new_place.to_dict()), 201

    # UNSUPPORTTING
    else:
        abort(501)


@app_views.route('/places/<place_id>',
                 methods=['GET', 'DELETE', 'PUT'],
                 strict_slashes=False)
def place_methods(place_id=None):
    """API requests on place objects
    """
    # GETTING REQUESTS
    if request.method == 'GET':

        # specific place object
        places = storage.all(Place)
        try:
            key = 'Place.' + place_id
            place = places[key]
            return jsonify(place.to_dict())
        except KeyError:
            abort(404)

    # REMOVING REQUESTS
    elif request.method == 'DELETE':

        # delete of specific place
        places = storage.all(Place)
        try:
            key = 'Place.' + place_id
            storage.delete(places[key])
            storage.save()
            return jsonify({}), 200
        except KeyError:
            abort(404)

    # PUTTING REQUESTS
    elif request.method == 'PUT':
        places = storage.all(Place)
        key = 'Place.' + place_id
        try:
            place = places[key]

            # JSON to dict
            if request.is_json:
                body_request = request.get_json()
            else:
                abort(400, 'Not a JSON')

            # updating Place object
            ignore = ['id', 'user_id', 'city_id', 'created_at', 'updated_at']
            for key, val in body_request.items():
                if key not in ignore:
                    setattr(place, key, val)

            storage.save()
            return jsonify(place.to_dict()), 200

        except KeyError:
            abort(404)

    # UNSUPPORTING
    else:
        abort(501)
