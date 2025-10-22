from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from datetime import datetime
import hashlib

app = FastAPI(title = "String Analasys API")

@app.get("/")
def root():
    return {"message": "String Analysis API running"}


# Temporary in memoryu database
database = {}

class StringInput(BaseModel):
    value: str
    
def analyze_string(value: str):
    value_stripped = value.strip()
    lower_value = value_stripped.lower()
    
    #compute properties
    length = len(value_stripped)
    is_palindrome = lower_value == lower_value[::-1]
    unique_characters = len(set(value_stripped))
    word_count = len(value_stripped.split())
    sha256_hash = hashlib.sha256(value_stripped.encode()).hexdigest()
    
    #frequency map
    freq_map = {}
    for char in value_stripped:
        freq_map[char] = freq_map.get(char, 0) + 1
        
    return {
        "length": length, 
        "is_palindrome": is_palindrome,
        "unique_characters": unique_characters, 
        "word_count": word_count, 
        "sha256_hash": sha256_hash, 
        "character_frequency_map": freq_map,
    }
    
@app.post("/strings", status_code=201)
def create_string(data: StringInput):
    
    # 422 is automatically raised by FastAPI if value isn't a string, so i didnt have to handle it manually.

    
    if not isinstance(data.value, str) or data.value.strip() == "":
        raise HTTPException(status_code=400, detail="Invalid request body or missing 'value' field")
    
    analyzed = analyze_string(data.value)
    string_id = analyzed["sha256_hash"]
    
    if string_id in database:
        raise HTTPException(status_code=409, detail="String already exists")
    
    record = {
        "id" : string_id, 
        "value": data.value, 
        "properties": analyzed, 
        "created_at": datetime.utcnow().isoformat() + "Z"
    }
    
    database[string_id] = record
    return record
    
    
  # getting a specfic string  
@app.get("/strings/{string_value}")
def get_string(string_value: str):
    value_stripped = string_value.strip()
    string_hash = hashlib.sha256(value_stripped.encode()).hexdigest()
    
    # checking if it exists
    record = database.get(string_hash)
    if not record: 
        raise HTTPException(status_code=404, detail="String not found")
    
    return record

# getting strings with filtering
@app.get("/strings")
def get_all_strings(
    is_palindrome: bool | None = Query(None), 
    min_length: int | None = Query(None, ge=0), 
    max_length: int | None = Query(None, ge=0), 
    word_count: int | None = Query(None, ge=0), 
    contains_character: str | None = Query(None, min_length=1, max_length=1)

):
    try:
        filtered = []
        for record in database.values():
            props = record["properties"]
            value = record["value"]
            
            #to apply filters provided
            if is_palindrome is not None and props["is_palindrome"] != is_palindrome:
                continue
            if min_length is not None and props["length"] < min_length:
                continue
            if max_length is not None and props["length"] > max_length:
                continue
            if word_count is not None and props["word_count"] != word_count:
                continue
            if contains_character and contains_character not in value:
                continue
            
            filtered.append(record)
            
        filtrs_applied = {
            "is_palindrome": is_palindrome,
            "min_length": min_length,
            "max_length": max_length,
            "word_count": word_count,
            "contains_character": contains_character,
        }
        
        return {
            "data": filtered, 
            "count": len(filtered),
            "filters_applied": {k: v for k, v in filtrs_applied.items() if v is not None}
        }

    except ValueError:
        raise HTTPException(status_code = 400, detail= "Invalid query parameter values or types")
    
    
@app.delete("/strings/{string_value}", status_code=204)
def delete_string(string_value: str):
    value_stripped = string_value.strip()
    string_hash = hashlib.sha256(value_stripped.encode()).hexdigest()

    if string_hash not in database:
        raise HTTPException(status_code=404, detail="String does not exist in the system")

    del database[string_hash]
    return  # empty body per spec
