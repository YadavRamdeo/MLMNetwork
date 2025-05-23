from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.db import transaction
from decimal import Decimal
import json

from .models import (
    Member, Plan, MemberPlan, CompanyWallet, RechargeTransaction, 
    IncomeHistory, RankAndRewards, Level
)
from .forms import UserRegistrationForm, PlanSelectionForm, MobileRechargeForm
from .ewe_functions import (
    generate_username, generate_random_password, send_gmail,
    recharge_mobile, create_order_id
)

def home(request):
    """Home page view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'auth/login.html')

def register(request):
    """User registration view"""
    # Get referral parameters from URL
    sponsor_username = request.GET.get('sponsor')
    position = request.GET.get('position', 'Left')  # Default to Left
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Create user
                    user = form.save(commit=False)
                    if not user.username:
                        user.username = generate_username()
                    user.save()
                    
                    # Create member profile
                    member = Member.objects.get(user=user)
                    member.mobile_no = form.cleaned_data['mobile_no']
                    
                    # Handle sponsor and position
                    sponsor_username = form.cleaned_data.get('sponsor_username') or request.POST.get('sponsor_from_url')
                    position = request.POST.get('position_from_url', 'Left')
                    
                    if sponsor_username:
                        try:
                            sponsor = User.objects.get(username=sponsor_username)
                            member.sponsor = sponsor
                            member.position = position
                            
                            # Place member in sponsor's tree
                            sponsor_member = Member.objects.get(user=sponsor)
                            sponsor_member.place_member(member, position)
                            
                        except User.DoesNotExist:
                            messages.error(request, 'Invalid sponsor username')
                            return render(request, 'auth/register.html', {'form': form})
                    
                    member.save()
                    
                    # Send welcome email
                    try:
                        send_gmail(
                            user.email,
                            'Welcome to EWE MLM Platform',
                            f'Welcome {user.first_name}! Your account has been created successfully. Username: {user.username}'
                        )
                    except Exception as e:
                        pass  # Don't fail registration if email fails
                    
                    messages.success(request, 'Registration successful! You can now login.')
                    return redirect('login')
            except Exception as e:
                messages.error(request, f'Registration failed: {str(e)}')
    else:
        form = UserRegistrationForm()
        # Pre-fill sponsor if coming from referral link
        if sponsor_username:
            form.fields['sponsor_username'].initial = sponsor_username
    
    return render(request, 'auth/register.html', {
        'form': form,
        'sponsor_from_url': sponsor_username,
        'position_from_url': position
    })

@login_required
def dashboard(request):
    """Main dashboard view"""
    try:
        member = request.user.mlm_profile
    except Member.DoesNotExist:
        # Create member if not exists
        member = Member.objects.create(user=request.user)
    
    # Get team counts
    left_team = member.count_team_members('left')
    right_team = member.count_team_members('right')
    
    # Get recent income history
    recent_income = IncomeHistory.objects.filter(member=member).order_by('-created_at')[:5]
    
    # Get current rank
    try:
        current_rank = RankAndRewards.objects.get(rank_no=member.rank_no)
    except RankAndRewards.DoesNotExist:
        current_rank = None
    
    context = {
        'member': member,
        'left_team': left_team,
        'right_team': right_team,
        'recent_income': recent_income,
        'current_rank': current_rank,
    }
    
    return render(request, 'dashboard/dashboard.html', context)

@login_required
def profile(request):
    """User profile view"""
    member = get_object_or_404(Member, user=request.user)
    
    context = {
        'member': member,
    }
    
    return render(request, 'dashboard/profile.html', context)

@login_required
def select_plan(request):
    """Plan selection view"""
    member = get_object_or_404(Member, user=request.user)
    
    # Check if already has active plan
    if member.plans.filter(is_active=True).exists():
        messages.info(request, 'You already have an active plan.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = PlanSelectionForm(request.POST)
        if form.is_valid():
            plan = form.cleaned_data['plan']
            
            # Check if user has sufficient balance
            if member.account_balance >= plan.price:
                try:
                    with transaction.atomic():
                        # Deduct plan price from account balance
                        member.account_balance -= plan.price
                        member.save()
                        
                        # Create member plan
                        member_plan = MemberPlan.objects.create(
                            member=member,
                            plan=plan
                        )
                        
                        # Add to company wallet
                        company_wallet, _ = CompanyWallet.objects.get_or_create(id=1)
                        company_wallet.add_to_wallet(plan.price)
                        
                        messages.success(request, f'Plan {plan.name} activated successfully!')
                        return redirect('dashboard')
                except Exception as e:
                    messages.error(request, f'Plan activation failed: {str(e)}')
            else:
                messages.error(request, 'Insufficient account balance to activate this plan.')
    else:
        form = PlanSelectionForm()
    
    plans = Plan.objects.all()
    context = {
        'form': form,
        'plans': plans,
        'member': member,
    }
    
    return render(request, 'dashboard/select_plan.html', context)

@login_required
def genealogy(request):
    """Genealogy tree view"""
    member = get_object_or_404(Member, user=request.user)
    
    def build_tree(member_obj, depth=0, max_depth=3):
        if depth >= max_depth:
            return None
        
        tree = {
            'member': member_obj,
            'left': None,
            'right': None,
        }
        
        if member_obj.left:
            try:
                left_member = Member.objects.get(user=member_obj.left)
                tree['left'] = build_tree(left_member, depth + 1, max_depth)
            except Member.DoesNotExist:
                pass
        
        if member_obj.right:
            try:
                right_member = Member.objects.get(user=member_obj.right)
                tree['right'] = build_tree(right_member, depth + 1, max_depth)
            except Member.DoesNotExist:
                pass
        
        return tree
    
    tree_data = build_tree(member)
    
    context = {
        'tree_data': tree_data,
        'member': member,
    }
    
    return render(request, 'dashboard/genealogy.html', context)

@login_required
def income_report(request):
    """Income report view"""
    member = get_object_or_404(Member, user=request.user)
    
    # Get income history
    income_history = IncomeHistory.objects.filter(member=member).order_by('-created_at')
    
    # Calculate income by type
    income_by_type = {}
    for income_type, _ in IncomeHistory.INCOME_TYPES:
        income_by_type[income_type] = income_history.filter(income_type=income_type).aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0.00')
    
    context = {
        'member': member,
        'income_history': income_history,
        'income_by_type': income_by_type,
    }
    
    return render(request, 'dashboard/income_report.html', context)

@login_required
def initiate_recharge(request):
    """Mobile recharge view"""
    if request.method == "POST":
        form = MobileRechargeForm(request.POST)
        if form.is_valid():
            mobile_no = form.cleaned_data['mobile_no']
            amount = form.cleaned_data['amount']
            company_name = form.cleaned_data['company_name']
            is_stv = form.cleaned_data['is_stv']
            
            member = get_object_or_404(Member, user=request.user)
            
            if amount > member.wallet_balance:
                messages.error(request, 'Insufficient wallet balance!')
                return render(request, 'service/mobile_recharge/recharge_form.html', {
                    'form': form,
                    'history': RechargeTransaction.objects.filter(user=request.user).order_by("-recharge_date")[:10]
                })
            
            try:
                with transaction.atomic():
                    order_id = create_order_id(10)
                    while RechargeTransaction.objects.filter(order_id=order_id).exists():
                        order_id = create_order_id(10)

                    response = recharge_mobile(mobile_no, amount, company_name, order_id, is_stv)

                    if response.get("status") == 'success':
                        member.wallet_balance -= amount
                        member.save(update_fields=['wallet_balance'])

                        # Calculate and distribute resale income
                        company_wallet, _ = CompanyWallet.objects.get_or_create(id=1)
                        calculate_sharable_amount = amount * 4 / 100  # 4% of amount
                        company_wallet.balance -= calculate_sharable_amount 
                        company_wallet.save()
                        
                        resale_income = calculate_sharable_amount * 50 / 100  # 50% of sharable amount
                        member.wallet_balance += resale_income
                        member.resale_income += resale_income
                        member.save(update_fields=['wallet_balance', 'resale_income'])
                        
                        # Create income history
                        IncomeHistory.objects.create(
                            member=member,
                            income_type='resale_income',
                            amount=resale_income,
                            description=f'Resale income from recharge of {mobile_no}'
                        )

                    # Create transaction record
                    transaction_record = RechargeTransaction.objects.create(
                        user=request.user,
                        mobile_no=mobile_no,
                        amount=amount,
                        company_name=company_name,
                        order_id=order_id,
                        status=response.get("status", "failed"),
                        response_data=response
                    )

                    return render(request, "service/mobile_recharge/recharge_result.html", {
                        "response": response, 
                        "transaction": transaction_record
                    })
            except Exception as e:
                messages.error(request, f'Recharge failed: {str(e)}')
    else:
        form = MobileRechargeForm()

    history = RechargeTransaction.objects.filter(user=request.user).order_by("-recharge_date")[:10]
    return render(request, "service/mobile_recharge/recharge_form.html", {
        "form": form,
        "history": history
    })

# Admin views (basic implementation)
@login_required
def admin_plans(request):
    """Admin plans management"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    plans = Plan.objects.all()
    return render(request, 'admin/plans.html', {'plans': plans})

@login_required
def admin_members(request):
    """Admin members management"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    members = Member.objects.all().order_by('-joined_on')
    return render(request, 'admin/members.html', {'members': members})

# API views for AJAX calls
@login_required
def referral_links(request):
    """Generate referral links for left and right placement"""
    try:
        member = Member.objects.get(user=request.user)
        base_url = request.build_absolute_uri('/auth/register/')
        
        # Generate referral links
        left_link = f"{base_url}?sponsor={request.user.username}&position=Left"
        right_link = f"{base_url}?sponsor={request.user.username}&position=Right"
        
        context = {
            'member': member,
            'left_referral_link': left_link,
            'right_referral_link': right_link,
        }
        return render(request, 'dashboard/referral_links.html', context)
    except Member.DoesNotExist:
        messages.error(request, 'Member profile not found')
        return redirect('dashboard')

@login_required
def api_member_search(request):
    """API endpoint for member search"""
    query = request.GET.get('q', '')
    if len(query) >= 3:
        members = Member.objects.filter(
            user__username__icontains=query
        ).values('user__username', 'user__first_name', 'user__last_name')[:10]
        return JsonResponse({'members': list(members)})
    return JsonResponse({'members': []})
