# calendari idescat un cop per setmana al correu de la gene

# Tutorials used: 
# how to schedule an email -  https://www.youtube.com/watch?v=OLrC4J2-pvk&ab_channel=CodingIsFun
# Creating app password for gmail - https://www.youtube.com/watch?v=TIrxdCO587U&ab_channel=BeyondKareers
# suggestions vscode - https://www.reddit.com/r/vscode/comments/1dfsizc/how_to_disable_autocompletion_hints/
# sending emails in python - https://www.youtube.com/watch?v=QJobMzcmoMo&t=293s&ab_channel=Hackr


# IMPORTEM LLIBRERIES

import pandas as pd
import os
import numpy as np
import requests
import json
from datetime import date
# from google import genai
import schedule
from datetime import datetime, timedelta
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import schedule
from dotenv import load_dotenv
import locale # per rebre la notificació en català
from email.utils import COMMASPACE



# PETICIÓ API IDESCAT ############################################################################

# format = 	https://api.idescat.cat/cal/v1/{operació}.{format}[?paràmetres]
today = date.today()

# 1. FUNCIO SETMANA IDESCAT
# 

def setmanes_idescat(today):
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)
    monday_idescat = monday.strftime("%Y%m%d")
    sunday_idescat = sunday.strftime("%Y%m%d")
    return monday_idescat, sunday_idescat

monday_idescat, sunday_idescat = setmanes_idescat(today)

##############################

# 2. FUNCIÓ VISUALITZACIÓ JSON:


def json_print (json_data, limit = None):

  # *isinstance* - The isinstance() function returns True if the specified object
  # is of the specified type, otherwise False.
  # If the type parameter is a tuple, this function will return True
  # if the object is one of the types in the tuple.


    if isinstance(json_data, (str)): # si json_data és type string

    # *json.loads*  - json.loads() method can be used to parse a valid JSON
    # string and convert it into a Python Dictionary.
        json_data = json.loads(json_data)

        # * json.dumps* - If you have a Python object, you can convert it into a JSON string by using the json.dumps() method.
    nice = json.dumps(json_data, sort_keys=True, indent=3, separators=(',', ': '))
    print("\n".join(nice.split("\n")[0:limit]))
    if limit is not None:
        print("[...]")

##############################

# 3. REQUESTS API IDESCAT AMB DUES FUNCIONS;
    # a. requests dades
    # b. request nodes

# creo una funció per extreure les dades i els nodes (perquè per la descripció de l'idescat no entenc la diferència)

def nodes_calendari_idescat(monday_idescat, sunday_idescat):
    response = requests.get(f"https://api.idescat.cat/cal/v1/nodes.json?t={monday_idescat}-{sunday_idescat}") 

    # llista buida per guardar resposta
    esdeveniments_setmana = []

    #condicional per la resposta de la petició
    if response.status_code == 200:
        headers = response.headers
        nodes = json.loads(response.text)
        print(headers)
        json_print(nodes)
    else:
        print(f"Error: {response.status_code}")
        return None
#########################################################
# prova nova funció idescat setmana
def dades_calendari_idescat(monday_idescat, sunday_idescat):
    ''' 
    Aquesta funció agafa les dades de l'API d'idescat i em retorna una llista
    amb quins elements es faran públics aquesta setmana.
    
    '''
    url = f"https://api.idescat.cat/cal/v1/dades.json?t={monday_idescat}-{sunday_idescat}"
    print(f"Petició de dades a {url}")

    idescat_setmana = [] #llista buida on incloure els esdeveniments setmanals
    current_locale = locale.getlocale(locale.LC_TIME) # per rebre els dies de la setmana en català

    try:
        # Set locale to Catalan for date formatting.
        # 'ca_ES.UTF-8' is a common locale for Catalan in Spain on Unix-like systems.
        # On Windows, it might be 'ca_ES' or 'Catalan_Spain.1252'.
        # Using '' tells Python to use the user's default locale.
        # For explicit Catalan, 'ca_ES.UTF-8' is usually the best bet.
        try:
            locale.setlocale(locale.LC_TIME, 'ca_ES.UTF-8')
        except locale.Error:
            print("Warning: Could not set locale to 'ca_ES.UTF-8'. Trying 'ca_ES'...")
            try:
                locale.setlocale(locale.LC_TIME, 'ca_ES')
            except locale.Error:
                print("Warning: Could not set locale to 'ca_ES'. Date formatting might not be in Catalan.")
                # Fallback to system default if explicit Catalan fails
                locale.setlocale(locale.LC_TIME, '')


        response = requests.get(url)
        response.raise_for_status()# inclou missatges en cas de no poder accedir a la petició

        events_data = json.loads(response.text)
        events = events_data.get('vevent')

        if events: # en cas que "vevent" existeixi
            for e in events:
                description = e.get('description')
                dtstart_str = e.get("dtstart") # el format d'això serà "20250612" , s'haurà de canviar

                if description and dtstart_str: # si els dos elements existeixen:
                    try:
                        dt_object = datetime.strptime(dtstart_str, "%Y%m%d") # canvio format de setmana en la següent linia
                        formatted_date = dt_object.strftime("%A, %B %d, %Y")

                        # append a la llista la informació i la data d 'aquesta
                        idescat_setmana.append(f"- {description} on {formatted_date}")
                    except ValueError:
                        print(f"Warning: Could not parse date string '{dtstart_str}' for event '{description}'.")
                        idescat_setmana.append(f"- {description} (Invalid Date Format: {dtstart_str})")
                elif description:
                    # Si només hi ha descripció però no hi ha data
                    idescat_setmana.append(f"- {description} (No Date Provided)")
                else:
                    print("S'ha trobat esdeveniment sense descripció o data")
            if not idescat_setmana: # si no hi ha esdeveniments aquella setmana
                idescat_setmana.append("No s'han trobat esdeveniments per aquesta setmana")
        else:
            idescat_setmana.append("No s'han trobat esdeveniments per aquesta setmana")

    except requests.exceptions.RequestException as e:
        print(f"Error amb la petició de l'API d'idescat per dades: {e}")
        print(f"Contingut de resposta: {response.text if 'resposta' in locals() else 'sense resposta'}")
        return None
    except json.JSONDecodeError:
        print("Error: No s'ha pogut descodificar la resposta JSON de ""dades"". ")
        print(f"Resposta: {response.text}")
        return None
    except Exception as e:
        print(f"Error inesperat mentre es processaven les dades_calendari_idescat: {e}")
        return None

    return idescat_setmana




#####################################################################################################

### PART 2  # ENVIAR AL MAIL SETMANAL CADA DILLUNS AL MATÍ


load_dotenv()  # Load environment variables from .env file
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587  # TLS/STARTTLS
EMAIL_ADDRESS = os.getenv("EMAIL")
EMAIL_PASSWORD = os.getenv("PASSWORD") # Use environment variable or replace with your app password

# Llista de persones que rebran el mail:
# NEW: Get recipients from .env and split them into a list
RECIPIENT_EMAILS_STR = os.getenv("RECIPIENTS")
if RECIPIENT_EMAILS_STR:
    RECIPIENTS = [email.strip() for email in RECIPIENT_EMAILS_STR.split(',')]
else:
    RECIPIENTS = [] # Or handle as an error if recipients are mandatory


def send_email (recipient_emails, subject, body):
    '''
    Envia un mail amb la informació de les publicacions d'aquesta setmana de l'idescat a una o més persones

    Args:
    recipient -  llista de persones que rebran el missatge
    subject -  titol
    body -  llista amb els esdeveniments d'idescat d'aquesta setmana
    '''

    # Ensure recipient_emails is a list
    if not isinstance(recipient_emails, list):
        recipient_emails = [recipient_emails] 

    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        # els recipient emails han d'estar separats per una coma
        msg['To'] = COMMASPACE.join(recipient_emails)
        msg['Subject'] = subject

        msg.attach(MIMEText(body,'plain'))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls() # secured connection
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD) # securily loging in
            server.sendmail (EMAIL_ADDRESS, recipient_emails, msg.as_string())

        print(f"Email sent successfully to {recipient_emails}")

    except Exception as e:
        print(f"Error sending email: {e}")

# why we use if__name__ = __main__ - https://www.youtube.com/watch?v=o4XveLyI6YU&ab_channel=b001

if __name__ == "__main__":

    # Setmana (per incorporar a l'assumpte):
    today = date.today()
    monday_str, sunday_str = setmanes_idescat(today)
    print(f"Determined week: {monday_str} to {sunday_str}")

    # Cridem la funció per agafar el calendari de la setmana
    dades_body = dades_calendari_idescat(monday_str, sunday_str)

    if dades_body is not None:

        # 
        recipients = ["berta.llugany@gmail.com", "bertallugany@gencat.cat","mmulet94@gmail.com", "oleguer.gabernet@gmail.com"]
        subject= f"Publicacions Idescat de la setmana del {monday_str} al {sunday_str}(test)"

    # Formategem el llistat que obtenim a dades_body perquè quedi un contingut coherent:

        email_body_lines = ["Hola!",
                            "\nA continuació trobaràs els esdeveniments del calendari de l'Idescat per a aquesta setmana:",
                            ""]
        email_body_lines.extend(dades_body)
        email_body_lines.append("\nEspereo que aquesta informació et sigui útil!")
        email_body_lines.append("\nSalutacions,")
        email_body_lines.append("Berta")

        email_body = "\n".join(email_body_lines)

        # Pass the RECIPIENTS list to the send_email function
        if RECIPIENTS: # Only try to send if there are recipients
             # Enviem el mail
            send_email(RECIPIENTS, subject, email_body)
        else:
            print("Error: No recipients found in .env file. Email not sent.")

              
    else:
        print("Error obtenint els esdeveniments de la setmana de l'API d'Idescat. El mail no ha estat enviat")

    print("Execució finalitzada.")


