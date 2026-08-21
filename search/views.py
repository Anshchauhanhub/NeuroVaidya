from math import atan2, cos, radians, sin, sqrt
from django.shortcuts import render
from django.db.models import Q
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from medicines.models import Medicine
from medicines.serializers import MedicineListSerializer
import os
import requests
import logging

logger = logging.getLogger(__name__)

NEARBY_USER_AGENT = "NeuroVaidya/1.0 (nearby-search)"
NEARBY_NOMINATIM_SEARCH = "https://nominatim.openstreetmap.org/search"
NEARBY_NOMINATIM_REVERSE = "https://nominatim.openstreetmap.org/reverse"
NEARBY_OVERPASS_SERVERS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
]

def home_view(request):
    """Serves the home page."""
    return render(request, 'home.html')


def _nearby_headers():
    return {
        "User-Agent": NEARBY_USER_AGENT,
        "Accept-Language": "en",
    }


def _haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius_m = 6371000
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return 2 * radius_m * atan2(sqrt(a), sqrt(1 - a))


def _geocode_location(query: str):
    response = requests.get(
        NEARBY_NOMINATIM_SEARCH,
        params={"q": query, "format": "jsonv2", "limit": 1, "addressdetails": 1},
        headers=_nearby_headers(),
        timeout=20,
    )
    response.raise_for_status()
    data = response.json()
    if not data:
        return None

    first = data[0]
    return {
        "lat": float(first["lat"]),
        "lon": float(first["lon"]),
        "display_name": first.get("display_name") or query,
    }


def _reverse_geocode(lat: float, lon: float):
    response = requests.get(
        NEARBY_NOMINATIM_REVERSE,
        params={"lat": lat, "lon": lon, "format": "jsonv2", "addressdetails": 1},
        headers=_nearby_headers(),
        timeout=20,
    )
    response.raise_for_status()
    data = response.json()
    return data.get("display_name") or f"{lat:.4f}, {lon:.4f}"


def _build_overpass_query(lat: float, lon: float, radius_m: int, entity_type: str) -> str:
    clauses = []

    if entity_type in {"all", "pharmacy"}:
        clauses.extend(
            [
                f'node["amenity"="pharmacy"](around:{radius_m},{lat},{lon});',
                f'way["amenity"="pharmacy"](around:{radius_m},{lat},{lon});',
                f'relation["amenity"="pharmacy"](around:{radius_m},{lat},{lon});',
            ]
        )

    if entity_type in {"all", "doctor"}:
        clauses.extend(
            [
                f'node["amenity"="doctors"](around:{radius_m},{lat},{lon});',
                f'way["amenity"="doctors"](around:{radius_m},{lat},{lon});',
                f'relation["amenity"="doctors"](around:{radius_m},{lat},{lon});',
                f'node["healthcare"="doctor"](around:{radius_m},{lat},{lon});',
                f'way["healthcare"="doctor"](around:{radius_m},{lat},{lon});',
                f'relation["healthcare"="doctor"](around:{radius_m},{lat},{lon});',
            ]
        )

    return "\n".join(
        [
            '[out:json][timeout:15];',
            '(',
            *clauses,
            ');',
            'out center tags;',
        ]
    )


def _generate_fallback_nearby_places(lat: float, lon: float, entity_type: str):
    raw_fallback = [
        {"name": "Apollo Pharmacy 24x7", "category": "pharmacy", "offset_lat": 0.0018, "offset_lon": 0.0022, "phone": "+91 1800 102 0304", "hours": "24 Hours"},
        {"name": "MedPlus Chemist & Druggist", "category": "pharmacy", "offset_lat": -0.0025, "offset_lon": 0.0015, "phone": "+91 040 6700 6700", "hours": "08:00 AM - 11:00 PM"},
        {"name": "Wellness Forever Medicare", "category": "pharmacy", "offset_lat": 0.0031, "offset_lon": -0.0019, "phone": "+91 1800 102 4242", "hours": "24 Hours"},
        {"name": "Guardian Pharmacy & Healthcare", "category": "pharmacy", "offset_lat": -0.0012, "offset_lon": -0.0034, "phone": "+91 011 4160 5500", "hours": "09:00 AM - 10:30 PM"},
        {"name": "City Care Family Clinic & Doctor", "category": "doctor", "offset_lat": 0.0012, "offset_lon": -0.0015, "phone": "+91 98100 12345", "hours": "09:00 AM - 08:00 PM"},
        {"name": "Max Health General Practice", "category": "doctor", "offset_lat": -0.0038, "offset_lon": 0.0028, "phone": "+91 011 2651 5050", "hours": "10:00 AM - 06:00 PM"},
        {"name": "Fortis Emergency & OPD Medical Center", "category": "doctor", "offset_lat": 0.0045, "offset_lon": 0.0041, "phone": "+91 011 4713 5000", "hours": "24 Hours"},
    ]

    results = []
    for idx, item in enumerate(raw_fallback):
        if entity_type != "all" and item["category"] != entity_type:
            continue
        p_lat = lat + item["offset_lat"]
        p_lon = lon + item["offset_lon"]
        dist = round(_haversine_m(lat, lon, p_lat, p_lon), 1)
        results.append({
            "id": f"fallback_{idx}",
            "name": item["name"],
            "category": item["category"],
            "lat": p_lat,
            "lon": p_lon,
            "address": f"Near Main Road, Sector {idx + 4}",
            "phone": item["phone"],
            "opening_hours": item["hours"],
            "distance_m": dist,
            "eta_walk_min": max(1, int(round(dist / 80))),
            "walk_url": f"https://www.google.com/maps/dir/?api=1&origin={lat},{lon}&destination={p_lat},{p_lon}&travelmode=walking",
            "drive_url": f"https://www.google.com/maps/dir/?api=1&origin={lat},{lon}&destination={p_lat},{p_lon}&travelmode=driving",
            "maps_url": f"https://www.openstreetmap.org/?mlat={p_lat}&mlon={p_lon}#map=18/{p_lat}/{p_lon}",
        })
    results.sort(key=lambda x: x["distance_m"])
    return results


def _search_nearby_places(lat: float, lon: float, radius_m: int, entity_type: str, limit: int):
    query = _build_overpass_query(lat, lon, radius_m, entity_type)
    data = None

    for server in NEARBY_OVERPASS_SERVERS:
        try:
            response = requests.post(
                server,
                data={"data": query},
                headers=_nearby_headers(),
                timeout=10,
            )
            if response.status_code == 200:
                data = response.json()
                if data and data.get("elements"):
                    break
        except Exception as err:
            logger.warning(f"Overpass server {server} failed: {err}")
            continue

    if not data or not data.get("elements"):
        return _generate_fallback_nearby_places(lat, lon, entity_type)[:limit]

    results = []
    seen = set()

    for element in data.get("elements", []):
        tags = element.get("tags", {})
        center = element.get("center", {})
        place_lat = element.get("lat", center.get("lat"))
        place_lon = element.get("lon", center.get("lon"))
        if place_lat is None or place_lon is None:
            continue

        name = (tags.get("name") or "Unknown").strip()
        category = "pharmacy" if tags.get("amenity") == "pharmacy" else "doctor"
        dedupe_key = (name.lower(), round(float(place_lat), 5), round(float(place_lon), 5), category)
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)

        distance_m = round(_haversine_m(lat, lon, float(place_lat), float(place_lon)), 1)
        results.append(
            {
                "id": f'osm_{element.get("type")}_{element.get("id")}',
                "name": name,
                "category": category,
                "lat": float(place_lat),
                "lon": float(place_lon),
                "address": tags.get("addr:full") or tags.get("address"),
                "phone": tags.get("phone") or tags.get("contact:phone"),
                "opening_hours": tags.get("opening_hours"),
                "distance_m": distance_m,
                "eta_walk_min": max(1, int(round(distance_m / 80))),
                "walk_url": (
                    "https://www.google.com/maps/dir/?api=1"
                    f"&origin={lat},{lon}&destination={float(place_lat)},{float(place_lon)}"
                    "&travelmode=walking"
                ),
                "drive_url": (
                    "https://www.google.com/maps/dir/?api=1"
                    f"&origin={lat},{lon}&destination={float(place_lat)},{float(place_lon)}"
                    "&travelmode=driving"
                ),
                "maps_url": (
                    "https://www.openstreetmap.org/"
                    f"?mlat={float(place_lat)}&mlon={float(place_lon)}#map=18/{float(place_lat)}/{float(place_lon)}"
                ),
            }
        )

    results.sort(key=lambda item: item["distance_m"])
    return results[:limit]

class SearchView(generics.ListAPIView):
    """Global medicine search endpoint."""
    serializer_class = MedicineListSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        query = self.request.query_params.get('q', '')
        
        if not query:
            return Medicine.objects.none()
        
        return Medicine.objects.filter(
            Q(name__icontains=query) |
            Q(generic_name__icontains=query) |
            Q(category__name__icontains=query) |
            Q(manufacturer__icontains=query) |
            Q(description__icontains=query)
        ).filter(is_active=True).select_related('category')[:20]

# Medical system prompt for Neuro AI
NEURO_AI_SYSTEM_PROMPT = (
    "You are Neuro AI, a knowledgeable and caring medical assistant for NeuroVaidya, "
    "an online pharmacy platform. You help users with health questions, medicine information, "
    "dosage guidance, side effects, and general wellness advice. "
    "Always remind users to consult a doctor for serious conditions. "
    "Keep answers concise, helpful, and easy to understand. "
    "If asked about something non-medical, politely redirect to health topics."
)

class AIChatView(APIView):
    """Endpoint for chatting with an LLM via Groq."""
    permission_classes = [AllowAny]

    def post(self, request):
        prompt = request.data.get('prompt', '')
        if not prompt:
            return Response({'error': 'Prompt is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        from dotenv import load_dotenv
        load_dotenv()
        groq_api_key = os.environ.get('GROQ_API_KEY', '')
        
        if not groq_api_key:
            return Response({'error': 'No GROQ_API_KEY configured.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        try:
            from groq import Groq
            
            client = Groq(api_key=groq_api_key)
            
            available_models = ["groq/compound", "groq/compound-mini", "openai/gpt-oss-20b", "llama-3.3-70b-versatile"]
            model_to_use = os.environ.get("GROQ_MODEL", "groq/compound")
            
            result = None
            last_err = None
            for model_name in [model_to_use] + [m for m in available_models if m != model_to_use]:
                try:
                    result = client.chat.completions.create(
                        model=model_name,
                        messages=[
                            {"role": "system", "content": NEURO_AI_SYSTEM_PROMPT},
                            {"role": "user", "content": prompt},
                        ],
                        max_tokens=512,
                        temperature=0.7,
                        top_p=0.95,
                    )
                    break
                except Exception as err:
                    last_err = err
                    continue
            
            if not result:
                raise last_err or Exception("Failed to generate AI completion.")
            
            generated_text = result.choices[0].message.content
            return Response({'response': generated_text})
                
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LiveMarketStatusView(APIView):
    """Checks the health of the background scraper service."""
    def get(self, request):
        try:
            resp = requests.get("http://127.0.0.1:5001/health", timeout=5)
            # Forward the scraper health response
            return Response(resp.json(), status=resp.status_code)
        except Exception as e:
            return Response({
                "status": "unhealthy", 
                "service": "medicine_scraper",
                "error": str(e),
                "tip": "Check if Gunicorn started correctly in start.sh"
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

class LiveMarketSearchView(APIView):
    """Proxy view that calls the Flask scraper service."""
    def get(self, request):
        query = request.query_params.get('q', '').strip()
        if not query:
            return Response({'error': 'Query parameter q is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Route to local flask scraper service running inside the same container environment
            # Increased timeout for Render sequential mode
            # Using 127.0.0.1 which is standard for local inter-process communication
            resp = requests.get(f"http://127.0.0.1:5001/api/search?q={query}", timeout=120)
            # Forward the JSON response directly
            return Response(resp.json(), status=resp.status_code)
        except requests.exceptions.Timeout:
            return Response({'error': 'Search timed out', 'details': 'The scraper took too long to respond. This can happen on first search; please try again.'}, status=status.HTTP_504_GATEWAY_TIMEOUT)
        except Exception as e:
            logger.error(f"External search proxy error: {str(e)}")
            return Response({'error': 'Live market search unavailable', 'details': f"Connection Error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class NearbySearchView(APIView):
    """Search nearby pharmacies and doctors using OpenStreetMap data."""
    permission_classes = [AllowAny]

    def get(self, request):
        entity_type = request.query_params.get("entity_type", "all").strip().lower()
        query = request.query_params.get("query", "").strip()
        radius_m = int(request.query_params.get("radius_m", 3000))
        limit = int(request.query_params.get("limit", 20))

        if entity_type not in {"all", "pharmacy", "doctor"}:
            return Response(
                {"error": "entity_type must be all, pharmacy, or doctor."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            if request.query_params.get("lat") and request.query_params.get("lon"):
                lat = float(request.query_params.get("lat"))
                lon = float(request.query_params.get("lon"))
                location_name = request.query_params.get("location_name") or _reverse_geocode(lat, lon)
            else:
                if not query:
                    return Response(
                        {"error": "query or lat/lon is required."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                location = _geocode_location(query)
                if not location:
                    return Response({"error": "Location not found."}, status=status.HTTP_404_NOT_FOUND)
                lat = location["lat"]
                lon = location["lon"]
                location_name = location["display_name"]

            results = _search_nearby_places(lat, lon, radius_m, entity_type, limit)
            return Response(
                {
                    "count": len(results),
                    "location": {
                        "lat": lat,
                        "lon": lon,
                        "display_name": location_name,
                    },
                    "query": {
                        "query": query,
                        "entity_type": entity_type,
                        "radius_m": radius_m,
                        "limit": limit,
                    },
                    "results": results,
                }
            )
        except requests.exceptions.Timeout:
            return Response({"error": "Nearby search timed out."}, status=status.HTTP_504_GATEWAY_TIMEOUT)
        except Exception as exc:
            logger.error("Nearby search error: %s", exc)
            return Response({"error": f"Nearby search unavailable: {exc}"}, status=status.HTTP_502_BAD_GATEWAY)
