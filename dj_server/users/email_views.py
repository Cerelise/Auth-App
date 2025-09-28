import random
import redis

from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django_redis import get_redis_connection
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import CustomUser

redis_instance = redis.StrictRedis(
    host="127.0.0.1", port=6379, db=1, decode_responses=True
)


def generate_OTP():
    otp = ""
    for _ in range(6):
        digit = random.randint(0, 9)
        otp += str(digit)
    return otp


@api_view(["POST"])
def send_verify_otp(request):
    data = request.data
    receiver_email = data["email"]

    otp = generate_OTP()

    send_mail(
        "Completed your account registation",
        f"Your OTP is {otp},Verify your account using this OTP",
        "cerelisezc@qq.com",
        [receiver_email],
        fail_silently=False,
    )

    redis_connect = get_redis_connection()
    res = redis_connect.set(receiver_email, otp)
    redis_connect.expire(receiver_email, 500)

    return Response(
        {"success": True, "message": "Verification OTP Sent on Email"},
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def verify_email(request):
    data = request.data
    user_id = request.user.id
    current_otp = data["otp"]

    user = CustomUser.objects.filter(id=user_id).exists()

    if not user:
        return Response({"success": False, "message": "User not found"})

    user_otp = redis_instance.get(data["email"])

    if user_otp != current_otp and current_otp == "":
        return Response({"success": False, "message": "Invalid OTP"})

    if user_otp == "":
        return Response({"success": False, "message": "OTP Expired"})

    user.is_verified = True
    user.save()

    return Response({"success": True, "message": "Account Verified Successfully"})


@api_view(["POST"])
# @permission_classes([IsAuthenticated])
def send_reset_password_otp(request):
    data = request.data
    receiver_email = data["email"]

    otp = generate_OTP()

    send_mail(
        "Password Reset OTP",
        f"Your OTP for resetting your password is {otp},Use this OTP to precessed with resetting your password.",
        "cerelisezc@qq.com",
        [receiver_email],
        fail_silently=False,
    )

    redis_connect = get_redis_connection()
    res = redis_connect.set(receiver_email, otp)
    redis_connect.expire(receiver_email, 500)

    return Response(
        {"success": True, "message": "Verification OTP Sent on Email"},
        status=status.HTTP_200_OK,
    )
