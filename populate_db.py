from tod import db, models

escrow_vpa_details = models.VpaDetails(id='33336390', vpa='escrow@icicibank')
merchant_vpa_details = models.VpaDetails(id='33336391', vpa='merchant@icicibank')
customer_one_vpa_details = models.VpaDetails(id='33336389', vpa='customer1@icicibank')
customer_two_vpa_details = models.VpaDetails(id='33336392', vpa='customer2@icicibank')

db.session.add(merchant_vpa_details)
db.session.add(escrow_vpa_details)
db.session.add(customer_one_vpa_details)
db.session.add(customer_two_vpa_details)

db.session.commit()
