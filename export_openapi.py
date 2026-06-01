# export_openapi.py
import json
import yaml
from main import app

openapi_schema = app.openapi()

with open("openapi.yaml", "w") as f:
    yaml.dump(openapi_schema, f, 
              allow_unicode=True, 
              sort_keys=False,
              default_flow_style=False)

print("openapi.yaml is generated!")