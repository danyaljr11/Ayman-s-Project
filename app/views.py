import json
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import render, get_object_or_404
from .models import CustomUser, Request
from .serializers import UserSerializer, RequestSerializer


# API Views
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            user = serializer.save()
            user.set_password(serializer.validated_data['password'])
            user.save()
            return Response({'message': 'User registered successfully'}, status=201)
        return Response(serializer.errors, status=400)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = get_object_or_404(CustomUser, email=email)

        if user.check_password(password):
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data
            }, status=200)
        return Response({'error': 'Invalid credentials'}, status=401)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Logged out successfully'}, status=200)
        except Exception as e:
            return Response({'error': str(e)}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class CreateRequestView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure authentication is applied

    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            guest = request.user  # This ensures the request is tied to the authenticated user
            employee_id = data.get('employee')
            description = data.get('description')
            req_type = data.get('type')

            # Validate that the employee exists
            employee = CustomUser.objects.filter(id=employee_id, user_type='employee').first()
            if not employee:
                return Response({'error': 'Invalid employee ID'}, status=400)

            # Create the request
            new_request = Request.objects.create(
                type=req_type,
                status='pending',
                description=description,
                guest=guest,
                employee=employee
            )

            return Response({'message': 'Request created successfully', 'request_id': new_request.id}, status=201)
        except Exception as e:
            return Response({'error': str(e)}, status=500)


class ListRequestsView(APIView):
    permission_classes = [IsAuthenticated]  # Token-based authentication required

    def get(self, request):
        user = request.user
        if user.user_type == 'guest':
            requests = Request.objects.filter(guest=user)
        elif user.user_type == 'employee':
            requests = Request.objects.filter(employee=user)
        else:
            return JsonResponse({"error": "Invalid user type"}, status=400)

        serializer = RequestSerializer(requests, many=True)
        return JsonResponse(serializer.data, safe=False)


class EmployeeListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        employees = CustomUser.objects.filter(user_type='employee')
        serializer = UserSerializer(employees, many=True)
        return Response(serializer.data, status=200)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_guest_requests(request):
    user_id = request.data.get('user_id')
    if not user_id:
        return Response({"error": "User ID is required"}, status=400)

    requests = Request.objects.filter(guest_id=user_id)
    serializer = RequestSerializer(requests, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_employee_requests(request):
    user_id = request.data.get('user_id')
    if not user_id:
        return Response({"error": "User ID is required"}, status=400)

    requests = Request.objects.filter(employee_id=user_id)
    serializer = RequestSerializer(requests, many=True)
    return Response(serializer.data)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def edit_request(request, pk):
    try:
        req = Request.objects.get(pk=pk)
    except Request.DoesNotExist:
        return Response({"error": "Request not found"}, status=status.HTTP_404_NOT_FOUND)

    # Only allow employees to update notes or status
    if request.user.user_type != "employee":
        return Response({"error": "You do not have permission to edit this request"}, status=status.HTTP_403_FORBIDDEN)

    # Partial update
    serializer = RequestSerializer(req, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Request updated successfully", "data": serializer.data})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Template Views
def render_index(request):
    return render(request, 'index.html')


def render_login(request):
    return render(request, 'login.html')


def render_register(request):
    return render(request, 'register.html')


def render_guest_home(request):
    return render(request, 'guest_home.html')


def render_employee_home(request):
    return render(request, 'employee_home.html')


def render_add_request(request):
    return render(request, 'add_request.html')


def render_edit_request(request):
    return render(request, 'edit_request.html')
