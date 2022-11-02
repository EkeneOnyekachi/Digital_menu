from flask import Flask, request, jsonify
import json
from flask_cors import CORS
from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
DEBUG = True
setup_db(app)
CORS(app)


# db_drop_and_create_all()

#Get all drinks
@app.route("/drinks")
def obtain_drinks():
    try:
        drinks = Drink.query.all()
        if len(drinks) == 0:
            return jsonify({"success": False, "error": "resource not found"}), 404
        return (
            jsonify({"success": True, "drinks": [drink.short() for drink in drinks]}),
            200,
        )
    except Exception:
        return jsonify({"success": False, "error": "an error occurred"}), 500


@app.route("/drinks-detail")
@requires_auth("get:drinks-detail")
def get_drinks(payload):
    try:
        drinks = Drink.query.all()
        if len(drinks) == 0:
            return jsonify({"success": False, "error": "resource not found"}), 404
        return (
            jsonify({"success": True, "drinks": [drink.long() for drink in drinks]}),
            200,
        )
    except Exception:
        return jsonify({"success": False, "error": "an error occurred"}), 500


@app.route("/drinks", methods=["POST"])
@requires_auth("post:drinks")
def create_drink(paylod):
    try:
        body = request.get_json()
        new_title = body.get("title")
        new_recipe = body.get("recipe")

        drink = Drink(title=new_title, recipe=json.dumps(new_recipe))

        try:
            drink.insert()

            return jsonify({"success": True, "drinks": [drink.long()]}), 200
        except Exception:
            return jsonify({"sucess": False, "error": "unprocessable entity"}), 422
    except Exception:
        return jsonify({"success": False, "error": "an error occured"}), 500


@app.route("/drinks/<id>", methods=["PATCH"])
@requires_auth("patch:drinks")
def update_drink(paylod, id):
    try:
        body = request.get_json()
        drink = Drink.query.filter(Drink.id == id).one_or_none()

        title = body.get("title")
        recipe = body.get("recipe")

        try:
            drink.title = title
            drink.recipe = json.dumps(recipe)

            drink.update()

            return jsonify({"success": True, "drinks": [drink.long()]}), 200
        except Exception:
            return jsonify({"success": False, "error": "unprocessable entity"}), 422
    except Exception:
        return jsonify({"success": False, "error": "an error occured"}), 500


@app.route("/drinks/<id>", methods=["DELETE"])
@requires_auth("delete:drinks")
def delete_drink(paylod, id):

    try:
        drink = Drink.query.filter(Drink.id == id).one_or_none()

        if drink is None:
            return jsonify({"success": False, "error": "resource not found"}), 404
        drink.delete()
        return jsonify({"success": True, "delete": id}), 200
    except Exception:
        return jsonify({"success": False, "error": "an error occured"}), 500


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({"success": False, "error": 422, "message": "unprocessable"}), 422


@app.errorhandler(404)
def not_found(error):
    jsonify({"success": False, "error": 404, "message": "resource not found"}), 404


@app.errorhandler(500)
def internal_server_error(error):
    return (
        jsonify({"success": False, "error": 500, "message": "internal server error"})
    ), 500


@app.errorhandler(AuthError)
def auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response
