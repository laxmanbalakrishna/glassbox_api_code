from rest_framework.routers import DefaultRouter
from . import views
router = DefaultRouter()
router.register(r'myRatings', views.MyRatingViewSets, basename='myRatings')
router.register(r'myPartners', views.MyPartnersViewSet, basename='myPartners')
router.register(r'globalConfig', views.GlobalConfigViewSet, basename='globalConfig')
router.register(r'searchPartner', views.SearchPartnerViewSet, basename='searchPartner')
router.register(r'gstSearch', views.GSTSearchViewSet, basename='gstSearch')
router.register('getPartnerRatings', views.GetPartnerRatingViewSet, basename='getPartnerRatings')
router.register('subscriptions', views.SubscriptionViewSet, basename='subscriptions')
router.register('raiseDispute', views.DisputeViewSet, basename='disputes')
router.register(r'notifications', views.NotificationViewSet,basename='notifications')
router.register(r'payments', views.PaymentViewSet,basename='payments')




urlpatterns = router.urls