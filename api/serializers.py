import json

from rest_framework import serializers
from django.db.models import Avg
from api.models import MyPartner, ScoreDetails, RaisedDisputes, Notification, Subscription
from users.models import CompanyType, Industry, UserType, User
from users.serializers import GetAssociateUserSerializer,GetMainUserSerializer
from .models import Payments,GSTinDetails
import jsonfield
class ScoreDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        exclude = ('user',)
        model = ScoreDetails

class MyPartnersSerializer(serializers.ModelSerializer):
    business_partner_assoc = GetAssociateUserSerializer()
    score_details = serializers.SerializerMethodField()
    class Meta:
        fields =('__all__')
        model = MyPartner

    def get_score_details(self, obj):
        score_details =  ScoreDetails.objects.get(user=obj.business_partner_assoc)
        score_data = ScoreDetailsSerializer(score_details).data
        return score_data

class AssociatePartnersSerializer(serializers.ModelSerializer):
    business_partner_main = GetAssociateUserSerializer()
    class Meta:
        fields =('__all__')
        model = MyPartner

class RaisedDisputeSerializer(serializers.ModelSerializer):
    # raised_on_user = GetAssociateUserSerializer()
    class Meta:
        fields =('__all__')
        model = RaisedDisputes

class ResolveDisputeSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.id')
    reason = serializers.ReadOnlyField()
    class Meta:
        model = RaisedDisputes
        fields = ['id','user','reason','raised_on', 'response', 'is_resolved','resolved_on']


class MyPartnersPostSerializer(serializers.ModelSerializer):
    class Meta:
        fields =('__all__')
        model = MyPartner
    def create(self, validated_data):
        assoc_partner = MyPartner.objects.create(**validated_data)
        # prev_avg_score = assoc_partner.aggregate(Avg('score'))['score__avg']
        score_details = ScoreDetails.objects.filter(user=assoc_partner.business_partner_assoc.id)

        if score_details:
            score_querset = score_details[0]
            prev_avg_score = score_querset.pres_avg_score
            score_querset.total_partners += 1
            score_querset.pres_avg_score = (score_querset.pres_avg_score + validated_data.get("score"))/score_querset.total_partners
            score_querset.is_raised = False
            if prev_avg_score < score_querset.pres_avg_score:
                score_querset.is_raised = True
            score_querset.prev_avg_score = score_querset.pres_avg_score

        else:
            score_querset = ScoreDetails.objects.create(user=User.objects.get(id=assoc_partner.business_partner_assoc.id))
            score_querset.pres_avg_score = validated_data.get("score",0)
            prev_avg_score = 1
            score_querset.total_partners = 1
            score_querset.prev_avg_score = validated_data.get("score",0)
            score_querset.is_raised = False

        score_querset.raise_or_fall_percentage = (score_querset.pres_avg_score - prev_avg_score)/prev_avg_score
        score_querset.save()
        return assoc_partner
    def update(self, instance, validated_data):
        # assoc_partner = MyPartner.objects.filter(business_partner_assoc=validated_data.get("business_partner_assoc"))
        # prev_avg_score = assoc_partner.aggregate(Avg('score'))['score__avg']
        score_details = ScoreDetails.objects.filter(user=instance.business_partner_assoc.id)
        if score_details:
            score_querset = score_details[0]
            prev_avg_score = score_querset.pres_avg_score
            # score_querset.total_partners += 1
            score_querset.pres_avg_score =  validated_data.get("score")
            score_querset.is_raised = False
            if prev_avg_score < score_querset.pres_avg_score:
                score_querset.is_raised = True
            score_querset.prev_avg_score = score_querset.pres_avg_score
            # if prev_avg_score != 0.0:
            #     score_querset.raise_or_fall_percent = (score_querset.pres_avg_score - prev_avg_score) / prev_avg_score
            # else:
            #     score_querset.raise_or_fall_percent = (score_querset.pres_avg_score - prev_avg_score) / 1
            score_querset.raise_or_fall_percent = score_querset.pres_avg_score - prev_avg_score

            score_querset.save()
            super().update(instance=instance, validated_data=validated_data)
            # instance.update(**validated_data)
            return instance

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('__all__')
        model = CompanyType

class IndustrySerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('__all__')
        model = Industry

class UserTypeSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('__all__')
        model = UserType

class GlobalConfigSerializer(serializers.Serializer):
    company_type = CompanySerializer(many=True)
    industry_type = IndustrySerializer(many=True)
    partner_type = UserTypeSerializer(many=True)
    class Meta:
        fields = ('company_type', 'industry_type','partner_type' )

class MyRatingSerializer(serializers.ModelSerializer):
    business_partner_main = GetAssociateUserSerializer()
    # score_details = serializers.SerializerMethodField()
    class Meta:
        fields =('__all__')
        model = MyPartner

    # def get_score_details(self, obj):
    #     try:
    #         score_details = ScoreDetails.objects.get(user=obj.business_partner_main)
    #         score_data = ScoreMainSerializer(score_details).data
    #
    #         return score_data
    #     except ScoreDetails.DoesNotExist:
    #         raise serializers.ValidationError("Score details not found for this user.")


class ScoreMainSerializer(serializers.ModelSerializer):
    pan_number = serializers.CharField(source='user.pan_number')
    username = serializers.CharField(source='user.first_name')
    class Meta:
        model = ScoreDetails
        fields = '__all__'


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'

class SubscriptionSerializer(serializers.ModelSerializer):
    description = serializers.JSONField()
    class Meta:
        model = Subscription
        fields = '__all__'

class PaymentSerializer(serializers.ModelSerializer):
    payment_amount = serializers.IntegerField(default=1999)

    class Meta:
        model = Payments
        fields = '__all__'

class GSTinDetailsSerializer(serializers.ModelSerializer):
    industry = serializers.JSONField()
    class Meta:
        model = GSTinDetails
        fields = '__all__'