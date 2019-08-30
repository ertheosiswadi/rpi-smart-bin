import firebase_admin
import google.cloud
from firebase_admin import credentials, firestore

cred = credentials.Certificate("./smart-bin-77a5a-firebase-adminsdk-vlnzr-91e9d40740.json")
app = firebase_admin.initialize_app(cred)
# db = firestore.client()
# db.collection(u'trash').document().set({
# 	'weight': '10',
# 	'unit': 'g',
# 	'fullness': '55%',
# 	'timestamp': firestore.SERVER_TIMESTAMP	
# })

store = firestore.client()

doc_ref = store.collection(u'test')
doc_ref.add({u'name': u'test', u'added': u'just now'})