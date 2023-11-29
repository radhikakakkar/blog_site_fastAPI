import time
import jwt
import os
from dotenv import load_dotenv
from fastapi import HTTPException, Header, Request

load_dotenv()

config = os.environ

JWT_SECRET = config.get("secret")
JWT_ALGORITHM = config.get("algorithm")


def token_response(token):
    return {"access token": token}


def signJWT(userID: str):
    payload = {"userId": userID, "expiry": time.time() + 600}
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return token_response(token)


def decodeJWT(token: str):
    try:
        decode_token = jwt.decode(token, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return decode_token if decode_token["expires"] >= time.time() else None
    except:
        return {}


def verify_jwt(request: Request, Authorization: str = Header(...)):
    if not Authorization:
        raise HTTPException(status_code=401, detail="Authorization header is missing")

    try:
        token = Authorization.split(" ")[1]
        decoded_token = jwt.decode(token, JWT_SECRET, JWT_ALGORITHM)
        user_id: str = decoded_token.get("userId", None)

        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        # //how do i return the email decoded here to in the response body of the request which depends on verify_jwt
    except jwt.exceptions.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")

    except jwt.exceptions.DecodeError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")

    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Error decoding token: {e}")

    request.state.user_id = user_id
    return user_id
