import json
from flask import Flask, jsonify, render_template, request, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, URL
import requests

API_URL = "http://127.0.0.1:9998"

app = Flask(__name__)
app.config['SECRET_KEY'] = '1AYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

header = {
    "Content-Type": "application/json"
}


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


# WTForm
class AddCafeForm(FlaskForm):
    name = StringField("Cafe's Name", validators=[DataRequired()])
    map_url = StringField("Map URL", validators=[DataRequired(), URL()])
    img_url = StringField("Cafe Image URL", validators=[DataRequired(), URL()])
    location = StringField("Location", validators=[DataRequired()])
    seats = StringField("Number of Seats", validators=[DataRequired()])
    has_toilet = StringField("Has Toilet: True or False", validators=[DataRequired()])
    has_wifi = StringField("Has Wifi: True or False", validators=[DataRequired()])
    has_sockets = StringField("Has Sockets: True or False", validators=[DataRequired()])
    can_take_calls = StringField("Can Take Calls: True or False", validators=[DataRequired()])
    coffee_price = StringField("Coffee Price in £", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


##--------------------------Website Endpoints---------------------------------------

@app.route("/")
def home():
    return render_template("index.html", methods=["GET"])


@app.route('/cafes')
def cafes():
    response = requests.get(API_URL + "/all")
    cafes = response.json()
    return render_template('cafes.html', cafes=cafes["cafes"])


@app.route("/add", methods=['GET', 'POST'])
def add_new_cafe():
    form = AddCafeForm()
    if form.validate_on_submit():
        new_cafe = Cafe(
            name=form.name.data,
            map_url=form.map_url.data,
            img_url=form.img_url.data,
            location=form.location.data,
            seats=form.seats.data,
            has_toilet=bool(form.has_toilet.data),
            has_wifi=bool(form.has_wifi.data),
            has_sockets=bool(form.has_sockets.data),
            can_take_calls=bool(form.can_take_calls.data),
            coffee_price=form.coffee_price.data
        )
        #print(json.dumps(new_cafe.to_dict()))
        response = requests.post(API_URL + "/addcafe", json=json.dumps(new_cafe.to_dict()))
        return redirect(url_for("cafes"))
    return render_template("add.html", form=form)


@app.route("/delete/<int:cafe_id>")
def delete_cafe(cafe_id):
    cafe_to_delete = Cafe.query.get(cafe_id)
    db.session.delete(cafe_to_delete)
    db.session.commit()
    return redirect(url_for("show_cafes"))


##----------------------------API EndPoints-----------------------------------------

## HTTP GET - Read Record
@app.route("/random")
def get_random_cafe():
    cafes = db.session.query(Cafe).all()
    return jsonify(cafe=cafes.to_dict())


@app.route("/all")
def get_all_cafes():
    cafes = db.session.query(Cafe).all()
    return jsonify(cafes=[cafe.to_dict() for cafe in cafes])


@app.route("/addcafe", methods=["POST"])
def post_new_cafe():
    new_cafe_request = json.loads(request.get_json())
    new_cafe = Cafe(
        name=new_cafe_request['name'],
        map_url=new_cafe_request["map_url"],
        img_url=new_cafe_request["img_url"],
        location=new_cafe_request["location"],
        has_sockets=bool(new_cafe_request["has_sockets"]),
        has_toilet=bool(new_cafe_request["has_toilet"]),
        has_wifi=bool(new_cafe_request["has_wifi"]),
        can_take_calls=bool(new_cafe_request["can_take_calls"]),
        seats=new_cafe_request["seats"],
        coffee_price=new_cafe_request["coffee_price"],
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe."})


@app.route("/update-price/<int:cafe_id>", methods=["PATCH"])
def patch_new_price(cafe_id):
    new_price = request.args.get("new_price")
    cafe = db.session.query(Cafe).get(cafe_id)
    if cafe:
        cafe.coffee_price = new_price
        db.session.commit()
        return jsonify(response={"success": "Successfully updated the price."}), 200
    else:
        return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404


@app.route("/deletecafe/<int:cafe_id>")
def API_delete_cafe(cafe_id):
    cafe_to_delete = Cafe.query.get(cafe_id)
    db.session.delete(cafe_to_delete)
    db.session.commit()
    return redirect(url_for("show_cafes"))


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=9998, debug=True)
