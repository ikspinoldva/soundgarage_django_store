from django.contrib import admin
from .models import *


class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}


class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "price", "stock", "available", "category", "digital", "created", "updated"]
    list_filter = ["available", "created", "updated", "category", "digital"]
    list_editable = ["price", "stock", "available"]
    prepopulated_fields = {"slug": ("name",)} #


admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)

admin.site.register(Customer)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(ShippingAddress)


