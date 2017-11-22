from flask import render_template, session, redirect, url_for, request
from tod import app, db
from forms import ClientVoteForm, DeliveryVoteForm
from models import VpaDetails, TodTransaction, IciciTransaction, TodTransactionState
import requests
import datetime
import json


NETBANKING = 'Netbanking'
CREDIT_CARD = 'Credit Card'
DEBIT_CARD = 'Debit Card'
COD = 'Cash On Delivery'
TOD = 'Transfer On Delivery'

payment_codes = {}
payment_codes[NETBANKING] = 'netbanking'
payment_codes[CREDIT_CARD] = 'creditcard'
payment_codes[DEBIT_CARD] = 'debitcard'
payment_codes[COD] = 'cod'
payment_codes[TOD] = 'tod'


vpa_to_custid = {}
custid_to_vpa = {}

vpa_to_custid['escrow@icicibank'] =    '33336390'
vpa_to_custid['customer1@icicibank'] = '33336389'
vpa_to_custid['customer2@icicibank'] = '33336392'
vpa_to_custid['merchant@icicibank'] =  '33336391'


custid_to_vpa['33336390'] = 'escrow@icicibank'
custid_to_vpa['33336389'] = 'customer1@icicibank'
custid_to_vpa['33336392'] = 'customer2@icicibank'
custid_to_vpa['33336391'] = 'merchant@icicibank'

status_tod = {}
status_tod[1] = 'In Escrow'
status_tod[2] = 'Paid To Merchant'
status_tod[3] = 'Refunded To Customer'
status_tod[4] = 'Conflict-To Be Resolved'


status_color = {}
status_color[1] = 'orange'
status_color[2] = 'green'
status_color[3] = 'green'
status_color[4] = 'red'

@app.route('/merchant')
def merchant():
    return render_template('merchant.html',
                           payment_methods=payment_codes)

@app.route('/')
def index():
    if not session.has_key('token'):
        x = requests.get('https://corporateapiprojectwar.mybluemix.net/corporate_banking/mybank/authenticate_client?client_id=rajathalex@gmail.com&password=FAJ83SAS')
        session['token'] = x.json()[0]['token']

    return render_template('index.html')

@app.route('/admin')
def admin():
    response = TodTransaction.query.all()
    return render_template('admin.html', response=response, custid_to_vpa=custid_to_vpa, status_tod=status_tod, status_color=status_color)

@app.route('/vote/<person>', methods=['GET'])
def vote(person):
    # we should should only unprocessed transactions
    txnids = TodTransaction.query.filter_by(status=1)
    numberOfTransactions = 0
    for i in txnids:
        numberOfTransactions = numberOfTransactions+1
    return render_template('vote_now.html',person=person, transactions=txnids, numberOfTransactions=numberOfTransactions)

@app.route('/payment', methods=['POST'])
def payment():
    print request.form.values()
    print request.form.keys()
    print request.form["formAmount"]
    print request.form['formCustomerVPA']
    print request.form['formRemarks']
    #if option != payment_codes[TOD]:
    #    return 'mainstream payment methods! won\'t support that'
    #else:
    amount = request.form['formAmount']
    remarks = request.form['formRemarks']
    customer_vpa = request.form['formCustomerVPA']
    customer_id = vpa_to_custid[customer_vpa]
    customer_details = VpaDetails(id=customer_id, vpa=customer_vpa)

    customer_db_response = VpaDetails.query.get(customer_id)
    customer_present = False
    if customer_db_response is not None:
        customer_present = True

    payer_db_response = VpaDetails.query.get(customer_id)
    payee_db_response = VpaDetails.query.get('33336390')

    payer_vpa = payer_db_response.vpa
    payee_vpa = payee_db_response.vpa

    make_payment_url = 'https://upiservice.mybluemix.net/banking/icicibank/upiFundTransferVToV?client_id=rajathalex@gmail.com&token={0}&payerCustId={1}&payerVPA={2}&payeeVPA={3}&amount={4}&remarks={5}'.format(
        session['token'],
        customer_id,
        payer_vpa,
        payee_vpa,
        amount,
        remarks)
    print make_payment_url
    payment_response = requests.get(make_payment_url)

    icici_payment_response = payment_response.json()[-1]
    try:
        if not customer_present:
            db.session.add(customer_details)
            db.session.commit()
            tod_transaction_details = TodTransaction(
                vpadetails=customer_details,
                amount=amount,
                remarks=remarks,
                status=1)
            db.session.add(tod_transaction_details)
        else:
            tod_transaction_details = TodTransaction(
                vpadetails=customer_db_response,
                amount=amount,
                remarks=remarks,
                status=1)
            db.session.add(tod_transaction_details)
        print icici_payment_response['transaction_date']
        icici_transaction_date = datetime.datetime.strptime(
            icici_payment_response['transaction_date'],
            '%Y-%m-%d %H:%M:%S')
        icici_transaction_details = IciciTransaction(
            transaction_id=icici_payment_response['transaction_id'],
            status=icici_payment_response['status'],
            todtransaction=tod_transaction_details,
            timestamp=icici_transaction_date,
            payer_id=payer_db_response.id,
            payee_id=payee_db_response.id,
            remarks=remarks)

        db.session.add(icici_transaction_details)
        db.session.commit()
    except:
        return render_template('merchant.html',
                error=icici_payment_response['description']+'! Please choose another payment method',
                payment_methods=payment_codes)

    return render_template(
        'transaction_done.html',
        txnid=str(tod_transaction_details))


def validate_smart_contract(txnid, tod_transaction_details):
    print 'Internal server transaction id {0}'.format(tod_transaction_details.transaction_id)
    states = tod_transaction_details.tod_transaction_state.all()  # retrieving states based on the txn id
    payload = {}
    payload['customer'] = states[0].customer_response
    payload['delivery'] = states[0].delivery_response

    escrow_db_response = VpaDetails.query.get('33336390')
    if payload['customer'] == payload['delivery']:
        if payload['customer']:
            # send to merchant
            merchant_db_response = VpaDetails.query.get('33336391')
            make_payment_url = 'https://upiservice.mybluemix.net/banking/icicibank/upiFundTransferVToV?client_id=rajathalex@gmail.com&token={0}&payerCustId={1}&payerVPA={2}&payeeVPA={3}&amount={4}&remarks={5}'.format(session['token'], escrow_db_response.id, escrow_db_response.vpa, merchant_db_response.vpa, tod_transaction_details.amount, 'payment from escrow')
            tod_transaction_details.status = 2
            icici_response = requests.get(make_payment_url)
            print make_payment_url
            print icici_response.json()
            icici_payment_response = icici_response.json()[-1]
            icici_transaction_date = datetime.datetime.strptime(
                icici_payment_response['transaction_date'],
                '%Y-%m-%d %H:%M:%S')
            icici_transaction_details = IciciTransaction(
                transaction_id=icici_payment_response['transaction_id'],
                status=icici_payment_response['status'],
                todtransaction=tod_transaction_details,
                timestamp=icici_transaction_date,
                payer_id=escrow_db_response.id,
                payee_id=merchant_db_response.id,
                remarks='payment from escrow')
            db.session.add(tod_transaction_details)
            db.session.add(icici_transaction_details)
            db.session.commit()
            return redirect(url_for('index'))
        else:
            # send back to customer from escrow
            tod_transaction_details.status = 3
            customer_id = tod_transaction_details.customer_id
            customer_db_response = VpaDetails.query.get(customer_id)
            make_payment_url = 'https://upiservice.mybluemix.net/banking/icicibank/upiFundTransferVToV?client_id=rajathalex@gmail.com&token={0}&payerCustId={1}&payerVPA={2}&payeeVPA={3}&amount={4}&remarks={5}'.format(session['token'], escrow_db_response.id, escrow_db_response.vpa, customer_db_response.vpa, tod_transaction_details.amount, 'refund for {0}'.format(tod_transaction_details.transaction_id))
            icici_response = requests.get(make_payment_url)
            print make_payment_url
            print icici_response.json()
            icici_payment_response = icici_response.json()[-1]
            icici_transaction_date = datetime.datetime.strptime(
                icici_payment_response['transaction_date'],
                '%Y-%m-%d %H:%M:%S')
            icici_transaction_details = IciciTransaction(
                transaction_id=icici_payment_response['transaction_id'],
                status=icici_payment_response['status'],
                todtransaction=tod_transaction_details,
                timestamp=icici_transaction_date,
                payer_id=escrow_db_response.id,
                payee_id=customer_db_response.id,
                remarks='refund for {0}'.format(tod_transaction_details.transaction_id))
            db.session.add(tod_transaction_details)
            db.session.add(icici_transaction_details)
            db.session.commit()
            return redirect(url_for('index'))

    else:
        tod_transaction_details.status = 4
        db.session.add(tod_transaction_details)
        db.session.commit()
        payload['conflict'] = 'huge conflict ! Needs to be resolved'
    	return redirect(url_for('index'))
    return json.dumps(payload)

@app.route('/customer/<transaction_id>', methods=['GET', 'POST'])
def client_vote(transaction_id):
    form = ClientVoteForm()
    if request.method == 'POST' and form.validate_on_submit():
        product_received = form.product_received.data
        product_good_condition = form.product_good_condition.data

        if product_received:
            product_received = 1
        else:
            product_received = 0

        if product_good_condition:
            product_good_condition = 1
        else:
            product_good_condition = 0

        tod_transaction_details = TodTransaction.query.get(transaction_id)
        state = TodTransactionState.query.get(transaction_id)
        if (product_received and product_good_condition):
            if state is not None:
                state.customer_response = 1
                state.customer_product_received = product_received
                state.customer_product_good_condition = product_good_condition
                db.session.commit()
                return validate_smart_contract(transaction_id, tod_transaction_details)
            else:
                state = TodTransactionState(todtransaction=tod_transaction_details,
                        customer_response=1,
                        delivery_response=-1,
                        customer_product_good_condition=product_good_condition,
                        customer_product_received=product_received,
                        delivery_product_delivered=-1,
                        delivery_product_good_condition=-1)
                db.session.add(state)
                db.session.commit()
        else:
            if state is not None:
                state.customer_response = 0
                state.customer_product_received = product_received
                state.customer_product_good_condition = product_good_condition
                db.session.commit()
                return validate_smart_contract(transaction_id, tod_transaction_details)
            else:
                state = TodTransactionState(todtransaction=tod_transaction_details,
                        customer_response=0,
                        delivery_response=-1,
                        customer_product_good_condition=product_good_condition,
                        customer_product_received=product_received,
                        delivery_product_delivered=-1,
                        delivery_product_good_condition=-1)
                db.session.add(state)
                db.session.commit()
        return redirect(url_for('index'))
    else:
        print 'no shit is happening'
    return render_template('client_vote.html', form=form)

@app.route('/delivery/<transaction_id>', methods=['GET', 'POST'])
def delivery_vote(transaction_id):
    form = DeliveryVoteForm()
    if request.method=='POST':
        product_delivered = form.product_delivered.data
        product_good_condition = form.product_good_condition.data

        if product_delivered:
            product_delivered = 1
        else:
            product_delivered = 0

        if product_good_condition:
            product_good_condition = 1
        else:
            product_good_condition = 0

        tod_transaction_details = TodTransaction.query.get(transaction_id)
        state = TodTransactionState.query.get(transaction_id)
        if (product_delivered and product_good_condition):
            if state is not None:
                state.delivery_response = 1
                state.delivery_product_delivered = product_delivered
                state.delivery_product_good_condition = product_good_condition
                db.session.commit()
                return validate_smart_contract(transaction_id, tod_transaction_details)
            else:
                state = TodTransactionState(todtransaction=tod_transaction_details,
                        customer_response=-1,
                        delivery_response=1,
                        customer_product_good_condition=-1,
                        customer_product_received=-1,
                        delivery_product_delivered=product_delivered,
                        delivery_product_good_condition=product_good_condition)
                db.session.add(state)
                db.session.commit()
        else:
            if state is not None:
                state.delivery_response = 0
                state.delivery_product_delivered = product_delivered
                state.delivery_product_good_condition = product_good_condition
                db.session.commit()
                return validate_smart_contract(transaction_id, tod_transaction_details)
            else:
                state = TodTransactionState(todtransaction=tod_transaction_details,
                        customer_response=-1,
                        delivery_response=0,
                        customer_product_good_condition=-1,
                        customer_product_received=-1,
                        delivery_product_delivered=product_delivered,
                        delivery_product_good_condition=product_good_condition)
                db.session.add(state)
                db.session.commit()
        return redirect(url_for('index'))
    return render_template('delivery_vote.html', form=form)


