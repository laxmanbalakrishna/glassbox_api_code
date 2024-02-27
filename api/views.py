import traceback

from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from users.serializers import GetUserReadOnlySerializer, UserSerializer
from . import serializers
from .models import MyPartner, RaisedDisputes, Notification, Payments, GSTinDetails, Subscription
from users.models import UserType, Industry, CompanyType, User
from collections import namedtuple
from django.db.models import Q, Avg
from datetime import datetime
from .serializers import RaisedDisputeSerializer, ResolveDisputeSerializer, NotificationSerializer, PaymentSerializer,GSTinDetailsSerializer, SubscriptionSerializer
from users.utils import hash_pan, get_serilizer_errors
from .utils import fetch_and_save_gstin_details, is_valid_phone_number
import requests
from datetime import datetime, timedelta

GlobalConfig = namedtuple('GlobalConfig', ('company_type', 'industry_type', 'partner_type'))


class MyPartnersViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.MyPartnersSerializer

    queryset = MyPartner.objects.all()

    def apply_default_values(self, instance, data):
        # Apply default values to specific fields if they are present in the payload
        fields_to_reset = [
            'pending_receivables', 'legal_proceedings', 'reachability',
            'recovery_probability', 'on_time_Payment', 'transaction_paid_ontime',
            'is_gst_paid', 'capital', 'assets', 'total_outstanding', 'dso', 'known_since'
        ]

        default_values = {
            'pending_receivables': 0,
            'legal_proceedings': 0,
            'reachability': 0,
            'recovery_probability': 0,
            'on_time_Payment': 0,
            'transaction_paid_ontime': 4,
            'is_gst_paid': 1,
            'capital': 0,
            'assets': 0,
            'total_outstanding': 0,
            'dso': 0,
            'known_since': datetime.now().date() - timedelta(days=365)  # Default value for known_since (one year ago)
        }

        for field in fields_to_reset:
            setattr(instance, field, data.get(field, default_values.get(field, 0)))
    def create(self, request, *args, **kwargs):
        try:
            user_id = request.user.id
            request.data['business_partner_main'] = user_id

            # Check if the MyPartner instance already exists
            my_partner_queryset = MyPartner.objects.filter(
                business_partner_main=user_id,
                business_partner_assoc=request.data['business_partner_assoc']
            )

            if my_partner_queryset.exists():
                # If it exists, update the existing instance
                update_serializer = serializers.MyPartnersPostSerializer(
                    my_partner_queryset.first(), data=request.data
                )

                if update_serializer.is_valid():
                    self.apply_default_values(update_serializer.instance, request.data)
                    update_serializer.save()
                    return Response({'success': True, 'message': 'Updated successfully'},
                                    status=status.HTTP_200_OK)
                return Response({'success': False, 'message': 'Updating rating to the customer/business Failed'},
                                status=status.HTTP_400_BAD_REQUEST)

            # If it doesn't exist, create a new instance
            serializer = serializers.MyPartnersPostSerializer(data=request.data)

            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            my_partner_obj = serializer.save()
            self.apply_default_values(my_partner_obj, request.data)
            my_partner_obj.save()

            # Create a notification for the recipient
            recipient_id = request.data['business_partner_assoc']
            sender_id = user_id
            score = request.data['score']

            title = f"{request.user.first_name} rates you "
            description = f"{request.user.first_name} has given a rating of {score} to you "
            my_partner_id = my_partner_obj.id

            Notification.objects.create(
                sender=User.objects.get(id=sender_id),
                recipient=User.objects.get(id=recipient_id),
                notification_type=2,
                type_id=my_partner_id,
                title=title,
                description=description
            )

            return Response({'success': True, 'message': 'Created successfully'},
                            status=status.HTTP_201_CREATED)

        except Exception as er:
            return Response({'success': False, 'message': f"{er}"}, status.HTTP_400_BAD_REQUEST)

    # def list(self, request, *args, **kwargs):
    #     user_id = request.user.id
    #     queryset = MyPartner.objects.filter(business_partner_main=user_id)
    #     serializer = self.serializer_class(queryset, many=True)
    #     return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        user_id = request.user.id
        queryset = MyPartner.objects.filter(business_partner_main=user_id)

        serialized_data = []

        for partner in queryset:
            partner_data = self.serializer_class(partner).data
            print(partner_data)
            partner_id = partner.business_partner_assoc.id

            # Calculate the average rating for the current partner
            avg_rating = MyPartner.objects.filter(business_partner_assoc=partner_id).aggregate(Avg('score'))[
                'score__avg']

            # Set avg_rating to 0.0 if there are no scores for the partner
            avg_rating = avg_rating or 0.0

            # Format avg_rating to two decimal places
            avg_rating_formatted = "{:.2f}".format(avg_rating)

            partner_data['avg_rating'] = avg_rating_formatted
            serialized_data.append(partner_data)
        return Response(serialized_data)

    def update(self, request, *args, **kwargs):
        user_id = request.user.id
        instance = self.get_object()
        if instance.business_partner_main.id != user_id:
            return Response({'success': False, 'message': 'You are not allowed to update this record'},
                            status=status.HTTP_400_BAD_REQUEST)
        serializer = serializers.MyPartnersPostSerializer(instance, data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response({'success': True, 'message': 'Updated successfully'},
                        status=status.HTTP_200_OK)


class GetPartnerRatingViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.AssociatePartnersSerializer
    http_method_names = ['get']

    def list(self, request, *args, **kwargs):
        user_id = request.user.id
        associate_patner_id = self.request.query_params.get('partner_id')

        queryset = MyPartner.objects.filter(business_partner_assoc=associate_patner_id)
        serializer = self.serializer_class(queryset, many=True)

        # Loop through each item in the serialized data
        disputes_on_him = RaisedDisputes.objects.filter(raised_on_user__id=associate_patner_id).count()
        for item in serializer.data:


            item['no_of_disputes'] = disputes_on_him

        return Response(serializer.data)


class DisputeViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = RaisedDisputes.objects.all()

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'create':
            return RaisedDisputeSerializer
        elif self.action == 'update' or self.action == 'partial_update':
            return ResolveDisputeSerializer

    # def create(self, request, *args, **kwargs):
    #     user_id = request.user.id
    #     request.data['user'] = user_id
    #     request.data['raised_on'] = datetime.datetime.now()
    #
    #     raised_on_user_id = request.data['raised_on_user']
    #
    #     queryset = RaisedDisputes.objects.filter(user=request.user, raised_on_user=raised_on_user_id)
    #
    #     if queryset.exists():
    #         return Response({'success': False, 'message': 'You Already Raised Dispute'}, status=status.HTTP_400_BAD_REQUEST)
    #     serializer = self.get_serializer(data=request.data)
    #     if not serializer.is_valid():
    #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #
    #     my_partner = MyPartner.objects.filter(business_partner_assoc=user_id).first()
    #
    #     if my_partner.score < 3:
    #         serializer.save()
    #         MyPartner.objects.filter(business_partner_assoc=user_id).update(is_raised_dispute=True)
    #
    #         return Response({'success': True, 'message': 'Created successfully'}, status=status.HTTP_201_CREATED)
    #     else:
    #         return Response(
    #             {'success': False, 'message': 'Dispute cannot be raised when score is greater than or equal to 3.'},
    #             status=status.HTTP_400_BAD_REQUEST)
    def create(self, request, *args, **kwargs):
        user_id = request.user.id
        request.data['user'] = user_id
        request.data['raised_on'] = datetime.now()

        raised_on_user_id = request.data['raised_on_user']

        queryset = RaisedDisputes.objects.filter(user=request.user, raised_on_user=raised_on_user_id)

        if queryset.exists():
            return Response({'success': False, 'message': 'You Already Raised Dispute'},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        list_of_my_partner = MyPartner.objects.filter(business_partner_assoc=user_id)

        # Filter the list further based on raised_on_user_id
        my_partner = list_of_my_partner.filter(business_partner_main__id=raised_on_user_id).first()

        if my_partner.score < 5:
            dispute = serializer.save()
            MyPartner.objects.filter(business_partner_assoc=user_id).update(is_raised_dispute=True)

            # Create a notification for the recipient
            recipient_id = raised_on_user_id  # Replace with the actual recipient's ID
            sender_id = user_id
            reason = request.data['reason']

            # You can customize the title and description as needed
            title = f"{request.user.first_name} raised a dispute on you"
            description = f" {reason}"

            Notification.objects.create(
                sender=User.objects.get(id=sender_id),
                recipient=User.objects.get(id=recipient_id),
                notification_type=1,  # Use the appropriate type for Raised Dispute
                type_id=dispute.id,  # Assuming the dispute has an ID
                title=title,
                description=description
            )

            return Response({'success': True, 'message': 'Raised Dispute successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {'success': False, 'message': 'Dispute cannot be raised when the score is greater than or equal to 3.'},
                status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        user_id = request.user.id
        instance = self.get_object()

        update_queryset = RaisedDisputes.objects.filter(raised_on_user=request.user)
        if not update_queryset.exists():
            return Response({'success': False, 'message': 'You are not allowed to update this record'},
                            status=status.HTTP_400_BAD_REQUEST)

        request.data['resolved_on'] = datetime.now()
        request.data['is_resolved'] = True

        if instance.user.id == user_id:
            return Response({'success': False, 'message': 'You are not allowed to update this record'},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = ResolveDisputeSerializer(instance, data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response({'success': True, 'message': 'Updated successfully'},
                        status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        user = request.user
        queryset = RaisedDisputes.objects.filter(Q(user=user) | Q(raised_on_user=user))

        raised_disputes = []
        resolved_disputes = []

        for dispute in queryset:
            if dispute.user == user:
                resolved_data = {
                    "id": dispute.id,
                    "reason": dispute.reason,
                    'response': dispute.response,
                    "user": UserSerializer(dispute.user).data,
                    "raised_on_user": UserSerializer(dispute.raised_on_user).data,
                    "is_resolved": dispute.is_resolved,
                    "raised_on": dispute.raised_on,
                    "resolved_on": dispute.resolved_on
                }
                raised_disputes.append(resolved_data)
            else:
                dispute_data = {
                    "id": dispute.id,
                    "reason": dispute.reason,
                    "raised_on": dispute.raised_on,
                    'response': dispute.response,
                    "resolved_on": dispute.resolved_on,
                    "user": UserSerializer(dispute.user).data,
                    "raised_on_user": UserSerializer(dispute.raised_on_user).data,
                    "is_resolved": dispute.is_resolved,
                }
                resolved_disputes.append(dispute_data)
        response_data = {
            "raisedDispute": raised_disputes,
            "resolveDispute": resolved_disputes
        }
        return Response(response_data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance is not None:
            self.perform_destroy(instance)
            return Response({'success': True, 'message': 'Raised Dispute deleted successfully'},
                            status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Raised Dispute does not exist'}, status=status.HTTP_404_NOT_FOUND)


class GlobalConfigViewSet(viewsets.ModelViewSet):
    http_method_names = ['get']
    serializer_class = serializers.GlobalConfigSerializer

    def list(self, request, *args, **kwargs):
        data = GlobalConfig(
            partner_type=UserType.objects.filter(~Q(id=1)),
            company_type=CompanyType.objects.all(),
            industry_type=Industry.objects.all()
        )
        serializer = serializers.GlobalConfigSerializer(data)

        return Response(serializer.data)

# #
# # #prev
# import requests
#
# from datetime import datetime
#
#
# class SearchPartnerViewSet(viewsets.ViewSet):
#     permission_classes = (IsAuthenticated,)
#     http_method_names = ['get']
#
#     def list(self, request, *args, **kwargs):
#         search_key = self.request.query_params.get('searchKey')
#
#         if not search_key:
#             return Response({'success':False, "message": 'Search key is required'}, status=status.HTTP_400_BAD_REQUEST)
#
#         if len(search_key) == 10:
#             if is_valid_phone_number(search_key):
#                 # Check with phone number in user model model
#                 user = User.objects.filter(~Q(id=request.user.id), phone_number=search_key)
#                 serializer = UserSerializer(user, many=True)
#                 if len(user) > 0:
#                     is_user_linked = self.check_user_link(user[0].id)
#                     serializer.data[0]['is_user_linked'] = is_user_linked
#                 return Response(serializer.data, status=status.HTTP_200_OK)
#             else:
#                 # Check with PAN number in user model
#                 user = User.objects.filter(~Q(id=request.user.id), pan_number=str(hash_pan(search_key)))
#                 serializer = UserSerializer(user, many=True)
#                 if len(user) > 0:
#                     is_user_linked = self.check_user_link(user[0].id)
#                     serializer.data[0]['is_user_linked'] = is_user_linked
#                 return Response(serializer.data, status=status.HTTP_200_OK)
#         elif len(search_key) == 15:
#             # Check with GSTIN number in GSTinDetails model
#             pan_number = search_key[2:12]
#             user = User.objects.filter(~Q(id=request.user.id), pan_number=str(hash_pan(pan_number)))
#             if len(user) > 0:
#                 serializer = UserSerializer(user, many=True)
#                 is_user_linked = self.check_user_link(user[0].id)
#                 serializer.data[0]['is_user_linked'] = is_user_linked
#                 serializer.data[0]['is_user_exists'] = True
#                 return Response(serializer.data, status=status.HTTP_200_OK)
#
#             gstin_details = GSTinDetails.objects.filter(gstin=search_key)
#             if gstin_details:
#                 serializer = GSTinDetailsSerializer(gstin_details, many=True)
#                 serializer.data[0]['is_user_exists'] = False
#                 serializer.data[0]['is_user_linked'] = False
#                 return Response(serializer.data, status=status.HTTP_200_OK)
#             else:
#                 # Fetch and create new GST details
#                 success, new_gstin_details_response = fetch_and_save_gstin_details(search_key)
#
#                 if success:
#                 # Create and save the new GST details in the GSTinDetails model
#                     gstin_details = GSTinDetails.objects.create(**extracted_data)
#
#                     # Serialize and return the newly created GSTinDetails
#                     serializer = GSTinDetailsSerializer(gstin_details)
#                     serializer.data[0]['is_user_exists'] = False
#                     serializer.data[0]['is_user_linked'] = False
#
#                         # Successfully created new GST details
#                     return Response(serializer.data, status=status.HTTP_201_CREATED)
#                 else:
#                     return Response({'success': False,'message': new_gstin_details_response},
#                                         status=status.HTTP_400_BAD_REQUEST)
#                     return Response({'success':False, "message": 'Invalid search key'}, status=status.HTTP_400_BAD_REQUEST)
#
#     def check_user_link(self, uid):
#         my_partner_queryset = MyPartner.objects.filter(business_partner_main=self.request.user.id,
#                                                        business_partner_assoc=uid)
#         return my_partner_queryset.exists()
#
#
# class GSTSearchViewSet(viewsets.ViewSet):
#     http_method_names = ['get']
#
#     def list(self, request, *args, **kwargs):
#         search_key = self.request.query_params.get('searchKey')
#
#         if not search_key:
#             return Response({'success': False, "message": 'Search key is required'}, status=status.HTTP_400_BAD_REQUEST)
#
#         if len(search_key) == 15:
#             # Check with GSTIN number in GSTinDetails model
#             pan_number = search_key[2:12]
#             user = User.objects.filter( pan_number=str(hash_pan(pan_number)))
#             if len(user) > 0:
#                 serializer = UserSerializer(user, many=True)
#                 serializer.data[0]['is_user_exists'] = True
#                 return Response(serializer.data, status=status.HTTP_200_OK)
#
#             gstin_details = GSTinDetails.objects.filter(gstin=search_key)
#             if gstin_details:
#                 serializer = GSTinDetailsSerializer(gstin_details, many=True)
#                 serializer.data[0]['is_user_exists'] = False
#                 return Response(serializer.data, status=status.HTTP_200_OK)
#             else:
#                 # Fetch and create new GST details
#                 success, new_gstin_details_response = fetch_and_save_gstin_details(search_key)
#
#                 if success:
#                     # Create and save the new GST details in the GSTinDetails model
#                     gstin_details = GSTinDetails.objects.create(**extracted_data)
#
#                     # Serialize and return the newly created GSTinDetails
#                     serializer = GSTinDetailsSerializer(gstin_details)
#                     serializer.data[0]['is_user_exists'] = False
#
#                     # Successfully created new GST details
#                     return Response(serializer.data, status=status.HTTP_201_CREATED)
#                 else:
#                     return Response({'success': False, 'message': new_gstin_details_response},
#                                     status=status.HTTP_400_BAD_REQUEST)
#         return Response({'success': False, "message": 'Invalid search key'}, status=status.HTTP_400_BAD_REQUEST)
# #
# # prev
#
#

class SearchPartnerViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)
    http_method_names = ['get']

    def list(self, request, *args, **kwargs):
        search_key = self.request.query_params.get('searchKey')

        if not search_key:
            return Response({'success':False, "message": 'Search key is required'}, status=status.HTTP_400_BAD_REQUEST)

        if len(search_key) == 10:
            if is_valid_phone_number(search_key):
                # Check with phone number in user model model
                user = User.objects.filter(~Q(id=request.user.id), phone_number=search_key)
                serializer = UserSerializer(user, many=True)
                if len(user) > 0:
                    is_user_linked = self.check_user_link(user[0].id)
                    serializer.data[0]['is_user_linked'] = is_user_linked
                    serializer.data[0]['is_user_exists'] = True
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                # Check with PAN number in user model
                user = User.objects.filter(~Q(id=request.user.id), pan_number=str(hash_pan(search_key)))
                serializer = UserSerializer(user, many=True)
                if len(user) > 0:
                    is_user_linked = self.check_user_link(user[0].id)
                    serializer.data[0]['is_user_linked'] = is_user_linked
                    serializer.data[0]['is_user_exists'] = True
                return Response(serializer.data, status=status.HTTP_200_OK)
        elif len(search_key) == 15:
            # Check with GSTIN number in GSTinDetails model
            pan_number = search_key[2:12]
            user = User.objects.filter(~Q(id=request.user.id), pan_number=str(hash_pan(pan_number)))
            if len(user) > 0:
                serializer = UserSerializer(user, many=True)
                is_user_linked = self.check_user_link(user[0].id)
                serializer.data[0]['is_user_linked'] = is_user_linked
                serializer.data[0]['is_user_exists'] = True
                return Response(serializer.data, status=status.HTTP_200_OK)

            gstin_details = GSTinDetails.objects.filter(gstin=search_key)
            if gstin_details:
                serializer = GSTinDetailsSerializer(gstin_details, many=True)
                serializer.data[0]['is_user_exists'] = False
                serializer.data[0]['is_user_linked'] = False
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                # Fetch and create new GST details
                success, extracted_data = fetch_and_save_gstin_details(search_key)
                if success:
                # Create and save the new GST details in the GSTinDetails model
                    gstin_details = GSTinDetails.objects.create(**extracted_data)

                    # Serialize and return the newly created GSTinDetails
                    serializer = GSTinDetailsSerializer(gstin_details)
                    serializer.data['is_user_exists'] = False
                    serializer.data['is_user_linked'] = False

                        # Successfully created new GST details
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    return Response({'success': False,'message': extracted_data},
                                        status=status.HTTP_400_BAD_REQUEST)
        return Response({'success':False, "message": 'Invalid search key'}, status=status.HTTP_400_BAD_REQUEST)

    def check_user_link(self, uid):
        my_partner_queryset = MyPartner.objects.filter(business_partner_main=self.request.user.id,
                                                       business_partner_assoc=uid)
        return my_partner_queryset.exists()

#code with fields
# class GSTSearchViewSet(viewsets.ViewSet):
#     http_method_names = ['get']
#
#     def list(self, request, *args, **kwargs):
#         search_key = self.request.query_params.get('searchKey')
#
#         if not search_key:
#             return Response({'success': False, "message": 'Search key is required'}, status=status.HTTP_400_BAD_REQUEST)
#
#         if len(search_key) == 15:
#             # Check with GSTIN number in GSTinDetails model
#             pan_number = search_key[2:12]
#             user = User.objects.filter(pan_number=str(hash_pan(pan_number)))
#             if len(user) > 0:
#                 serializer = UserSerializer(user, many=True)
#                 is_user_linked = self.check_user_link(user[0].id)
#                 serializer_data = serializer.data
#                 for data in serializer_data:
#                     data['is_user_linked'] = is_user_linked
#                     data['is_user_exists'] = True
#                 return Response(serializer_data, status=status.HTTP_200_OK)
#
#             gstin_details = GSTinDetails.objects.filter(gstin=search_key)
#             if gstin_details:
#                 serializer = GSTinDetailsSerializer(gstin_details, many=True)
#                 serializer_data = serializer.data
#                 for data in serializer_data:
#                     data['is_user_linked'] = False
#                     data['is_user_exists'] = False
#                 return Response(serializer_data, status=status.HTTP_200_OK)
#             else:
#                 # Fetch and create new GST details
#                 success, new_gstin_details_response = fetch_and_save_gstin_details(search_key)
#
#                 if success:
#                     # Create and save the new GST details in the GSTinDetails model
#                     gstin_details = GSTinDetails.objects.create(**new_gstin_details_response)
#
#                     # Serialize and return the newly created GSTinDetails
#                     serializer = GSTinDetailsSerializer(gstin_details)
#                     if serializer.data:
#                         data_dict = dict(serializer.data)
#                         data_dict['is_user_linked'] = False
#                         data_dict['is_user_exists'] = False
#                         return Response(data_dict, status=status.HTTP_201_CREATED)
#                     else:
#                         return Response({'success': False, 'message': 'Failed to serialize GSTinDetails'},
#                                         status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#                 else:
#                     return Response({'success': False, 'message': new_gstin_details_response},
#                                     status=status.HTTP_400_BAD_REQUEST)
#         return Response({'success': False, "message": 'Invalid search key'}, status=status.HTTP_400_BAD_REQUEST)
#


#code in array
class GSTSearchViewSet(viewsets.ViewSet):

    http_method_names = ['get']

    def list(self, request, *args, **kwargs):
        search_key = self.request.query_params.get('searchKey')

        if not search_key:
            return Response({'success': False, "message": 'Search key is required'}, status=status.HTTP_400_BAD_REQUEST)

        if len(search_key) == 15:
            # Check with GSTIN number in GSTinDetails model
            pan_number = search_key[2:12]
            user = User.objects.filter(pan_number=str(hash_pan(pan_number)))
            if len(user) > 0:
                serializer = UserSerializer(user[0])
                is_user_linked = self.check_user_link(user[0].id)
                serializer_data = serializer.data
                serializer_data['is_user_linked'] = is_user_linked
                serializer_data['is_user_exists'] = True
                return Response(serializer_data, status=status.HTTP_200_OK)

            gstin_details = GSTinDetails.objects.filter(gstin=search_key).first()
            if gstin_details:
                serializer = GSTinDetailsSerializer(gstin_details)
                serializer_data = serializer.data
                serializer_data['is_user_linked'] = False
                serializer_data['is_user_exists'] = False
                return Response(serializer_data, status=status.HTTP_200_OK)
            else:
                # Fetch and create new GST details
                success, new_gstin_details_response = fetch_and_save_gstin_details(search_key)

                if success:
                    # Create and save the new GST details in the GSTinDetails model
                    gstin_details = GSTinDetails.objects.create(**new_gstin_details_response)

                    # Serialize and return the newly created GSTinDetails
                    serializer = GSTinDetailsSerializer(gstin_details)
                    if serializer.data:
                        data_dict = dict(serializer.data)
                        data_dict['is_user_linked'] = False
                        data_dict['is_user_exists'] = False
                        return Response(data_dict, status=status.HTTP_201_CREATED)
                    else:
                        return Response({'success': False, 'message': 'Failed to serialize GSTinDetails'},
                                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                else:
                    return Response({'success': False, 'message': new_gstin_details_response},
                                    status=status.HTTP_400_BAD_REQUEST)
        return Response({'success': False, "message": 'Invalid search key'}, status=status.HTTP_400_BAD_REQUEST)
    def check_user_link(self, uid):
        my_partner_queryset = MyPartner.objects.filter(business_partner_main=self.request.user.id,
                                                       business_partner_assoc=uid)
        return my_partner_queryset.exists()
# class GSTSearchViewSet(viewsets.ViewSet):
#     http_method_names = ['get']
#
#     def list(self, request, *args, **kwargs):
#         search_key = self.request.query_params.get('searchKey')
#
#         if not search_key:
#             return Response({'success': False, "message": 'Search key is required'}, status=status.HTTP_400_BAD_REQUEST)
#
#         if len(search_key) == 15:
#             # Check with GSTIN number in GSTinDetails model
#             pan_number = search_key[2:12]
#             user = User.objects.filter(pan_number=str(hash_pan(pan_number)))
#             if len(user) > 0:
#                 serializer = UserSerializer(user, many=True)
#                 serializer.data[0]['is_user_exists'] = True
#                 return Response(serializer.data, status=status.HTTP_200_OK)
#
#             gstin_details = GSTinDetails.objects.filter(gstin=search_key)
#             if gstin_details:
#                 serializer = GSTinDetailsSerializer(gstin_details, many=True)
#                 serializer.data[0]['is_user_exists'] = False
#                 return Response(serializer.data, status=status.HTTP_200_OK)
#             else:
#                 # Fetch and create new GST details
#                 success, new_gstin_details_response = fetch_and_save_gstin_details(search_key)
#
#                 if success:
#                     # Create and save the new GST details in the GSTinDetails model
#                     gstin_details = GSTinDetails.objects.create(**new_gstin_details_response)
#
#                     # Serialize and return the newly created GSTinDetails
#                     serializer = GSTinDetailsSerializer(gstin_details)
#                     if serializer.data:
#                         serializer.data['is_user_exists'] = False
#                         return Response(serializer.data, status=status.HTTP_201_CREATED)
#                     else:
#                         return Response({'success': False, 'message': 'Failed to serialize GSTinDetails'},
#                                         status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#                 else:
#                     return Response({'success': False, 'message': new_gstin_details_response},
#                                     status=status.HTTP_400_BAD_REQUEST)
#         elif len(search_key) == 10:
#             # Check with GSTIN number in GSTinDetails model
#             pan_number = search_key[2:12]
#             gstin_details = GSTinDetails.objects.filter(gstin__contains=pan_number)
#             if gstin_details:
#                 serializer = GSTinDetailsSerializer(gstin_details, many=True)
#                 serializer.data[0]['is_user_exists'] = False
#                 return Response(serializer.data, status=status.HTTP_200_OK)
#         return Response({'success': False, "message": 'Invalid search key'}, status=status.HTTP_400_BAD_REQUEST)

class MyRatingViewSets(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.MyRatingSerializer

    queryset = MyPartner.objects.all()

    def list(self, request, *args, **kwargs):
        user_id = request.user.id
        queryset = MyPartner.objects.filter(business_partner_assoc=user_id)
        serializer = self.serializer_class(queryset, many=True)


        return Response(serializer.data)


class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    queryset = Notification.objects.all()
    permission_classes = (IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        # Get notifications for the logged-in user
        queryset = self.queryset.filter(recipient=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_read = True
        instance.save()
        return Response({'success': True, 'message': 'Notification marked as read'})


class PaymentViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Payments.objects.all()
    serializer_class = PaymentSerializer

    def create(self, request, *args, **kwargs):
        user = request.user
        request.data['user'] = user.id
        request.data['business'] = user.business.id

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'message': 'Transaction created successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'success': False,
                             'message': f'Transaction creation failed. Error is: {get_serilizer_errors(serializer)}'},
                            status=status.HTTP_400_BAD_REQUEST)

class SubscriptionViewSet(viewsets.ViewSet):


    def list(self, request, *args, **kwargs):
        # Get notifications for the logged-in user
        queryset = Subscription.objects.all()
        serializer = SubscriptionSerializer(queryset, many=True)
        return Response({"success": True, "result": serializer.data}, status=status.HTTP_200_OK)