from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .models import Tweet, Like
from .serializer import TweetSerializer, TweetCreateSerializer
from apps.users.models import User
from apps.utils import success_response, error_response


class TweetListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: TweetSerializer(many=True)},
        summary='Listar tweets propios',
        description='Retorna los tweets del usuario autenticado paginados.',
        parameters=[
            OpenApiParameter('page', OpenApiTypes.INT, description='Page number', required=False)
        ]
    )
    def get(self, request):
        tweets = Tweet.objects.filter(author=request.user).select_related('author')
        page_number = request.query_params.get('page', 1)
        paginator = Paginator(tweets, 10)
        page = paginator.get_page(page_number)
        serializer = TweetSerializer(page.object_list, many=True, context={'request': request})
        return success_response(data={
            'tweets': serializer.data,
            'total_pages': paginator.num_pages,
            'current_page': page.number,
            'has_next': page.has_next(),
            'has_previous': page.has_previous(),
        })

    @extend_schema(
        request=TweetCreateSerializer,
        responses={201: TweetSerializer},
        summary='Crear tweet',
        description='Crea un nuevo tweet para el usuario autenticado. Máximo 280 caracteres.',
    )
    def post(self, request):
        serializer = TweetCreateSerializer(data=request.data)
        if serializer.is_valid():
            tweet = serializer.save(author=request.user)
            return success_response(
                data=TweetSerializer(tweet, context={'request': request}).data,
                message='Tweet created successfully.',
                status_code=201
            )
        return error_response(message='Error creating tweet.', errors=serializer.errors, status_code=400)


class TweetDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: TweetSerializer},
        summary='Obtener tweet',
        description='Retorna el detalle de un tweet por id.',
    )
    def get(self, request, pk):
        tweet = get_object_or_404(Tweet, pk=pk)
        serializer = TweetSerializer(tweet, context={'request': request})
        return success_response(data=serializer.data)

    @extend_schema(
        responses={200: None},
        summary='Eliminar tweet',
        description='Elimina un tweet propio.',
    )
    def delete(self, request, pk):
        tweet = get_object_or_404(Tweet, pk=pk)
        if tweet.author != request.user:
            return error_response(message='You are not the owner of this tweet.', status_code=403)
        tweet.delete()
        return success_response(message='Tweet deleted successfully.')


class TimelineView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: TweetSerializer(many=True)},
        summary='Timeline',
        description='Retorna los tweets de los usuarios que seguís, ordenados cronológicamente.',
        parameters=[
            OpenApiParameter('page', OpenApiTypes.INT, description='Page number', required=False)
        ]
    )
    def get(self, request):
        following_users = User.objects.filter(followers__follower=request.user)
        tweets = Tweet.objects.filter(author__in=following_users).select_related('author').prefetch_related('likes')
        page_number = request.query_params.get('page', 1)
        paginator = Paginator(tweets, 10)
        page = paginator.get_page(page_number)
        serializer = TweetSerializer(page.object_list, many=True, context={'request': request})
        return success_response(data={
            'tweets': serializer.data,
            'total_pages': paginator.num_pages,
            'current_page': page.number,
            'has_next': page.has_next(),
            'has_previous': page.has_previous(),
        })


class LikeView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={201: None},
        summary='Like / Unlike tweet',
        description='Si no likeaste el tweet lo likeás, si ya lo likeaste lo unlikeás.',
    )
    def post(self, request, pk):
        tweet = get_object_or_404(Tweet, pk=pk)
        like, created = Like.objects.get_or_create(user=request.user, tweet=tweet)
        if not created:
            like.delete()
            return success_response(message='Like removed.')
        return success_response(message='Like added.', status_code=201)