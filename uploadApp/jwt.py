import datetime
import sys

from datetime import datetime
from datetime import timedelta

from builtins import bytes
import base64
from datetime import datetime, timedelta
import json
# from lib2to3.pgen2.token import NEWLINE
import ast

from django.db import connections

from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto import Random

"""def generate_sec_token(userid):
    access_token=''
    # datetime object containing current date and time
    now = datetime.now()
    try:



    except:
        pass
    return access_token
    """


def aes(secret_key, msg_text, encrypt=True):
    """_summary_

    Args:
        secret_key (_type_): _description_
        msg_text (_type_): _description_
        encrypt (bool, optional): _description_. Defaults to True.

    Returns:
        _type_: _description_
    """
    # an AES key must be either 16, 24, or 32 bytes long
    # in this case we make sure the key is 32 bytes long by adding padding and/or slicing if necessary
    remainder = len(secret_key) % 16
    modified_key = secret_key.ljust(len(secret_key) + (16 - remainder))[:32]
    # print(modified_key)

    # input strings must be a multiple of 16 in length
    # we achieve this by adding padding if necessary
    remainder = len(msg_text) % 16
    modified_text = msg_text.ljust(len(msg_text) + (16 - remainder))

    cipher = AES.new(modified_key, AES.MODE_ECB)  # use of ECB mode in enterprise environments is very much frowned upon

    if encrypt:
        return base64.b64encode(cipher.encrypt(modified_text)).strip()

    return cipher.decrypt(base64.b64decode(modified_text)).strip()


def jwt_token_refresh(sec_key, user_id, exp_minutes):
    """_summary_

    Args:
        sec_key (_type_): _description_
        user_id (_type_): _description_
        exp_minutes (_type_): _description_

    Returns:
        _type_: _description_
    """
    header = {'alg': 'aes', 'typ': 'jwt'}
    payload = {"uid": user_id,
               "iat": str(int(datetime.now().timestamp())),
               "exp": str(int((datetime.now() + timedelta(hours=0, minutes=exp_minutes)).timestamp()))
               }
    header_part = json.dumps(header)

    payload_part = json.dumps(payload)

    header_part_encrypted = aes(bytes(sec_key, encoding='ascii'),
                                base64.b64encode(bytes(header_part, encoding='ascii')), True).decode('UTF-8')

    payload_part_encrypted = aes(bytes(sec_key, encoding='ascii'),
                                 base64.b64encode(bytes(payload_part, encoding='ascii')), True).decode('UTF-8')
    signature_encrypted = aes(bytes(sec_key, encoding='ascii'),
                              base64.b64encode(bytes(header_part + '.' + payload_part, encoding='ascii')), True).decode(
        'UTF-8')

    jwt_token = header_part_encrypted + '.' + payload_part_encrypted + '.' + signature_encrypted

    return jwt_token


def create_jwt_token(sec_key, payload, exp_minutes):
    """_summary_

    Args:
        payload: The information that needs to be encoded.
        sec_key (_type_): _description_
        user_id (_type_): _description_
        exp_minutes (_type_): _description_

    Returns:
        _type_: _description_
    """
    header = {'alg': 'aes', 'typ': 'jwt'}
    payload = {**payload,
               "iat": str(int(datetime.now().timestamp())),
               "exp": str(int((datetime.now() + timedelta(hours=0, minutes=exp_minutes)).timestamp()))
               }
    print('new payload', payload)
    header_part = json.dumps(header)

    payload_part = json.dumps(payload)

    header_part_encrypted = aes(bytes(sec_key, encoding='ascii'),
                                base64.b64encode(bytes(header_part, encoding='ascii')), True).decode('UTF-8')

    payload_part_encrypted = aes(bytes(sec_key, encoding='ascii'),
                                 base64.b64encode(bytes(payload_part, encoding='ascii')), True).decode('UTF-8')
    signature_encrypted = aes(bytes(sec_key, encoding='ascii'),
                              base64.b64encode(bytes(header_part + '.' + payload_part, encoding='ascii')), True).decode(
        'UTF-8')

    jwt = header_part_encrypted + '.' + payload_part_encrypted + '.' + signature_encrypted
    return jwt

# def decode_jwt_token_and_return_validity(sec_key, token, exp_minutes):
#     """_summary_
#
#     Args:
#         sec_key (_type_): _description_
#         token (_type_): _description_
#         exp_minutes (_type_): _description_
#
#     Returns:
#         _type_: _description_
#     """
#     jwt_token_dict = {}
#     jwt_parts = token.split('.')
#
#     header_part = aes(bytes(sec_key, encoding='ascii'), bytes(jwt_parts[0], encoding='ascii'), encrypt=False).decode(
#         'UTF-8')
#     payload_part = aes(bytes(sec_key, encoding='ascii'), bytes(jwt_parts[1], encoding='ascii'), encrypt=False).decode(
#         'UTF-8')
#     signatue_part = aes(bytes(sec_key, encoding='ascii'), bytes(jwt_parts[2], encoding='ascii'), encrypt=False).decode(
#         'UTF-8')
#     hp = base64.b64decode(header_part).decode('UTF-8')
#     pl = base64.b64decode(payload_part).decode('UTF-8')
#     sgn = base64.b64decode(signatue_part).decode('UTF-8')
#     return is_valid_token(hp, pl, sgn, exp_minutes)


def decode_jwt_token_and_return_validity(sec_key, token, exp_minutes):
    """_summary_

    Args:
        sec_key (_type_): _description_
        token (_type_): _description_
        exp_minutes (_type_): _description_

    Returns:
        _type_: _description_
    """
    jwt_token_dict = {}
    jwt_parts = token.split('.')

    if len(jwt_parts) < 3:
        return {"message": "Invalid token", "status_code": 401, "success": False, "payload": None}
    else:
        try:
            header_part = aes(bytes(sec_key, encoding='ascii'), bytes(jwt_parts[0], encoding='ascii'),
                              encrypt=False).decode('UTF-8')
            payload_part = aes(bytes(sec_key, encoding='ascii'), bytes(jwt_parts[1], encoding='ascii'),
                               encrypt=False).decode('UTF-8')
            signatue_part = aes(bytes(sec_key, encoding='ascii'), bytes(jwt_parts[2], encoding='ascii'),
                                encrypt=False).decode('UTF-8')
            hp = base64.b64decode(header_part).decode('UTF-8')
            pl = base64.b64decode(payload_part).decode('UTF-8')
            sgn = base64.b64decode(signatue_part).decode('UTF-8')

            return is_valid_token(hp, pl, sgn, exp_minutes)
        except ValueError as error:
            return {"message": "Malformed token", "status_code": 401, "success": False, "payload": None}


def is_valid_token(header_part, payload_part, signatue_part, exp_minutes=None):
    """_summary_

    Args:
        header_part (_type_): _description_
        payload_part (_type_): _description_
        signatue_part (_type_): _description_
        exp_minutes (_type_): _description_

    Returns:
        _type_: _description_
    """

    hp = ast.literal_eval(header_part)

    pl = ast.literal_eval(payload_part)

    sgn = ast.literal_eval(signatue_part.replace('.', ','))

    validity = 'Valid'
    status_code = 200
    success = True

    try:
        if hp["alg"] != 'aes' or hp["typ"] != 'jwt':
            validity = "Invalid"
            status_code = 401
            success = False
        elif sgn[1]["email"].replace(',', '.') != pl["email"] or sgn[1]["uid"] != pl["uid"] \
                or sgn[1]["iat"] != pl["iat"] or sgn[1]["exp"] != pl["exp"]:
            validity = "Invalid"
            status_code = 401
            success = False
        else:

            iat = int(pl["iat"])
            exp = int(pl["exp"])
            dt = datetime.now()

            # getting the timestamp
            ts = datetime.timestamp(dt)

            seconds = int(exp) - int(ts)
            if seconds < 0:
                validity = 'Expired'
                status_code = 400
                success = False
    except (ValueError, KeyError, RuntimeError) as error:
        validity = 'Invalid'
        status_code = 401
        success = False

    if success is False:
        pl = None
    return {"message": validity, "status_code": status_code, "success": success, "payload": pl}


def log_errordata(exeption, user_logged):
    exception_type, exception_object, exception_traceback = sys.exc_info()
    filename = exception_traceback.tb_frame.f_code.co_filename
    line_number = exception_traceback.tb_lineno
    line_no = str(line_number)

    log_data = filename + ' - ' + line_no
    remarks = exeption.__str__()
    user_logged = user_logged
    logged_userid = str(user_logged)
    try:
        dbConnection = connections['default'].cursor()
        dbConnection.execute("select udf_add_policy_event_log(%s,%s,%s);", (log_data, logged_userid, remarks,))
        dbConnection.commit()
        dbConnection.close()
    except:
        pass


"""        
def generate_jwt_token(userid):
    access_token=''
    try:
        access_token_payload = {
            'user_id': userid,
            'exp': datetime.utcnow() + timedelta(days=0, minutes=2),
            'iat': datetime.utcnow(),
        }

        access_token = jwt.encode(access_token_payload,
                              settings.SECRET_KEY,  algorithm='HS256').decode('utf-8')
    except Exception as e:
            print(e)
            print("Exception in token generation")
    return access_token

def refresh_jwt_token(userid):

    refresh_token_payload = {
        'user_id': userid,
        'exp': datetime.utcnow() + timedelta(minutes=5),
        'iat': datetime.utcnow()
    }
    refresh_token = jwt.encode(
        refresh_token_payload,  settings.SECRET_KEY, algorithm='HS256').decode('utf-8')

    return refresh_token
def is_validtoken(token):
    tk= token.replace('Bearer ','')
    #print(tk,"********")

    if len(tk)%4==3:
           token=token+'000' 
    elif len(tk)%4==2:
        token=token+'00'
    elif len(tk)%4==1:
            token=token+'0'
    valid=True
    try:
        #access_token_json = jwt.decode(token, settings.SECRET_KEY)
        access_token=jwt.decode(tk, settings.SECRET_KEY, algorithm=["HS256"])

        if valid==True:
            #print(type(access_token['exp']),type(access_token['iat']))
            token_date = datetime.datetime.fromtimestamp(access_token['exp'])
            current_date=datetime.datetime.now()
            time_diff=token_date-current_date

            #print(time_diff.seconds,"    ********")
            valid="Ok"
    except Exception as e:
        #print(e,"===========================")
        #print(e,"algorithm error")
        #print "Not working using PEM key with ----: ", e
        valid="Invalid Token"


    return valid

"""
"""
def validate_jwt(token):
    if len(token)%4==3:
       token=token+'000' 
    elif len(token)%4==2:
        token=token+'00'
    elif len(token)%4==1:
            token=token+'0'
    access_token_json = jwt.decode(token, verify=False)
    #algo = HMACAlgorithm(HMACAlgorithm.HS)
    algo=HMACAlgorithm(HMACAlgorithm.SHA256)
    shakey = algo.prepare_key(settings.SECRET_KEY)
    #testtoken = jwt.encode(access_token_json, key=shakey, algorithm='HS256')
    options={'verify_exp': True,  # Skipping expiration date check
         'verify_aud': True } # Skipping audience check
    valid=True
    try:
        jwt.decode(token, key=shakey, options=options)
    except Exception as e:
        print(e)
        #print "Not working using PEM key with ----: ", e
        valid=False
    return valid
    """


def create_jwt_token(sec_key, user_id, exp_minutes):
    """_summary_

    Args:
        sec_key (_type_): _description_
        user_id (_type_): _description_
        exp_minutes (_type_): _description_

    Returns:
        _type_: _description_
    """
    header = {'alg': 'aes', 'typ': 'jwt'}
    payload = {"uid": user_id,
               "iat": str(int(datetime.now().timestamp())),
               "exp": str(int((datetime.now() + timedelta(hours=0, minutes=exp_minutes)).timestamp()))
               }
    header_part = json.dumps(header)

    payload_part = json.dumps(payload)

    header_part_encrypted = aes(bytes(sec_key, encoding='ascii'),
                                base64.b64encode(bytes(header_part, encoding='ascii')), True).decode('UTF-8')

    payload_part_encrypted = aes(bytes(sec_key, encoding='ascii'),
                                 base64.b64encode(bytes(payload_part, encoding='ascii')), True).decode('UTF-8')
    signature_encrypted = aes(bytes(sec_key, encoding='ascii'),
                              base64.b64encode(bytes(header_part + '.' + payload_part, encoding='ascii')), True).decode(
        'UTF-8')

    jwt = header_part_encrypted + '.' + payload_part_encrypted + '.' + signature_encrypted
    return jwt



def create_jwt_token(sec_key, payload, exp_minutes):
    """_summary_

    Args:
        payload: The information that needs to be encoded.
        sec_key (_type_): _description_
        user_id (_type_): _description_
        exp_minutes (_type_): _description_

    Returns:
        _type_: _description_
    """
    header = {'alg': 'aes', 'typ': 'jwt'}
    payload = {**payload,
               "iat": str(int(datetime.now().timestamp())),
               "exp": str(int((datetime.now() + timedelta(hours=0, minutes=exp_minutes)).timestamp()))
               }
    print('new payload', payload)
    header_part = json.dumps(header)

    payload_part = json.dumps(payload)

    header_part_encrypted = aes(bytes(sec_key, encoding='ascii'),
                                base64.b64encode(bytes(header_part, encoding='ascii')), True).decode('UTF-8')

    payload_part_encrypted = aes(bytes(sec_key, encoding='ascii'),
                                 base64.b64encode(bytes(payload_part, encoding='ascii')), True).decode('UTF-8')
    signature_encrypted = aes(bytes(sec_key, encoding='ascii'),
                              base64.b64encode(bytes(header_part + '.' + payload_part, encoding='ascii')), True).decode(
        'UTF-8')

    jwt = header_part_encrypted + '.' + payload_part_encrypted + '.' + signature_encrypted
    return jwt
