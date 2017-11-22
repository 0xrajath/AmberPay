# get token
AUTH_URL = 'https://corporateapiprojectwar.mybluemix.net/corporate_banking/mybank/authenticate_client?client_id={0}&password={1}'
# Returns account number
PARTICIPANT_DATA_MAPPING = 'https://retailbanking.mybluemix.net/banking/icicibank/participantmapping?client_id={0}'
BALANCE_ENQUIRY = 'https://retailbanking.mybluemix.net/banking/icicibank/balanceenquiry?client_id={0}&token={1}&accountno={2}'
# cust id(unique bank customer id) and account number not important
ACCOUNT_SUMMARY = 'https://retailbanking.mybluemix.net/banking/icicibank/account_summary?client_id={0}&token={1}&custid={2}&accountno={3}'
REGISTERD_PAYEE = 'https://retailbanking.mybluemix.net/banking/icicibank/listpayee?client_id={0}&token={1}&custid={2}'
FUND_TRANSFER = 'https://retailbanking.mybluemix.net/banking/icicibank/fundTransfer?client_id={0}&token={1}&srcAccount={2}&destAccount={3}&amt={4}&payeeDesc={5}&payeeId={6}&type_of_transaction={7}'
TYPE_OF_TRANSACTION = ['PMR', 'Direct-To-Home payments']
DEBIT_CARD_DETAILS = 'https://debitcardapi.mybluemix.net/debit/icicibank/getDebitDetails?client_id={0}&token={1}&custid={2}'
AUTHORIZE_DEBIT_CARD = 'https://debitcardapi.mybluemix.net/debit/icicibank/authDebitDetails?client_id={0}&token={1}&custid={2}&debit_card_no={3}&cvv={4}&expiry_date={5}'
