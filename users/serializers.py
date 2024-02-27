import json

from dj_rest_auth.registration.serializers import RegisterSerializer
from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from dj_rest_auth.serializers import LoginSerializer, PasswordResetSerializer
from api.models import Payments
from users.models import UserType, User, Industry, CompanyType, Business
import hashlib
from .utils import hash_pan,get_masked_pan
from django.contrib.auth import get_user_model
from .models import Verification
from rest_framework.viewsets import ModelViewSet

class IndustrySerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name')
        model = Industry


class BusinessSerializer(serializers.ModelSerializer):
    industry = IndustrySerializer()

    class Meta:
        fields = ('__all__')
        model = Business


class BusinessPostSerializer(serializers.ModelSerializer):
    masked_pan = serializers.CharField(required=False, write_only=True)
    class Meta:
        fields = ('__all__')
        model = Business


class UserTypeSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name')
        model = UserType


class GetUserReadOnlySerializer(serializers.ModelSerializer):
    business = BusinessSerializer(many=False, read_only=True)
    user_type = UserTypeSerializer()

    class Meta:
        model = User
        exclude = ('password', 'groups', 'user_permissions', 'is_staff')


class GetAssociateUserSerializer(serializers.ModelSerializer):
    user_type = UserTypeSerializer()

    business = BusinessSerializer(many=False, read_only=True)

    class Meta:
        model = User
        fields = ('id', 'first_name', 'user_type', 'business')


class GetMainUserSerializer(serializers.ModelSerializer):
    user_type = UserTypeSerializer()
    business = BusinessSerializer(many=False, read_only=True)

    class Meta:
        model = User
        fields = ('id', 'first_name', 'user_type', 'business')

 #masked_pan = serilaizer.CharField(required=False, write_only=True)
class UserRegisterSerializer(RegisterSerializer):
    user_type = serializers.IntegerField(required=True, write_only=True)
    # created_by = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=True)
    pan_number = serializers.CharField(required=False, write_only=True)

    first_name = serializers.CharField(required=False, write_only=True)
    last_name = serializers.CharField(required=False, write_only=True)
    business = serializers.CharField(required=False, write_only=True)
    phone_number = serializers.CharField(required=False, write_only=True)
    is_premium_user = serializers.CharField(required=False, write_only=True)

   # masked_pan = serializers.SerializerMethodField(read_only=True)


    def custom_signup(self, request, user):
        user.first_name = self.validated_data.get('first_name', '')
        user.last_name = self.validated_data.get('last_name', '')
        user.phone_number = self.validated_data.get('phone_number', '')
        user.pan_number = hash_pan(self.validated_data.get('pan_number', ''))
        user.masked_pan = get_masked_pan(self.validated_data.get('pan_number', ''))
        business_id = self.validated_data.get('business', '')
        user.is_premium_user = self.validated_data.get('is_premium_user', False)
        created_by = request.data['user'].get('created_by', '')
        if created_by != '':
            create_by_user = User.objects.filter(id=created_by)
            if create_by_user:
                user.created_by = create_by_user.first()

        if business_id != '':
            business_info = Business.objects.filter(id=business_id)
            if business_info:
                user.business = business_info.first()

        user_type_info = UserType.objects.filter(id=self.validated_data.get('user_type', '')).first()
        if user_type_info:
            user.user_type = user_type_info
        else:
            return Response({"Status": "Failure", "Message": "There was no record with the provided user_type_id"},
                            status=status.HTTP_404_NOT_FOUND)
        user.save()
# class UserRegistrationViewSet(ModelViewSet):
#     serializer_class = serializers.UserRegisterSerializer
#
#     def create(self, request, *args, **kwargs):
#         try:
#             payload = request.data
#             user_id = request.user.id
#
#             user_details = payload.get('user', {})
#             business_details = payload.get('business', {})
#
#             # Check if 'business' is missing
#             if not business_details:
#                 error_response = {"business": ["This field is required."]}
#                 return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
#
#             is_create_business = False
#             business_id = ''
#             user_details['created_by'] = str(user_id) if user_id else ''
#             is_adding_customer_only = True
#
#             if 'business' in payload:
#                 business_serializer = serializers.BusinessPostSerializer(data=business_details)
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
#             user_serializer = serializers.UserRegisterSerializer(data=user_details)
#             if user_serializer.is_valid():
#                 user_serializer.save(self.request)
#                 user = User.objects.filter(pan_number=user_details['pan_number']).first()
#                 print(serializer.data)
#                 return Response({"success": True, "message": "User Registration successfully completed"},
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


class UserTokenSerializer(serializers.ModelSerializer):
    user = GetUserReadOnlySerializer(many=False, read_only=True)

    class Meta:
        model = Token
        fields = ('key', 'user')


class CustomLoginSerializer(serializers.Serializer):
    pan_number = serializers.CharField(required=True)
    email = serializers.CharField(required=False)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        pan_number = attrs.get('pan_number')

        if not (email or password or pan_number):
            raise serializers.ValidationError('Either "email" or "password" or "pan_number" must be provided.')

        user = authenticate(request=self.context.get('request'), email=email, password=password, pan_number=hash_pan(pan_number))

        if not user:
            user = authenticate(request=self.context.get('request'), email=email, password=password, pan_number=pan_number)
            if not user:
                raise serializers.ValidationError('Unable to log in with provided credentials.')

        if not user.is_active:
            raise serializers.ValidationError('User account is disabled.')

            # Check for pending payments
            # Check for pending payments

        attrs['user'] = user
        return attrs



# class CustomLoginSerializer(serializers.Serializer):
#     pan_number = serializers.CharField(required=True)
#     email = serializers.CharField(required=False)
#
#     def validate(self, attrs):
#         email = attrs.get('email')
#         pan_number = attrs.get('pan_number')
#
#         if not email and not pan_number:
#             raise serializers.ValidationError('Either "email" or "pan_number" must be provided.')
#
#         user = None
#         if email:
#             user = User.objects.filter(email=email).first()
#
#         if pan_number:
#             # hashed_pan = hash_pan(pan_number)
#             user = User.objects.filter(pan_number=hashed_pan).first()
#
#         if not user:
#             raise serializers.ValidationError('Unable to log in with provided credentials.')
#
#         if not user.is_active:
#             raise serializers.ValidationError('User account is disabled.')
#
#         attrs['user'] = user
#         return attrs

class PasswordResetCustomSerializer(PasswordResetSerializer):
    domain = serializers.CharField(required=False)

    def get_email_options(self):
        print('validated_data', self.validated_data)
        """Override this method to change default e-mail options"""
        return {"domain_override": self.validated_data.get('domain')}

class VerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Verification
        fields = ['id', 'identifier', 'otp', 'expiration']


class BusinessSerializer(serializers.ModelSerializer):
    industry = serializers.PrimaryKeyRelatedField(queryset=Industry.objects.all())
    #pan_number = serializers.CharField(read_only=True)  # Set pan_number field as read-only
   # masked_pan = serializers.SerializerMethodField()
    masked_pan = serializers.CharField(read_only=True)
    # def get_masked_pan(self, obj):
    #     return get_masked_pan(obj.pan_number)


    class Meta:
        model = Business
        fields = ['id', 'email', 'masked_pan', 'is_company','incorporation_date', 'industry', 'company', 'name',
                  'city', 'state', 'district', 'country', 'cin', 'phone_number']


# class UserSerializer(serializers.ModelSerializer):
#     pan_number = serializers.CharField(read_only=True)
#     business = BusinessSerializer(read_only=True)
#
#     class Meta:
#         model = User
#         fields = ['id', 'email', 'pan_number', 'user_type', 'business', 'first_name', 'last_name', 'phone_number']
#
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    #pan_number = serializers.CharField(read_only=True)
   # masked_pan = serializers.SerializerMethodField()
    masked_pan = serializers.CharField(read_only=True)
    business = BusinessSerializer()

    # def get_masked_pan(self, obj):
    #     return get_masked_pan(obj.pan_number)

    class Meta:
        model = User
        fields = ['id', 'email', 'masked_pan', 'user_type', 'business', 'first_name', 'last_name', 'phone_number','is_premium_user']

    def update(self, instance, validated_data):
        # Handling update for the nested 'business' field
        business_data = validated_data.pop('business', None)
        if business_data is not None:
            business_instance, _ = Business.objects.get_or_create(id=str(instance.business.id))
            for key, value in business_data.items():
                setattr(business_instance, key, value)
            business_instance.save()

        # Update the remaining fields in 'User' model
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance

class OTPValidationSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    otp = serializers.CharField()
    new_password = serializers.CharField(write_only=True)  # Assuming you're updating the password


class ForgotPasswordSerializer(serializers.Serializer):
    pan_number = serializers.CharField(max_length=10)
    phone_number = serializers.CharField(max_length=10)