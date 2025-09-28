import redis

from django_redis import get_redis_connection
from rest_framework.views import APIView
from rest_framework.generics import RetrieveUpdateAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.exceptions import InvalidToken

from .models import CustomUser
from .serializers import (
    CustomUserSerializers,
    CreateUserSerializer,
    LoginUserSerializer,
    UploadProfileImageSerializer
)

redis_instance = redis.StrictRedis(
    host="127.0.0.1", port=6379, db=1, decode_responses=True
)

class UploadProfileImageView(APIView):
    serializer_class = UploadProfileImageSerializer

    def post(self,request):
        user = request.user
        serializer =self.serializer_class(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True, "message": "Profile Image Updated Successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserInfoView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CustomUserSerializers

    def get(self, request):
        user = request.user
        serializer = self.serializer_class(user)
        return Response({"success":True,"userData":serializer.data}, status=status.HTTP_200_OK)
# class UserRegistrationView(CreateAPIView):
#     serializer_class = CreateUserSerializer


class RegistrationView(APIView):
    def post(self, request):
        data = request.data
        exist_user = CustomUser.objects.filter(email=data["email"]).exists()
        if exist_user:
            return Response(
                {"success": False, "message": "User already exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = CreateUserSerializer(data=data)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        serializer = LoginUserSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data
            # generate token
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            response = Response(
                {"success": True, "user": CustomUserSerializers(user).data},
                status=status.HTTP_200_OK,
            )

            response.set_cookie(
                key="access_token",
                value=access_token,
                httponly=True,
                secure=True,
                samesite="None",
            )

            response.set_cookie(
                key="refresh_token",
                value=str(refresh),
                httponly=True,
                secure=True,
                samesite="None",
            )
            return response

        return Response(
            {"success": False, "error": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


class LogoutView(APIView):
    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")
        if refresh_token:
            try:
                refresh = RefreshToken(refresh_token)
            except Exception as e:
                return Response(
                    {"error": "Error invalidating token:" + str(e)},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        response = Response(
            {"success": True, "message": "Successfully logged out!"},
            status=status.HTTP_200_OK,
        )
        response.delete_cookie("access_token",samesite="None")
        response.delete_cookie("refresh_token",samesite="None")
        return response


class CookieTokenRefreshView(TokenRefreshView):
    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return Response(
                {"success": False, "error": "Refresh token not provided"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)

            response = Response(
                {
                    "success": True,
                    "message": "Access token token refreshed successfully",
                },
                status=status.HTTP_200_OK,
            )
            response.set_cookie(
                key="access_token",
                value=access_token,
                httponly=True,
                secure=True,
                samesite="None",
            )
            return response
        except InvalidToken:
            return Response(
                {"success": False, "error": "Invalid token"},
                status=status.HTTP_401_UNAUTHORIZED,
            )


class ResetPasswordView(APIView):

    def post(self,request):

        data = request.data

        user = CustomUser.objects.filter(email=data['email']).exists()
        if not user:
            return Response(
                {"success": False, "message": "User already exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        reset_otp = redis_instance.get(data['email'])

        if reset_otp != data['otp'] and data['otp'] == "":
            return Response({"success": False, "message": "Invalid OTP"})

        if reset_otp == "":
            return Response({"success": False, "message": "OTP Expired"})

        reset_user = CustomUser.objects.get(email=data['email'])
        reset_user.set_password(data['newPassword'])
        reset_user.save()

        return Response({ "success": True, "message": "Password Reset Successfully" })

class IsAuthView(APIView):
    def post(self, request):
        access_token = request.COOKIES.get("token")
        print("Access Token:", access_token)  # Debugging line
        if not access_token:
            return Response(
                {"success": False, "error": "Access token not provided"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        try:
            # Decode the token to check its validity
            RefreshToken(access_token)
            return Response({"success": True}, status=status.HTTP_200_OK)
        except InvalidToken:
            return Response(
                {"success": False, "error": "Invalid token"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
