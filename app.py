from flask import Flask, request, jsonify
import logging
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Set up Flask app and logging
app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

# Database setup
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    "DATABASE_URL", "sqlite:///dustbin_data.db")
# Disable tracking modifications for performance
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define Dustbin model


class Dustbin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True, nullable=False, index=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    address = db.Column(db.String(100), nullable=False)
    recyclable_bio = db.Column(db.Float, nullable=False)
    recyclable_nonbio = db.Column(db.Float, nullable=False)
    nonrecyclable_bio = db.Column(db.Float, nullable=False)
    nonrecyclable_nonbio = db.Column(db.Float, nullable=False)
    overall_fill_percentage = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


# Initialize the database
with app.app_context():
    db.create_all()


@app.route("/update_dustbin_data", methods=["POST"])
def update_dustbin():
    """
    Accepts JSON data and updates or adds a dustbin entry in the database.
    """
    data = request.json
    required_fields = ["code", "latitude", "longitude", "address", "recyclable_bio",
                       "recyclable_nonbio", "nonrecyclable_bio", "nonrecyclable_nonbio",
                       "overall_fill_percentage", "timestamp"]

    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        logging.error(f"Missing fields: {missing_fields}")
        return jsonify({"error": f"Missing fields: {missing_fields}"}), 400

    try:
        timestamp = datetime.strptime(data["timestamp"], "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return jsonify({"error": "Invalid timestamp format, expected YYYY-MM-DD HH:MM:SS"}), 400

    dustbin = Dustbin.query.filter_by(code=data["code"]).first()

    if not dustbin:
        dustbin = Dustbin(
            code=data["code"], latitude=data["latitude"], longitude=data["longitude"],
            address=data["address"], recyclable_bio=data["recyclable_bio"],
            recyclable_nonbio=data["recyclable_nonbio"], nonrecyclable_bio=data["nonrecyclable_bio"],
            nonrecyclable_nonbio=data["nonrecyclable_nonbio"], overall_fill_percentage=data["overall_fill_percentage"],
            timestamp=timestamp
        )
        db.session.add(dustbin)
        status_code = 201
    else:
        dustbin.recyclable_bio = data["recyclable_bio"]
        dustbin.recyclable_nonbio = data["recyclable_nonbio"]
        dustbin.nonrecyclable_bio = data["nonrecyclable_bio"]
        dustbin.nonrecyclable_nonbio = data["nonrecyclable_nonbio"]
        dustbin.overall_fill_percentage = data["overall_fill_percentage"]
        dustbin.timestamp = timestamp
        status_code = 200

    try:
        db.session.commit()
        logging.info(f"Data stored for Dustbin {data['code']}: {
                     data['overall_fill_percentage']}%")
        return jsonify({"message": "Data received successfully"}), status_code
    except Exception as e:
        db.session.rollback()
        logging.error(f"Database commit failed: {str(e)}")
        return jsonify({"error": "Database error"}), 500


@app.route("/get_dustbin_data", methods=["GET"])
def get_dustbin_data():
    """
    Returns all dustbin data stored in the database.
    """
    dustbins = Dustbin.query.all()
    return jsonify({"dustbins": [
        {col.name: getattr(bin, col.name) for col in bin.__table__.columns} for bin in dustbins
    ]})


if __name__ == "__main__":
    app.run(debug=True)
