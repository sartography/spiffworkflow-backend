from flask_bpmn.models.db import db


class CartModel(db.Model):
    __tablename__ = 'carts'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
