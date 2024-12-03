from flask import Flask, request, jsonify
from flask_cors import CORS  # Importálás
import requests
import ibm_boto3
from ibm_botocore.client import Config
import json
import os

# Flask alkalmazás létrehozása
app = Flask(__name__)

# CORS engedélyezése minden domain számára
CORS(app)

# IBM Cloud Object Storage konfigurálása
cos = ibm_boto3.client(
    's3',
    ibm_api_key_id='5o6X835azJMALPLiebgIUUqRQ8e-NEM_PkQJ4thH9aI7',
    ibm_service_instance_id='f39973c6-786a-459c-9564-40f6d8e6a6b7',
    config=Config(signature_version='oauth'),
    endpoint_url='https://s3.us-south.cloud-object-storage.appdomain.cloud'
)

bucket_name = 'servicenow3'  # COS bucket neve

# Token érvényességének ellenőrzése
def check_token_validity(felhasználónév):
    try:
        # Token lekérése a COS-ból
        response_token = cos.get_object(Bucket=bucket_name, Key=f'{felhasználónév}_user_token')
        token = response_token['Body'].read().decode('utf-8')

        # Token használatával próbáljuk lekérni a felhasználó adatokat
        headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
        response_user = requests.get(
            f"https://dev227667.service-now.com/api/now/table/sys_user?sysparm_query=user_name={felhasználónév}",
            headers=headers
        )

        # Ha a válasz státuszkódja 200, akkor a token érvényes
        if response_user.status_code == 200:
            return "Hitelesítés sikeres"
        else:
            return "Hitelesítés sikertelen"

    except Exception as e:
        # Ha bármi hiba történik (pl. token nem található vagy nem olvasható), akkor a hitelesítés sikertelen
        print(f"Hiba történt a token ellenőrzésekor: {e}")
        return "Hitelesítés sikertelen"


# Flask útvonal a token ellenőrzéshez
@app.route('/check_token', methods=['POST'])
def check_token():
    data = request.json
    felhasználónév = data.get('felhasználónév')

    if not felhasználónév:
        return jsonify({"error": "A felhasználónév megadása szükséges"}), 400

    result = check_token_validity(felhasználónév)
    return jsonify({"message": result})


# Flask szerver indítása
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
