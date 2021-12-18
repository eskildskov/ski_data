#!/usr/bin/env python
# coding: utf-8

# In[8]:


import csv
import json
import re
import pandas as pd
import numpy as np
from pydantic import BaseModel, ValidationError
from typing import Optional, Any


# In[9]:


routes = pd.read_csv("Skiturer Sunnmøre - Turer.csv")


class Route(BaseModel):
    route_id: int
    mountain_name: str
    area: str
    route_name: str
    max_start_altitude: int
    avalanche_start_zones: list
    kast: int
    dangers: str
    exposure: str
    difficulty: str
    comment: str
    equipment: str
    max_steepness: Any
    is_descent: bool
    start_location: str
    altitude: int
    geoJSON: dict


columns = {
    "Fjell": "mountain_name",
    "Himmelretning (topp til bunn)": "aspect",
    "Område": "area",
    "Rute": "route_name",
    "Høyeste startsted": "max_start_altitude",
    "Løsneområder (obligatoriske)": "avalanche_start_zones",
    "KAST": "kast",
    "Terrengfeller/farer": "dangers",
    "Eksponering": "exposure",
    "Vanskelighetsgrad": "difficulty",
    "Kommentar": "comment",
    "Utstyr": "equipment",
    "Max bratthet": "max_steepness",
    "Primært nedkjøring?": "is_descent",
    "Startsted": "start_location",
    "Toppunkt": "altitude",
    "Hvem": "who",
}

routes = routes.rename(columns=columns)
routes = routes.drop(labels="who", axis="columns")
routes = routes.dropna(how="all", axis="columns")
routes = routes.fillna("")
routes["route_id"] = routes.index


# In[10]:


routes_dict = routes.to_dict(orient="records")

for route in routes_dict:
    for key, val in route.items():
        if val == "FALSE" or val == "USANN":
            route[key] = False

        if val == "TRUE" or val == "SANN":
            route[key] = True

    if route["avalanche_start_zones"] == False:
        route["avalanche_start_zones"] = []

    if route["geoJSON"]:
        route["geoJSON"] = json.loads(route["geoJSON"])

    if route["aspect"]:
        route["aspect"] = route["aspect"].split(" ")

    if route["avalanche_start_zones"]:
        elevation_spans = route["avalanche_start_zones"].replace(",", ".").split(".")
        elevation_spans = [tuple(span.strip().split(":")) for span in elevation_spans]
        route["avalanche_start_zones"] = elevation_spans


# In[11]:


valid_routes = []
invalid_count = 0
for route in routes_dict:
    try:
        r = Route(**route)
        valid_routes.append(route)
    except ValidationError as e:
        error_text = (
            f'{route["mountain_name"]} - {route["route_name"]}: \n'
            f"{e} \n"
            f"-------------"
        )
        invalid_count += 1
        print(error_text)


# In[12]:


invalid_count


# In[13]:


len(valid_routes)


# In[14]:


with open("routes.json", "w") as file:
    file.write(json.dumps(valid_routes))
valid_routes
