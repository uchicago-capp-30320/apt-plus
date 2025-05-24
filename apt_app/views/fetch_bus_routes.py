from django.core.serializers import serialize
from django.http import JsonResponse
from apt_app.models import TransitRoute
import json


def _get_hsl_colors(n):
    return [f"hsl({int(360 * i / n)}, 100%, 45%)" for i in range(n)]


def _assign_color(feature, route_color_map):
    feature["properties"]["color"] = route_color_map[feature["properties"]["route_id"]]
    return feature


def _parse_input_routes(in_routes: str) -> list:
    """
    Parse a common-seperated string of bus routes into list.
    e.g. "171,172,55" -> [171,172,55]
    """
    if in_routes.strip() == "":
        return []
    return [r.strip() for r in in_routes.split(",")]


def _fetch_bus_routes(routes: str):
    route_num_list = _parse_input_routes(routes)
    if not route_num_list:
        return JsonResponse({"error": "No valid input"}, status=400)
    try:
        routes_qs = TransitRoute.objects.filter(route_id__in=route_num_list)
        if not routes_qs:
            return JsonResponse({"error": "This route does not pass Hyde Park"}, status=400)
        routes_list = list(routes_qs)
    except TransitRoute.DoesNotExist as e:
        return JsonResponse({"error": f"This route does not pass Hyde Park: {e}"}, status=404)

    geojson = serialize(
        "geojson", routes_list, geometry_field="geometry", fields=("route_id", "name", "type")
    )
    data = json.loads(geojson)
    for feature in data["features"]:
        feature["properties"]["route_id"] = feature.pop("id")
    route_color_map = {
        rid: color for rid, color in zip(route_num_list, _get_hsl_colors(len(route_num_list)))
    }
    data["features"] = [_assign_color(f, route_color_map) for f in data["features"]]

    return JsonResponse(data)
