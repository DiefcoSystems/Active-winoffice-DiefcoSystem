from flask import Flask, request, Response
import firebase_admin
from firebase_admin import credentials, firestore
import json

app = Flask(__name__)

# Firebase Credentials JSON configuration
firebase_config = {
  "type": "service_account",
  "project_id": "active-winoffice-diefcosystem",
  "private_key_id": "21051d5be75ea0bca1bec554841fea50a1dcfcba",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQCrkN8uXgOeZjNd\nEXW0H2vHBVnhE7jlZ345ZIWt8SvCrm37CUYUwNPQhB3WkBUcy5jc8OdtAx43Yl9L\nlgRma7YjfkubLri3xJADvjIifsZN+y+ES3NUVjieYpmpZ4Dz+g1mUiY5qmj4Z8zh\ntu322k4sHm8YKsMUKBVj4VjUrQOqOVtI56qOiiGtA0N1CSWzFNz63Kn1tD+uqOhp\nq+2ZEtvHN8sWub8+/owbq0vT6UVatKmiDHd2AU5Qrmd7jAfky52a8lamllo5WYKF\naZkruWi95/n+aX9EmXBgYKBYGzshOo1OqkLLhGqs9vyUnv2iCbHmD/R4mSpo8w+m\nEI9Wft2DAgMBAAECggEAKXQgqNhocW5qPLOKSBJLfVQKqnqUc0F1WzKxphyeoTR6\nOGy+NSd+RmSVvRElOMbs0X2XvVxCgclQEzhVKdYetSa/5+f7E9P3pB/hhzowegkW\nKxX78MXAemyCik8K9mhVsoJo4AgPwu15sJP9nWaT+s8DssgqSIWC3ZZGW2TOfONn\netv4DG8++bJXwPM+vDvTn8qN+glGf0IFU7UaBkQEXJQfS9rJ/ywGsf8Pc6jI+CNZ\nUss+hAAwBZy3ZlZFwfi9y14K3H8ljAJZUr3KKfru41/3dP7ENu/T0cX6VpZ3XniS\nMc/Zlgshl0/7eV1SQKdFo0vSAFPiBZsDk1B4REZhmQKBgQDeP7W3Zrq+SL21ZROR\n1b8rYwHiSUM+KlkQ6D0an//+eA2ejSN9GdaX6boSLP6HcVhnLTUwzNUZLu1Wplg2\n2yCrLZsyQRlyhJmJsaaXqfgyjlCSJXuovoVVLBWPPT9tR09d5dbtFomh+Gy9vyht\nbURH0vLochpRYqPqqnNO6zH6nQKBgQDFnsdMqgMZVTcgfulYL3wj9nWYopNeJL31\nxiq30rWazk7j/2y+oSeJI4JlJSBwAWEFdQJzy1qbDNKO1dq4YSuOmIpe7WrlCTkB\nv/CESH2axS82v+pf+l11Z6RaktGeqV76BVGTA0u4c1STTKGfGJmpmcZbMP/qzNX8\n9wWt41wunwKBgQCIIt5ciUC6bjRGeLOUESoYmXz974KRAb+s65UCSh+08DTneezT\nJJCeXTztBUKkFHniOX7rdYzS8DvRZ/OBJpjMQhNepSHBVBf4kClLnYG69hHEc9Fb\ne9iQY4CRTSMc/SFQkwkkETodTN7PG9jXrqa0mDLSz5HvaEyf4ejf3GuwQKBgQCD\nbqV4bH4hJBbE6wNAnlw/AtSVTlMawu7//es9VMtpiRrY8nEdm8rSn6ZCpN2dAJ3J\nZlfaMX4yLuX/D2YnSKESdotYtShp6adbbY+GOzwmakyLajpz2Oy9f8/EWW9Gybic\nKltlnkSHCVVPniDD0jWoodhVoBIk1FThqFzDmLofWwKBgQCfw3tvcvCLROWWakxr\n+C4SVTRWQDCbmva5XFUdDL08xLGg1ahHzgsemLXBbzyPi7UouD/kLso3to9VnMbn\nvqCSiIO9CeYnAbpFCGYZq03kVI11tMskez5sTqxeMIc/+uOSwnvlmqJOKqaZNirQ\nQZM2wujODqB0E1Zb76Xctb/VkQ==\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-fbsvc@active-winoffice-diefcosystem.iam.gserviceaccount.com",
  "client_id": "117763845775781682477",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40active-winoffice-diefcosystem.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}

if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_config)
    firebase_admin.initialize_app(cred)

db = firestore.client()

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST'])
@app.route('/<path:path>', methods=['GET', 'POST'])
def catch_all(path):
    if request.method == 'GET':
        return Response("Server is running successfully.", mimetype='text/plain')

    token_sent = None
    if request.is_json:
        try:
            token_sent = request.json.get('token')
        except Exception:
            pass

    if not token_sent:
        return Response("Write-Host 'Error: Token is missing!' -ForegroundColor Red", mimetype='text/plain; charset=utf-8')

    try:
        users_ref = db.collection('users')
        query = users_ref.where('token', '==', token_sent).limit(1).stream()
        
        user_doc = None
        for doc in query:
            user_doc = doc
            break

        if not user_doc:
            return Response("Write-Host 'Invalid Activation Code!' -ForegroundColor Red", mimetype='text/plain; charset=utf-8')
        
        user_data = user_doc.to_dict()
        usage_count = user_data.get('usageCount', 0)
        
        if usage_count >= 2:
            return Response("Write-Host 'This code has reached its maximum usage limit (2 times)!' -ForegroundColor Red", mimetype='text/plain; charset=utf-8')
        
        # تحديث العداد في فايربيز أولاً
        user_doc.reference.update({'usageCount': usage_count + 1})
        
        # بدلاً من جلب السكربت من السيرفر مسبباً كراش، نمرر الأمر للباورشيل لينفذه العميل تلقائياً في نفس السطر بأمان وبشكل مخفي
        full_payload = "Write-Host 'Code Accepted! Launching Activation System...' -ForegroundColor Green; irm https://get.activated.win | iex"
        return Response(full_payload, mimetype='text/plain; charset=utf-8')
                
    except Exception as e:
        return Response(f"Write-Host 'Server internal error: {str(e)}' -ForegroundColor Red", mimetype='text/plain; charset=utf-8')
