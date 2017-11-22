from flask_wtf import Form
from wtforms import StringField, BooleanField
from wtforms.validators import DataRequired


class PaymentForm(Form):
    remarks = StringField('remarks', validators=[DataRequired()])
    customer_vpa = StringField('customer_vpa', validators=[DataRequired()])

class ClientVoteForm(Form):
    product_received = BooleanField('product_received')
    product_good_condition = BooleanField('product_good_condition')

class DeliveryVoteForm(Form):
    product_delivered = BooleanField('product_delivered')
    product_good_condition = BooleanField('product_good_condition')
