""" IMPORTACIONES """

import os
import re
import requests 
from dotenv import load_dotenv
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from base64 import b64encode

""" cargar variables de ambiente para correr flask """
load_dotenv()

# Acomodar el código de autenticación que va a ir en el header
auth_str = "AC5335ed07f9d725cb587f7d570974f529:2dc56329ce5929f35a73d9192b2b2e53"
auth_bytes = auth_str.encode('utf-8')
auth_b64 = b64encode(auth_bytes).decode('utf-8')
headers = {'Authorization': 'Basic ' + auth_b64}

""" Corre Flask """
app = Flask(__name__)

""" Para responder los mensajes """
def respond(message, media=None):
    response = MessagingResponse()
    if media:
        for img in media:
            response.message(img)
    response.message(message)
    return str(response)

@app.route('/message', methods=['POST'])
def reply():
    saludos_clave = [r"hol+", r"saludos+", r"buenas+"]
    afirmativas_clave = [r"si+", r"yes+", r"sí+"]
    sender = request.form.get('From')
    message = request.form.get('Body')
    media_url = request.form.get('MediaUrl0')
    print(f'{sender} sent {message}')

    # Enviar las tres imágenes después del saludo
    for saludo in saludos_clave:
        if re.search(saludo, message, re.IGNORECASE):
            return respond("Hola, bienvenido a Tu Factura Paga. Para iniciar, por favor, ingresa tu número de cédula. Sin puntos, ni comas. \n Recuerda que las fotos de tus facturas deben de contener : cédula legible, fecha de expedición de la factura y lista de productos de acuerdo a los términos y condiciones: \n  https://www.misede.com/trminos-y-condiciones-tu-factura-paga")

    # Validar cédula
    if message.isdigit():
        return respond(f"La cédula ingresada es: {message}. ¿Está correcta? Responde 'si' o 'no'.")

    # Confirmar cédula
    for afirmativa in afirmativas_clave:
        if re.search(afirmativa, message, re.IGNORECASE):
            """ aquí va una foto """
            return respond("Por favor, envía una imagen de tu factura.")
        elif message.lower() == "no":
            return respond("Por favor, ingresa nuevamente tu número de cédula.")

    # Procesar imagen
    if media_url:
        """r es el link donde quedará la imagen guardada y a donde vamos a acceder r.content será la imagen"""
        r = requests.get(media_url, headers=headers)
        content_type = r.headers['Content-Type']
        id = r.headers['X-Amz-Cf-Id']
        username = sender.split(':')[1] # remove the whatsapp: prefix from the number

        if content_type == 'image/jpeg':
            filename = f'uploads/{username}/{id}.jpg'
        elif content_type == 'image/png':
            filename = f'uploads/{username}/{id}.png'
        elif content_type == 'image/gif':
            filename = f'uploads/{username}/{id}.gif'
        else:
            filename = None

        if filename:
            if not os.path.exists(f'uploads/{username}'):
                os.makedirs(f'uploads/{username}')
            with open(filename, 'wb') as f:
                """Aquí guarda la imagen r.content"""
                f.write(r.content)
            return respond('Gracias por enviar la imagen de tu factura. Para recibir tu bono, recuerda enviar mínimo 5 facturas antes del 15/07/2025.')
        else:
            return respond('El archivo que ha subido no es del tipo imagen: jpg, png')
    else:
        return respond('No ingresaste una respuesta válida, por favor ingrésala nuevamente. En caso de tener alguna duda, por favor lee los términos y condiciones.')

if __name__ == '__main__':
    app.run(debug=True)