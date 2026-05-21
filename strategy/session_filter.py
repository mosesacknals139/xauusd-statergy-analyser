from datetime import datetime

def allowed_session():

    hour = datetime.utcnow().hour

    # London + New York
    if 7 <= hour <= 20:
        return True

    return False