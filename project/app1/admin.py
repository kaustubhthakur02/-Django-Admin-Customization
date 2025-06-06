from django.contrib import admin
from .models import Product, Order, Category
from django.utils.html import format_html
from django.db.models import Sum
from django.shortcuts import redirect
from django.contrib import messages



@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']
    list_editable = ['is_active']
    list_per_page = 20
    
    # Custom field organization
    fieldsets = (
        ('Category Information', {
            'fields': ('name', 'is_active'),
            'classes': ('wide',)
        }),
    )
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(product_count=Sum('product__stock_quantity'))
    
    def product_count(self, obj):
        return obj.product_count or 0
    product_count.short_description = 'Product Count'

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'image_preview', 'name', 'category', 'price', 
        'stock_status', 'is_featured', 'created_at'
    ]
    list_filter = ['category', 'is_featured', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['price', 'is_featured']
    list_per_page = 20
    
    # Custom field organization
    fieldsets = (
        ('Product Information', {
            'fields': ('name', 'description', 'category', 'image')
        }),
        ('Pricing & Inventory', {
            'fields': ('price', 'stock_quantity', 'is_featured'),
            'classes': ('wide',)
        })
    )
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius: 5px;"/>',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = 'Image'
    
    def stock_status(self, obj):
        if obj.stock_quantity == 0:
            return format_html('<span style="color: red; font-weight: bold;">Out of Stock</span>')
        elif obj.stock_quantity < 10:
            return format_html('<span style="color: orange;">Low Stock ({})</span>', obj.stock_quantity)
        return format_html('<span style="color: green;">In Stock ({})</span>', obj.stock_quantity)
    stock_status.short_description = 'Stock Status'

    def price_display(self, obj):
        return f"Rs{obj.price:.2f}"
    price_display.short_description = 'Price'

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer_email', 'status_display', 'total_amount', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['customer_email', 'id']
    actions = ['mark_as_processing', 'mark_as_shipped']
        
    def status_display(self, obj):
        colors = {
            'pending': 'orange',
            'processing': 'blue', 
            'shipped': 'purple',
            'delivered': 'green'
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.status, 'black'),
            obj.get_status_display()
        )
    status_display.short_description = 'Status'
    
    def mark_as_processing(self, request, queryset):
        updated = queryset.filter(status='pending').update(status='processing')
        messages.success(request, f'{updated} orders marked as processing.')
    mark_as_processing.short_description = "Mark as Processing"
    
    def mark_as_shipped(self, request, queryset):
        updated = queryset.filter(status='processing').update(status='shipped')
        messages.success(request, f'{updated} orders marked as shipped.')
    mark_as_shipped.short_description = "Mark as Shipped"

# Custom admin site title and header
admin.site.site_header = "E-Commerce Admin"
admin.site.site_title = "E-Commerce Admin Portal"
admin.site.index_title = "Welcome to E-Commerce Administration"