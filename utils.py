def success_response(message:str , data = None):
    response = {"status": "success", "message": message}

    if data is not None:
        response["data"] = data 
    return response

def error_response(message: str):
    return {"status": "error", "message": message}