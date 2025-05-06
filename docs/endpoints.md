The endpoints are listed below in the order they might be triggered during the usual user journey through the application. 

## `/fetch_all_data`

- Method: GET
- Description: Loads the results page for the provided address.
    - Results are displayed if and only if the following conditions are satisfied:
        - `usaddress` or `postal` is able to successfully parse the address to produce a cleaned address
        - We are able to successfully geocode the address and determine from the geocoding that the address is within the bounds of Hyde Park
    - If the above conditions fail, then we put an error message in front of the user to re-enter the address.
- Response Format: HTML (Rendered Template)
- Template Context:

```python
{
	"cleaned_address": String,    
	"property_id": String,
	"address_geojson": {
		"type": "FeatureCollection",
		"features": [
			{
				"type": "Feature",
				"geometry": {
					"type": "Point",
					"coordinates": [lon, lat]
				},
				"properties": {
					"label": String  # e.g., "123 Main St"
				}
			}
		]
	}
}
```

Frontend behavior:

- Should trigger requests to get the data to display on this page:
    - `/fetch_inspections/?address=...`
    - `/fetch_bus_stops/?geocode=...`
    - `/fetch_grocery/?geocode=...`
- User interaction, such as setting the walking time will re-trigger the requests to the endpoints listed above.

Backend behavior:

- In addition to returning the template, geocoding and cleaned address string, this endpoint also marks the beginning of our caching strategy. The endpoint will also return a `property_id`.
    - Once we have validated the user's address, we will store the address and geocoding in our `properties` table. The primary key for this table will serve as the `property_id`.
        - Validation means that we were able to generate a clean address string and the geocoding lies within the boundaries of Hyde Park.

## `/fetch_inspections`

- Method: GET
- Description: Fetches building inspection records for a given address or location.
- Response Format: JSON
- Query Parameters:
    - `address`: Cleaned address string
    - `property_id`: Unique property ID created by the server and returned by `fetch_all_data`
- Example return:

```python
{
	"inspections": [
		{
			"inspection_id": String,  # Unique identifier for each inspection record
			"inspection_date": Date,  # Date of the inspection
			"inspection_type": String,  # Type of inspection 
			"status": String,  # Status of the inspection 
			"violations": [
				{
					"violation_id": String,  # Unique identifier for each violation
					"description": String,  # Description of the violation
					"severity": String,  # Severity of the violation (e.g., Critical, Minor, etc.)
				}
			],
			"notes": String,  # Any additional notes
		}
	],
	"total_inspections_count": Integer  # Total number of inspections for the given address
}
```

Note that in practice, the endpoint will look something like this: `/fetch_inspections/?address=123+Main+St`. Then in Django, we will extract the address like this: `address = request.POST.get('address')` 

On the backend this endpoint will also update the `properties` table, which serves as our cache. The `properties` table will have columns that will store the inspections data being returned by this endpoint. 

## `/fetch_groceries`

- Method: GET
- Description: Returns a list of nearby grocery stores within a specified walking distance from the user's address.
- Response format: GEOJSON
- Query Parameters:
    - `geocode`: Geocoding (coordinates) of the apartment being searched
    - `property_id`: Unique property ID created by the server and returned by `fetch_all_data`
    - `walking_time`: The maximum walking time (in minutes) from the given address to the grocery stores. Default will be 5 minutes.
- Example return:

```python
{
  "address": "123 Main St",  # cleaned address
  "walking_time": 5,         # default parameter
  "grocery_geojson": {       # geojson of grocery stores
    "type": "FeatureCollection",
    "features": [
      {
        "type": "Feature",
        "geometry": {
          "type": "Point",
          "coordinates": [-97.7431, 30.2672]   # [longitude, latitude]
        },
        "properties": {
          "name": String, # ame of the retailer, e.g., "Whole Foods"
          "distance_min": Integer, # Walking distance in minutes
          "address": String # e.g., "789 Oak St, Chicago, IL"
        }
      },
      {
        "type": "Feature",
        "geometry": {
          "type": "Point",
          "coordinates": [-97.7448, 30.2691]
        },
        "properties": {
          "name": String,
          "distance_min": Integer,
          "address": String 
        }
      }
    ]
  }
}

```

A request will look like this:

`/fetch_groceries/?geocode=30.2672,-97.7431&property_id=123&walking_time=5`

On the backend this endpoint will also update the `properties` table, which serves as our cache. The `properties` table will have columns that will store the groceries data being returned by this endpoint. 

## `/fetch_bus_stops`

- Method: GET
- Description: Returns bus stops within walking distance of the provided address.
- Response Format: GEOJSON
- Query Parameters:
    - `geocode`: Geocoding (coordinates) of the apartment being searched
    - `property_id`: Unique property ID created by the server and returned by `fetch_all_data`
    - `walking_time`: The maximum walking time (in minutes) from the given address to the grocery stores. Default will be 5 minutes.
- Example return:

```python
{
	"address": "123 Main St",  # cleaned address
	"walking_time": 5,         # default parameter
	"bus_stops_geojson": {     # geojson of bus stops
		"type": "FeatureCollection",
		"features": [
			{
				"type": "Feature",
				"geometry": {
					"type": "Point",
					"coordinates": [-97.7425, 30.2675]
				},
				"properties": {
					"stop_name": String, # e.g., "Main St & 1st Ave",
					"distance_min": Integer,
					"routes": List # e.g., ["7", "20", "45"],  # list of route numbers
					"stop_id": String # CTA ID, e.g., "BUS12345"
				}
			}
		]
	}
}
```

A request will look like this:

`/fetch_bus_stops/?geocode=30.2672,-97.7431&property_id=123&walking_time=5`

On the backend this endpoint will also update the `properties` table, which serves as our cache. The `properties` table will have columns that will store the bus stops data being returned by this endpoint. 

Note: the backend will only return the nearest stop within the walking distance that has a new transportation mode (different bus route, shuttle, train) as a point.

## `/save_property`

- Method: POST
- Description: Saves a property and user-provided remarks from the user favorites table.
- Response Format: HTML or JSON (TBD)
- Query Parameters:
    - `user_id`: The user ID
    - `property_id`: Unique property ID created by the server and returned by `fetch_all_data`
    - `remarks`: String
    - `price`: Float
- Template Context (on successful save)

```python
{
	"save_success": Boolean,
	"message": String, # e.g., "Property saved successfully."
}
```

Note that this endpoint is only accessible when the user is logged in. 

## `/delete_property`

- Method: DELETE
- Description: Deletes a property and user-provided remarks froom the user favorites table.
- Response Format: HTML or JSON (TBD)
- Query Parameters:
    - `user_id`: The user ID
    - `property_id`: Unique property ID created by the server and returned by `fetch_all_data`
- Template Context (on successful save)

```python
{
	"save_success": Boolean,
	"message": String # "Property saved successfully."
}
```

Note that this endpoint is only accessible when the user is logged in. It will delete the favorited property from the `favorite_properties` table.

## `/saved_properties`

- Method: GET
- Description: Displays all properties saved by the user, with summaries for inspections, nearby bus stops, and grocery stores.
- Response Format: HTML (Rendered Template)
- Query Parameters:
    - `user_id`: The user ID
- Template Context:

```python
{
	"saved_properties": [
		{
			"address": "123 Main St",
			"remarks": "Near TJs",
			"inspections_summary": {
				"num_inspections": 3,
				"latest_violation": "Pest control issue on 2023-08-14",
				"has_critical_violations": true
			},
			"bus_stops_by_time": {
				"5": ["Stop A", "Stop B"],  # Stops within 5 minutes walk
				"10": ["Stop A", "Stop B", "Stop C", "Stop D"],  # Stops within 10 minutes walk
				"15": ["Stop A", "Stop B", "Stop C", "Stop D", "Stop E"]  # Stops within 15 minutes walk
			},
			"grocery_stores_by_time": {
				"5": ["Trader Joe’s"],  # Stores within 5 minutes
				"10": ["Trader Joe’s", "HPP"],  # Stores within 10 minutes
				"15": ["Trader Joe’s", "HPP", "Whole Foods"]  # Stores within 15 minutes
			}
		},
		{
			"address": "456 Elm St",
			"remarks": "Quiet street",
			"inspections_summary": {
				"num_inspections": 1,
				"latest_violation": "Unclean hallway on 2024-05-09",
				"has_critical_violations": false
			},
			"bus_stops_by_time": {
				"5": ["Stop F"],  # Stops within 5 minutes walk
				"10": ["Stop F", "Stop G"],  # Stops within 10 minutes walk
				"15": ["Stop F", "Stop G", "Stop H"]  # Stops within 15 minutes walk
			},
			"grocery_stores_by_time": {
				"5": [],  # No stores within 5 minutes
				"10": ["HPP"],  # Stores within 10 minutes
				"15": ["HPP", "Trader Joe’s"]  # Stores within 15 minutes
			}
		}
	]
}
```

Note: this will require authentication and in the longer term include client-side caching

## `/fetch_bus_routes`

- Method: GET
- Description: Returns the geojson for the relevant bus routes. This GEOJSON will be used by maplibre to plot the bus route (not stop).
- Response Format: GEOJSON
- Arguments:
    - `bus_route`: String (6, 172, Regents Park Express, etc.)
- Response:

```python
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {
        "route_number": "6",
        "route_name": "Route 6",
        "color": "#FF5733"
      },
      "geometry": {
        "type": "LineString",
        "coordinates": [
          [-97.7431, 30.2672],
          [-97.7448, 30.2691],
          [-97.7460, 30.2700]
        ]
      }
    },
    {
      "type": "Feature",
      "properties": {
        "route_number": "172",
        "route_name": "Route 172",
        "color": "#33FF57"
      },
      "geometry": {
        "type": "LineString",
        "coordinates": [
          [-97.7448, 30.2691],
          [-97.7465, 30.2705],
          [-97.7480, 30.2720]
        ]
      }
    }
  ]
}
```