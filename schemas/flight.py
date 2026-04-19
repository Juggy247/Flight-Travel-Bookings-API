from pydantic import BaseModel, Field, StrictStr, model_validator, ConfigDict
from datetime import datetime

class Flight(BaseModel):
    name: str
    origin: StrictStr
    destination: StrictStr
    flight_number: str
    boarding_time: datetime
    price: float = Field(gt=0)
    seats: int = Field(gt=0)
    model_config = ConfigDict(from_attributes=True)
    
    #validate string fields 
    @model_validator(mode='before')
    @classmethod
    def no_numeric_strings(cls, values):
        #Check if values is a dict or not 
        if not isinstance(values, dict):
            values = vars(values)   #var() - python built in function return obj.__dict__
        for field in ['name', 'origin', 'destination','flight_number']:
            val = values.get(field)
            if isinstance(val,str):
                if val.strip() == "":
                    raise ValueError(f"{field} cannot be empty or whitespace")
                if val.strip().isdigit():
                    raise ValueError(f"{field} cannot be purely Numeric")
        return values

class FlightResponse(Flight):   #Inherits from Flight class
    id: int     #client will see it in GET responses

class FlightUpdate(BaseModel):
    name: StrictStr | None = None
    origin: StrictStr | None = None
    boarding_time: datetime | None = None
    destination: StrictStr | None = None 
    price: float | None = Field(default=None,gt=0) #gt=0 greater than 0, default - if user does not give input it become None
    seats: int | None = Field(default=None,gt=0)
    #Flight number do no change 