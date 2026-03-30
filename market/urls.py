from django.contrib.admin.views.decorators import staff_member_required
from django.urls import path
from . import views

app_name = 'market'

urlpatterns = [
    path('calculate/', staff_member_required(views.CalculateMarketShareView.as_view()), name='calculate_market_share'),
    path('report/', staff_member_required(views.MarketShareReportView.as_view()), name='market_share_report'),
    path('user-log-details/<int:ebook_id>/<int:user_id>/', staff_member_required(views.UserLogDetailView.as_view()), name='user_log_details'),
]
