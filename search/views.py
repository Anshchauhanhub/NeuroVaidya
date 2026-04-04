from django.db.models import Q
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from medicines.models import Medicine
from medicines.serializers import MedicineListSerializer
import os

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

class LiveMarketSearchView(APIView):
    """Proxy endpoint to the local Flask scraper running on port 5000."""
    permission_classes = [AllowAny]
    
    def get(self, request):
        query = request.query_params.get('q', '')
        import requests
        
        if not query:
            return Response({'error': 'Query parameter required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Route to local flask scraper service running inside the same container environment
            resp = requests.get(f"http://127.0.0.1:5000/api/search?q={query}", timeout=15)
            # Forward the JSON response directly
            return Response(resp.json(), status=resp.status_code)
        except Exception as e:
            return Response({'error': 'Live market search unavailable', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
