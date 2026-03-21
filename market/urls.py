from django.urls import path
from . import views

app_name = 'market'

urlpatterns = [
    path('calculate/', views.CalculateMarketShareView.as_view(), name='calculate_market_share'),
    path('report/', views.MarketShareReportView.as_view(), name='market_share_report'),
    path('user-log-details/<int:ebook_id>/<int:user_id>/', views.UserLogDetailView.as_view(), name='user_log_details'),
]
