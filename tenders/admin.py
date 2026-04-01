from django.contrib import admin
from .models import Tender
from .models import Prequalification
from .models import Institution, Category

@admin.register(Prequalification)
class PrequalificationAdmin(admin.ModelAdmin):
    list_display = ("company_name", "vendor", "category", "status", "applied_at")
    list_filter = ("status", "category")
    search_fields = ("company_name",)


# ===============================
# INSTITUTION ADMIN
# ===============================
@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    search_fields = ['name']


# ===============================
# CATEGORY ADMIN
# ===============================
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ['name']


# ===============================
# TENDER ADMIN (🔥 UPGRADED)
# ===============================
@admin.register(Tender)
class TenderAdmin(admin.ModelAdmin):

    list_display = ('title', 'institution', 'category', 'deadline')
    list_filter = ('institution', 'category', 'deadline')
    search_fields = ('title', 'description')

    # 🔥 This makes dropdown searchable
    autocomplete_fields = ['institution', 'category']