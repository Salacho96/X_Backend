from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from apps.users.models import User
from apps.users.serializer import UserProfileSerializer
from apps.utils import success_response


class UserSearchView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: UserProfileSerializer(many=True)},
        summary='Buscar usuarios',
        description='Busca usuarios por username o nombre.',
        parameters=[
            OpenApiParameter('q', OpenApiTypes.STR, description='Texto a buscar', required=False)
        ]
    )
    def get(self, request):
        query = request.query_params.get('q', '').strip()
        if not query:
            return success_response(data=[])
        users = User.objects.filter(
            username__icontains=query
        ) | User.objects.filter(
            first_name__icontains=query
        ) | User.objects.filter(
            last_name__icontains=query
        )
        users = users.exclude(id=request.user.id).distinct()
        serializer = UserProfileSerializer(users, many=True)
        return success_response(data=serializer.data)