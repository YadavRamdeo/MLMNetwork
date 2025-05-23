from django.contrib import admin
from .models import (
    Member, Plan, Level, RankAndRewards, CompanyWallet, 
    MemberPlan, IncomeHistory, RechargeTransaction, MemberBankDetails
)

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ['user', 'mobile_no', 'status', 'sponsor', 'rank_no', 'total_income', 'joined_on']
    list_filter = ['status', 'rank_no', 'joined_on']
    search_fields = ['user__username', 'user__first_name', 'mobile_no']
    readonly_fields = ['joined_on', 'last_updated']

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'direct', 'matching']

@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ['plan', 'level', 'distributed_amount', 'resale_percentage']
    list_filter = ['plan']

@admin.register(RankAndRewards)
class RankAndRewardsAdmin(admin.ModelAdmin):
    list_display = ['rank_no', 'rank_name', 'pairs', 'royalty', 'amount']
    ordering = ['rank_no']

@admin.register(CompanyWallet)
class CompanyWalletAdmin(admin.ModelAdmin):
    list_display = ['balance', 'charges_balance']
    readonly_fields = ['balance', 'charges_balance']

@admin.register(MemberPlan)
class MemberPlanAdmin(admin.ModelAdmin):
    list_display = ['member', 'plan', 'activated_on', 'is_active']
    list_filter = ['plan', 'is_active', 'activated_on']
    search_fields = ['member__user__username']

@admin.register(IncomeHistory)
class IncomeHistoryAdmin(admin.ModelAdmin):
    list_display = ['member', 'income_type', 'amount', 'created_at']
    list_filter = ['income_type', 'created_at']
    search_fields = ['member__user__username']
    readonly_fields = ['created_at']

@admin.register(RechargeTransaction)
class RechargeTransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'mobile_no', 'amount', 'company_name', 'status', 'recharge_date']
    list_filter = ['status', 'company_name', 'recharge_date']
    search_fields = ['user__username', 'mobile_no', 'order_id']
    readonly_fields = ['recharge_date']

@admin.register(MemberBankDetails)
class MemberBankDetailsAdmin(admin.ModelAdmin):
    list_display = ['member', 'bank_name', 'account_number', 'is_primary']
    list_filter = ['bank_name', 'is_primary']
    search_fields = ['member__user__username', 'account_number']
