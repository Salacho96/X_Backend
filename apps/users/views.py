from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

from .models import User, Follow
from .serializer import RegisterSerializer, LoginSerializer, UserProfileSerializer
from apps.utils import success_response, error_response


class RegisterView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=RegisterSerializer,
        responses={201: UserProfileSerializer},
        summary='Registro de usuario',
        description='Crea un nuevo usuario y retorna tokens JWT.',
        examples=[
            OpenApiExample(
                'Ejemplo registro',
                value={'email': 'user@example.com', 'username': 'myuser', 'password': 'mypassword123'},
                request_only=True,
            )
        ]
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return success_response(
                data={
                    'user': UserProfileSerializer(user).data,
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                },
                message='User successfully registered.',
                status_code=201
            )
        return error_response(
            message='Error in registration.',
            errors=serializer.errors,
            status_code=400
        )


class LoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=LoginSerializer,
        responses={200: UserProfileSerializer},
        summary='Login de usuario',
        description='Authenticates a user and returns JWT tokens.',
        examples=[
            OpenApiExample(
                'Ejemplo login',
                value={'email': 'user@example.com', 'password': 'mypassword123'},
                request_only=True,
            )
        ]
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            return success_response(
                data={
                    'user': UserProfileSerializer(user).data,
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                },
                message='Sesión iniciada correctamente.'
            )
        return error_response(
            message='Invalid credentials.',
            errors=serializer.errors,
            status_code=400
        )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request={'application/json': {'type': 'object', 'properties': {'refresh': {'type': 'string'}}}},
        responses={200: None},
        summary='Logout de usuario',
        description='Blacklistea el refresh token para cerrar sesión.',
        examples=[
            OpenApiExample(
                'Ejemplo logout',
                value={'refresh': 'eyJ...'},
                request_only=True,
            )
        ]
    )
    def post(self, request):
        try:
            refresh_token = request.data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist()
            return success_response(message='Session successfully closed.')
        except Exception:
            return error_response(message='Invalid token.', status_code=400)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: UserProfileSerializer},
        summary='Obtener perfil de usuario',
        description='Retorna el perfil público de un usuario por username.',
    )
    def get(self, request, username):
        user = get_object_or_404(User, username=username)
        return success_response(data=UserProfileSerializer(user).data)

    @extend_schema(
        request=UserProfileSerializer,
        responses={200: UserProfileSerializer},
        summary='Actualizar perfil de usuario',
        description='Actualiza bio o avatar del usuario autenticado.',
        examples=[
            OpenApiExample(
                'Ejemplo actualizar perfil',
                value={'bio': 'Mi nueva bio'},
                request_only=True,
            )
        ]
    )
    def put(self, request, username):
        if request.user.username != username:
            return error_response(message='Unauthorized.', status_code=403)
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return success_response(data=serializer.data, message='Profile updated successfully.')
        return error_response(message='Error updating profile.', errors=serializer.errors, status_code=400)


class FollowView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={201: None},
        summary='Follow / Unfollow usuario',
        description='Si no seguís al usuario lo seguís, si ya lo seguís lo dejás de seguir.',
    )
    def post(self, request, username):
        target = get_object_or_404(User, username=username)
        if target == request.user:
            return error_response(message='You cannot follow yourself.', status_code=400)
        follow, created = Follow.objects.get_or_create(follower=request.user, following=target)
        if not created:
            follow.delete()
            return success_response(message=f'You stopped following {target.username}.')
        return success_response(message=f'You are now following {target.username}.', status_code=201)


class FollowersListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: UserProfileSerializer(many=True)},
        summary='Listar followers',
        description='Retorna la lista de usuarios que siguen al usuario dado.',
    )
    def get(self, request, username):
        user = get_object_or_404(User, username=username)
        followers = User.objects.filter(following__following=user)
        return success_response(data=UserProfileSerializer(followers, many=True).data)


class FollowingListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: UserProfileSerializer(many=True)},
        summary='Listar following',
        description='Retorna la lista de usuarios que sigue el usuario dado.',
    )
    def get(self, request, username):
        user = get_object_or_404(User, username=username)
        following = User.objects.filter(followers__follower=user)
        return success_response(data=UserProfileSerializer(following, many=True).data)