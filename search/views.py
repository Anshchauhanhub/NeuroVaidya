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

def home_view(request):
    """Serves the home page."""
    return render(request, 'home.html')

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
        
        groq_api_key = os.environ.get('GROQ_API_KEY', '')
        
        if not groq_api_key:
            return Response({'error': 'No GROQ_API_KEY configured.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        try:
            from groq import Groq
            
            client = Groq(api_key=groq_api_key)
            
            result = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": NEURO_AI_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=512,
                temperature=0.7,
                top_p=0.95,
            )
            
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
