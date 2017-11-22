from tod import db


class VpaDetails(db.Model):
    id = db.Column(db.String(90), primary_key=True)
    vpa = db.Column(db.String(90))
    tod_transactions = db.relationship(
        'TodTransaction',
        backref='vpadetails',
        lazy='dynamic')
    icici_transaction = db.relationship(
        'IciciTransaction',
        backref='vpadetails',
        lazy='dynamic',
        primaryjoin="or_(VpaDetails.id==IciciTransaction.payee_id, VpaDetails.id==IciciTransaction.payer_id)")

    def __repr__(self):
        return '<CustomerDetails %r>' % (self.customer_id)


class TodTransaction(db.Model):
    transaction_id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float)
    remarks = db.Column(db.String(100))
    customer_id = db.Column(db.String(90), db.ForeignKey('vpa_details.id'))
    status = db.Column(db.Integer)
    tod_transaction_state = db.relationship(
        'TodTransactionState',
        backref='todtransaction',
        lazy='dynamic')
    tod_transactions_icici = db.relationship(
        'IciciTransaction',
        backref='todtransaction',
        lazy='dynamic')

    def __repr__(self):
        return str(self.transaction_id)


class IciciTransaction(db.Model):
    transaction_id = db.Column(db.Integer, primary_key=True)
    payee_id = db.Column(db.String(90), db.ForeignKey('vpa_details.id'))
    payer_id = db.Column(db.String(90), db.ForeignKey('vpa_details.id'))
    tod_transaction_id = db.Column(
        db.Integer,
        db.ForeignKey('tod_transaction.transaction_id'))
    status = db.Column(db.String(20))
    remarks = db.Column(db.String(90))
    timestamp = db.Column(db.DateTime)

    def __repr__(self):
        return 'ICICI txn {0}'.format(self.transaction_id)


class TodTransactionState(db.Model):
    transaction_id = db.Column(
        db.Integer,
        db.ForeignKey('tod_transaction.transaction_id'),
        )
    ticket_id = db.Column(db.Integer, primary_key=True)
    customer_product_received = db.Column(db.Integer)
    customer_product_good_condition =db.Column(db.Integer)
    delivery_product_delivered =db.Column(db.Integer)
    delivery_product_good_condition =db.Column(db.Integer)
    customer_response = db.Column(db.Integer)
    delivery_response = db.Column(db.Integer)

    def __repr__(self):
        return 'TodTransactionState txn {0}'.format(self.transaction_id)
