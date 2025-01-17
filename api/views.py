from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Subject
from difflib import SequenceMatcher
import re


def clean_text(text):
    if not text:
        return ""
    text = re.sub(r'[\'"`“‘’”«»]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def get_similarity(a, b):
    return SequenceMatcher(None, a, b).ratio() * 100


class FindBestMatchAPIView(APIView):
    def post(self, request, *args, **kwargs):
        query_key = request.data.get('key', '')

        if not query_key:
            return Response({'error': 'Key not provided'}, status=status.HTTP_400_BAD_REQUEST)

        query_key = clean_text(query_key)

        best_match = None
        highest_similarity = 0

        for subject in Subject.objects.all():
            cleaned_key = clean_text(subject.key)
            similarity = get_similarity(query_key, cleaned_key)

            # 60% va undan yuqori o'xshashlikni tekshirish
            if similarity > 60 and similarity > highest_similarity:
                highest_similarity = similarity
                best_match = subject

        if best_match:
            return Response({
                'value': best_match.value,
                'similarity': highest_similarity
            })
        else:
            return Response({'error': 'No matching key found'})
