from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
 
##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
 
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
        dictionary = {}
 
        for column in self.__table__.columns:
            dictionary[column.name] = getattr(self, column.name)
 
        return dictionary
 
@app.route("/")
def home():
    return render_template("index.html")
 
@app.route("/all", methods=["GET"])
def get_all():
    cafes = db.session.query(Cafe).all() ################ERROR-LINE###################
    print(cafes)
    return jsonify(cafes=[cafe.to_dict() for cafe in cafes])

@app.route('/search/',methods=['GET'])
def search():
    req_cafe=request.args.get('loc')
    req_cafe=req_cafe.title()
    print(req_cafe)
    caf_=Cafe.query.filter_by(location=req_cafe).all()
    # caf_=db.session.query(Cafe).all()
    print(caf_)
    if caf_:
        return  jsonify(cafe=[caf.to_dict() for caf in caf_])
    # for caf in caf_:
    #     print(caf.location)
    #     if caf.location==req_cafe:
    #        return  jsonify(cafe=caf.to_dict())
    #        break
    return jsonify(error={"error":"there were no cafe in  the place"})

@app.route('/add',methods=['POST'])
def add_new():
    new_cafe=Cafe(
    name=request.form.get('name'),
    map_url=request.form.get('map_url'),
    img_url=request.form.get('img_url'),
    location=request.form.get('loc'),
    has_sockets=bool(request.form.get('sockets')),
    has_toilet=bool(request.form.get('toilet')),
    has_wifi=bool(request.form.get('wifi')),
    can_take_calls=bool(request.form.get('calls')),
    seats=request.form.get('seats'),
    coffee_price=request.form.get('coffee_price')                         
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(responce={"sucess":"sucessfully added new cafe"})


@app.route('/update-price/<int:ids>/',methods=['PATCH','GET'])
def updates(ids):
    cafe_update=Cafe.query.filter_by(id=ids)
    print(cafe_update)
    up_price=str(request.args.get('new_price'))
    print(up_price)
    if cafe_update:
        cafe_update.coffee_price=up_price
        db.session.commit()
        print(cafe_update.coffee_price)
        return jsonify(responce={"sucess":"price updated for cafe"})
    else:
        return jsonify(responce={"error":"error no cafe found for id"})
@app.route("/report-closed/<int:cafe_id>/", methods=["DELETE"])
def delete_cafe(cafe_id):
    api_key = request.args.get("api-key")
    if api_key == "TopSecretAPIKey":
        cafe = db.session.query(Cafe).get(cafe_id)
        if cafe:
            db.session.delete(cafe)
            db.session.commit()
            return jsonify(response={"success": "Successfully deleted the cafe from the database."}), 200
        else:
            return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404
    else:
        return jsonify(error={"Forbidden": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403
if __name__=='__main__':
    app.run(debug=True)