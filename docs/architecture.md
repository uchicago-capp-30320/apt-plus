Apartments Plus is a single page app with most functionality run through a backend. The technology stack is as follows:

- Database: postgreSQL and postGIS
- Backend: Django
- Frontend: Alpine.js (UI logic) and HTMX (requests)
- Mapping: MapLibre (interactive maps, layers)
- CSS Styling: Bulma

Our current data flow uses static data, but we anticipate including a separate backend flow to regularly refresh commonly updated data such as building inspections.

## Core User flow

1. Users submit an address on the landing page, which triggers a GET request from the backend to receive information
    1. Data validation: the address is validated using (i) that the address is geocodable and (ii) within Hyde Park, our initial neighborhood.
    2. We return HTML for the frontend to render.
2. Once the map view loads, the rendered HTML includes a series of GET requests to load data onto the MapLibre screen that forms the core of the user experience.
    1. On the backend, we run a series of spatial queries to extract key amenities (grocery stores) and transit information, as well as collect municipal property information from the address.
    2. The frontend contains some modifications to visualize the data, but if core elements like the radius of amenities around the property changes, we request the API again.
3. Users can save properties to their user account (based on `django-allauth` user authentication flows).

In the future, we anticipate including a set of views that will allow users to compare saved properties.