import requests
from django.shortcuts import render
from django.utils.crypto import get_random_string
# Create your views here.
# views.py
from django.db.models import Q
from api.models import Payments
from api.models import GSTinDetails
from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import permissions
import json
from dj_rest_auth.views import LoginView
from api.utils import send_mail_to_user
from glassbox_api import constants
from .models import Business, User
from .serializers import CustomLoginSerializer, UserSerializer, BusinessSerializer, ForgotPasswordSerializer
from . import serializers
from rest_framework.exceptions import PermissionDenied
from rest_framework.exceptions import ValidationError
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .serializers import UserRegisterSerializer,BusinessPostSerializer,OTPValidationSerializer
from rest_framework.viewsets import ModelViewSet
from .utils import hash_pan,get_masked_pan
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
import re
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Verification
from .serializers import VerificationSerializer
from datetime import timedelta
from django.utils import timezone
from .utils import send_verification_message
import random

class CustomLoginView(LoginView):

    serializer_class = CustomLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        user_data = UserSerializer(user).data
        key = user.auth_token.key
        # Check if the user has a Payment with is_success=True
        is_payment_pending = Payments.objects.filter(
            Q(user=user, is_success=False) & ~Q(transaction_id__exact="")
        ).exists()
        user_payment = Payments.objects.filter(user=user)
        is_subscription_active = False
        if user_payment:
            is_subscription_active = user_payment[0].is_subscription_active()
        response_data = {
            'key': key,
            'user': user_data,
            'is_payment_pending':is_payment_pending,
            'is_subscription_active':is_subscription_active
        }

        return Response(response_data, status=status.HTTP_200_OK)

    # def create(self, request):
    #     pan_nummber =  request.data.get('pan_number','')
    #     if pan_nummber:
    #         if Business.objects.filter(pan_number=pan_nummber):
    #             serializer = CustomLoginSerializer(request.data)
    #             if serializer.is_valid():
    #                 return Response(serializer.data)


class VerificationAPIView(APIView):
    def post(self, request, *args, **kwargs):
        identifier = request.data.get('identifier')
        if not identifier:
            return Response({'message': 'phone/email is required'}, status=status.HTTP_400_BAD_REQUEST)

        verification_instance = get_object_or_404(Verification, identifier=identifier)
        otp = request.data.get('otp')

        if verification_instance.is_otp_valid() and otp == verification_instance.otp:
            # Add logic here for successful verification, e.g., user registration
            return Response({'message': 'Verification successful'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Invalid OTP or expired'}, status=status.HTTP_400_BAD_REQUEST)

# Function to generate a new OTP
def generate_otp():
    return ''.join(random.choice('0123456789') for _ in range(6))

class ResendVerificationAPIView(APIView):
    def post(self, request, *args, **kwargs):
        identifier = request.data.get('identifier')
        if not identifier:
            return Response({'message': 'email/phone is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Generate a new OTP for each verification attempt
        otp_value = generate_otp()

        verification_instance, created = Verification.objects.get_or_create(
            identifier=identifier,
            defaults={
                'otp': otp_value,
                'expiration': timezone.now() + timedelta(minutes=15)  # Adjust the expiration time as needed
            }
        )

        # If the instance already exists, update the OTP and expiration time
        if not created:
            verification_instance.otp = generate_otp()
            verification_instance.expiration = timezone.now() + timedelta(minutes=15)
            verification_instance.save()

        send_verification_message(identifier, verification_instance.otp)

        # Add logic here to resend the OTP, e.g., sending a new OTP via email or SMS

        return Response({'message': 'New OTP sent successfully'}, status=status.HTTP_200_OK)



class CustomLoginViewSet(viewsets.ModelViewSet):
    serializer_class = CustomLoginSerializer


    def create(self, request):
        pan_nummber = request.data.get('pan_number', '')
        if pan_nummber:
            if Business.objects.filter(pan_number=pan_nummber):
                serializer = CustomLoginSerializer(request.data)
                if serializer.is_valid():
                    return Response(serializer.data)
#
# class UserRegistrationViewSet(ModelViewSet):
#     serializer_class = UserRegisterSerializer
#
#     def is_pan_or_gstin_exist(self, pan_or_gstin):
#         # Check if the provided pan_or_gstin exists in user details
#         if User.objects.filter(pan_number=pan_or_gstin).exists():
#             return True
#
#         # Check if the provided pan_or_gstin exists in business details
#         if Business.objects.filter(pan_number=pan_or_gstin).exists():
#             return True
#
#         # Check if the provided pan_or_gstin has a PAN in GSTIN details (2nd to 12th characters)
#         gstin_details = Gstindetails.objects.filter(gstin=pan_or_gstin)
#         for gstin_detail in gstin_details:
#             if gstin_detail.gstin[1:12] == pan_or_gstin:
#                 return True
#
#         return False


def is_pan_exists(pan_number):
    # Check if the provided pan_or_gstin exists in user details
    if User.objects.filter(pan_number=hash_pan(pan_number)).exists():
        return True

    return False
def is_phone_exists(phone_number):
    # Check if the provided pan_or_gstin exists in user details
    if User.objects.filter(phone_number=phone_number).exists():
        return True

    return False


class UserRegistrationViewSet(ModelViewSet):
    serializer_class = UserRegisterSerializer  # Use the class directly without the 'serializers.' prefix



    def is_pan_or_gstin_exist(self, pan_or_gstin):
        # Check if the provided pan_or_gstin exists in user details
        if User.objects.filter(pan_number=pan_or_gstin).exists():
            return True


        # Check if the provided pan_or_gstin exists in business details
        if Business.objects.filter(pan_number=pan_or_gstin).exists():
            return True

        # Check if the provided pan_or_gstin exists in GSTIN details
        if GSTinDetails.objects.filter(gstin=pan_or_gstin).exists():
            return True

        # Check if the provided pan_or_gstin has a PAN in GSTIN details (2nd to 12th characters)
        gstin_details = GSTinDetails.objects.all()
        for gstin_detail in gstin_details:
            if gstin_detail.gstin[1:12] == pan_or_gstin:
                return True

        return False


    def create(self, request, *args, **kwargs):
        try:
            payload = request.data
            user_id = request.user.id

            user_details = payload.get('user', {})
            business_details = payload.get('business', {})
            # business_details['masked_pan'] = get_masked_pan(business_details.get('pan_number', ''))



            if not 'phone_number' in user_details:
                error_response = {"phone_number": ["This field is required."]}
                return Response(error_response, status=status.HTTP_400_BAD_REQUEST)

            # Check if PAN or GSTIN already exists
            pan_or_gstin = user_details.get('pan_number', '') or business_details.get('pan_number', '')
            if pan_or_gstin and self.is_pan_or_gstin_exist(pan_or_gstin):
                return Response({"message": "PAN or GSTIN already exists."}, status=status.HTTP_400_BAD_REQUEST)
            # Check if the pan_number's 4th letter is 'c'
            if is_pan_exists(user_details['pan_number']):
                return Response({"message": "PAN already exists."}, status=status.HTTP_400_BAD_REQUEST)


            if is_phone_exists(user_details['phone_number']):
                return Response({"message": "Phone Number already exists."}, status=status.HTTP_400_BAD_REQUEST)
            if 'pan_number' in business_details and business_details['pan_number'].lower()[3] == 'c':
                business_details['is_company'] = True
            # Check if 'business' is missing
            if not business_details:
                error_response = {"business": ["This field is required."]}
                return Response(error_response, status=status.HTTP_400_BAD_REQUEST)

            is_create_business = False
            business_id = ''
            user_details['created_by'] = str(user_id) if user_id else ''
            is_adding_customer_only = True
        #   mobile number and email check
            if 'email' not in user_details or 'phone_number' not in user_details:
                error_response = {"message": ["Email and phone number are required fields."]}
                return Response(error_response, status=status.HTTP_400_BAD_REQUEST)

            if 'business' in payload:
                business_serializer = BusinessPostSerializer(data=business_details)  # Use the class directly
                if business_serializer.is_valid():
                    business_serializer.save()
                    business_id = business_serializer.data['id']
                    user_details['business'] = business_id
                    is_create_business = True
                else:
                    return Response({"success": False, 'message': str(business_serializer.errors)},
                                    status=status.HTTP_400_BAD_REQUEST)

            if 'password1' not in user_details:
                temp_pwd = get_random_string(length=8)
                user_details['password1'] = temp_pwd
                user_details['password2'] = temp_pwd

            user_serializer = UserRegisterSerializer(data=user_details)  # Use the class directly
            if user_serializer.is_valid():
                user_serializer.save(self.request)
                user = User.objects.filter(pan_number=hash_pan(user_details['pan_number'])).first()
                user_data = UserSerializer(user).data
                token = Token.objects.create(user=user).key
                response_data = {
                    'user': user_data,
                    'key': token,
                    'is_subscription_active':False,
                    'is_payment_pending':False
                }
                print(user_serializer.data)  # Corrected 'serializer' to 'user_serializer'
                return Response({"success": True, "message": "User Registration successfully completed", "data": response_data},
                                status=status.HTTP_201_CREATED)
            else:
                if is_create_business:
                    Business.objects.filter(id=business_id).delete()
                return Response({"success": False, 'message': f"{user_serializer.errors}"},
                                status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"success": False, 'message': str(e)},
                            status=status.HTTP_400_BAD_REQUEST)




#
#
# class UserRegistrationViewSet(ModelViewSet):
#     serializer_class = UserRegisterSerializer  # Use the class directly without the 'serializers.' prefix
#
#
#
#
#     def create(self, request, *args, **kwargs):
#         try:
#             payload = request.data
#             user_id = request.user.id
#
#             user_details = payload.get('user', {})
#             business_details = payload.get('business', {})
#             # business_details['masked_pan'] = get_masked_pan(business_details.get('pan_number', ''))
#             # Check if the pan_number's 4th letter is 'c'
#             if 'pan_number' in business_details and business_details['pan_number'].lower()[3] == 'c':
#                 business_details['is_company'] = True
#             # Check if 'business' is missing
#             if not business_details:
#                 error_response = {"business": ["This field is required."]}
#                 return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
#
#             is_create_business = False
#             business_id = ''
#             user_details['created_by'] = str(user_id) if user_id else ''
#             is_adding_customer_only = True
#         #   mobile number and email check
#             if 'email' not in user_details or 'phone_number' not in user_details:
#                 error_response = {"error": ["Email and phone number are required fields."]}
#                 return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
#
#             if 'business' in payload:
#                 business_serializer = BusinessPostSerializer(data=business_details)  # Use the class directly
#                 if business_serializer.is_valid():
#                     business_serializer.save()
#                     business_id = business_serializer.data['id']
#                     user_details['business'] = business_id
#                     is_create_business = True
#                 else:
#                     return Response({"success": False, 'message': str(business_serializer.errors)},
#                                     status=status.HTTP_400_BAD_REQUEST)
#
#             if 'password1' not in user_details:
#                 temp_pwd = get_random_string(length=8)
#                 user_details['password1'] = temp_pwd
#                 user_details['password2'] = temp_pwd
#
#             user_serializer = UserRegisterSerializer(data=user_details)  # Use the class directly
#             if user_serializer.is_valid():
#                 user_serializer.save(self.request)
#                 user = User.objects.filter(pan_number=hash_pan(user_details['pan_number'])).first()
#                 user_data = UserSerializer(user).data
#                 token = Token.objects.create(user=user).key
#                 response_data = {
#                     'user': user_data,
#                     'key': token
#                 }
#                 print(user_serializer.data)  # Corrected 'serializer' to 'user_serializer'
#                 return Response({"success": True, "message": "User Registration successfully completed", "data": response_data},
#                                 status=status.HTTP_201_CREATED)
#             else:
#                 if is_create_business:
#                     Business.objects.filter(id=business_id).delete()
#                 return Response({"success": False, 'message': f"{user_serializer.errors}"},
#                                 status=status.HTTP_400_BAD_REQUEST)
#
#         except Exception as e:
#             return Response({"success": False, 'message': str(e)},
#                             status=status.HTTP_400_BAD_REQUEST)
#


class UserLogoutViewSet(viewsets.ViewSet):
    def create(self, request):
        Token.objects.filter(user=request.user).delete()
        return Response({"success": True, "message": "User logged out successfully"}, status=status.HTTP_200_OK)



class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'id'
    # authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def list(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        user = self.get_object()

        # Check if the user is trying to update their own details
        if user == request.user:
            pan_number = request.data['user'].get("pan_number","")
            business_pan_number = request.data['business'].get("pan_number","")

            masked_pan_number = request.data['user'].get("masked_pan", "")
            masked_business_pan_number = request.data['business'].get("masked_pan", "")

            if pan_number != "" and business_pan_number != "" and masked_pan_number != "" and masked_business_pan_number != "" and (user.pan_number != pan_number or user.business.pan_number != business_pan_number):
                return Response({"detail": "Pan numbers cannot be modified."}, status=status.HTTP_403_FORBIDDEN)
            request_data = request.data["user"]
            request_data["business"] = request.data["business"]
            serializer = self.get_serializer(user, data = request_data,partial=True)

            serializer.is_valid(raise_exception=True)

            self.perform_update(serializer)
            return Response(serializer.data)
        else:
            raise PermissionDenied(detail="You don't have permission to update this user.")



class ForgotPasswordView(APIView):
    def post(self, request):
        # Use the ForgotPasswordSerializer for validation
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            pan_number = serializer.validated_data['pan_number']

            # Check if user exists with the provided PAN number
            user_model = get_user_model()
            user = user_model.objects.filter(pan_number=hash_pan(pan_number)).first()

            if not user:
                return Response({'message': 'User not found with the provided PAN number'}, status=status.HTTP_404_NOT_FOUND)

            # Check if the provided phone number matches the user's phone number
            if user.phone_number != phone_number:
                return Response({'message': 'Phone number does not match the user'}, status=status.HTTP_400_BAD_REQUEST)


            otp_value = generate_otp()
            verification_instance, created = Verification.objects.get_or_create(
                identifier=phone_number,
                defaults={
                    'otp': otp_value,
                    'expiration': timezone.now() + timedelta(minutes=15)  # Adjust the expiration time as needed
                }
            )

            # If the instance already exists, update the OTP and expiration time
            if not created:
                verification_instance.otp = generate_otp()
                verification_instance.expiration = timezone.now() + timedelta(minutes=15)
                verification_instance.save()

            send_verification_message(phone_number, verification_instance.otp)

            # Add logic here to resend the OTP, e.g., sending a new OTP via email or SMS

            return Response({'message': 'New OTP sent successfully'}, status=status.HTTP_200_OK)

            # return Response({'message': 'OTP sent successfully. Please check your phone for the verification code.'})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyPasswordResetView(APIView):
    def post(self, request):
        validation_serializer = OTPValidationSerializer(data=request.data)
        if validation_serializer.is_valid():
            entered_otp = validation_serializer.validated_data['otp']
            phone_number = validation_serializer.validated_data['phone_number']


            if not phone_number:
                return Response({'message': 'phone/email is required'}, status=status.HTTP_400_BAD_REQUEST)

            verification_instance = get_object_or_404(Verification, identifier=phone_number)


            if verification_instance.is_otp_valid() and entered_otp == verification_instance.otp:
                # If OTP is valid, proceed to update the password
                user = get_user_model().objects.get(phone_number=phone_number)
                # Update the user's password (you might want to use serializers for this)
                user.set_password(request.data['new_password'])
                user.save()

                # Delete the verification instance since OTP is used
                verification_instance.delete()

                return Response({'message': 'Password updated successfully'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'Invalid OTP or expired'}, status=status.HTTP_400_BAD_REQUEST)


        else:
            return Response(validation_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


