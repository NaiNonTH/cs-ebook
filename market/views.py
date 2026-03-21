from datetime import date
import math
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, TemplateView
from django.db.models import Prefetch
from django.db import connection
from django.contrib.auth.models import User

from ebooks.models import EBook, LogRead
from .models import MarketShare
from .services import calculate_uread_criteria


class CalculateMarketShareView(View):
    def get(self, request):
        # Current month
        current_date = date.today()
        first_day_of_month = current_date.replace(day=1)

        # Get all log reads for calculation up to current month
        # Use existing EBook and LogRead models
        ebooks = EBook.objects.prefetch_related('logread_set').all()
        
        calculated_data = []

        for ebook in ebooks:
            total_pages = ebook.page_count
            if not total_pages or total_pages <= 0:
                continue

            # Group logs by user
            user_pages_map = {}
            for log in ebook.logread_set.all():
                if log.user_id not in user_pages_map:
                    user_pages_map[log.user_id] = []
                user_pages_map[log.user_id].append(log.page_number)

            uread_count = 0
            uread_users = [] # Keep track of who passed
            failed_users = [] # Keep track of who failed
            for user_id, read_pages in user_pages_map.items():
                if calculate_uread_criteria(read_pages, total_pages):
                    uread_count += 1
                    uread_users.append(user_id)
                else:
                    failed_users.append(user_id)
            
            calculated_data.append({
                'ebook_id': ebook.id,
                'title': ebook.title,
                'total_pages': total_pages,
                'uread': uread_count,
                'uread_users': uread_users, # Add list of passing user IDs
                'failed_users': failed_users, # Add list of failing user IDs
                'month': first_day_of_month # Using first day of current month for "reporting month"
            })

        return render(request, 'market/calculate.html', {'calculated_data': calculated_data})

    def post(self, request):
        current_date = date.today()
        first_day_of_month = current_date.replace(day=1)

        ebooks = EBook.objects.prefetch_related('logread_set').all()
        
        for ebook in ebooks:
            total_pages = ebook.page_count
            if not total_pages or total_pages <= 0:
                continue

            user_pages_map = {}
            for log in ebook.logread_set.all():
                if log.user_id not in user_pages_map:
                    user_pages_map[log.user_id] = []
                user_pages_map[log.user_id].append(log.page_number)

            uread_count = 0
            for user_id, read_pages in user_pages_map.items():
                if calculate_uread_criteria(read_pages, total_pages):
                    uread_count += 1
            
            MarketShare.objects.update_or_create(
                ebook=ebook,
                month=first_day_of_month,
                defaults={'uread': uread_count}
            )

        return redirect('market:market_share_report')


class MarketShareReportView(View):
    def get(self, request):
        # Fetch distinct months available in DB
        available_months = MarketShare.objects.dates('month', 'month', order='DESC')

        selected_month_str = request.GET.get('month')
        
        if selected_month_str:
            year, month = map(int, selected_month_str.split('-'))
            selected_month = date(year, month, 1)
        elif available_months.exists():
            selected_month = available_months.first()
        else:
            selected_month = date.today().replace(day=1)
            
        market_data = MarketShare.objects.filter(month=selected_month).select_related('ebook')

        context = {
            'available_months': available_months,
            'selected_month': selected_month,
            'market_data': market_data
        }

        return render(request, 'market/report.html', context)

class UserLogDetailView(View):
    def get(self, request, ebook_id, user_id):
        ebook = get_object_or_404(EBook, id=ebook_id)
        user = get_object_or_404(User, id=user_id)
        
        # Get all distinct pages read by this user for this book IN THE EXACT ORDER THEY READ THEM
        # Instead of sorting or relying on DB distinct which might sort by id or page_number
        # We want to show their chronological reading journey to easily spot jumpers!
        logs = LogRead.objects.filter(ebook=ebook, user=user).order_by('date_time', 'id')
        
        # Build the exact sequence they read (chronological)
        chronological_read_pages = []
        # Keep track of unique read pages just for the stats
        unique_read_pages = set()
        
        for log in logs:
            chronological_read_pages.append(log.page_number)
            unique_read_pages.add(log.page_number)
            
        read_pages_list = list(unique_read_pages)
        
        total_pages = ebook.page_count
        passed = calculate_uread_criteria(read_pages_list, total_pages)
        
        # Calculate stats for the view
        unique_pages_count = len(read_pages_list)
        fifty_percent_required = math.ceil(total_pages * 0.5)
        forty_percent_required = math.ceil(total_pages * 0.4)
        
        context = {
            'ebook': ebook,
            'user': user,
            'chronological_read_pages': chronological_read_pages, # Pass exact reading order
            'passed': passed,
            'unique_pages_count': unique_pages_count,
            'fifty_percent_required': fifty_percent_required,
            'forty_percent_required': forty_percent_required,
        }
        
        return render(request, 'market/user_log_detail.html', context)
