from django.contrib import admin
from product.models import (
    Category, 
    SubCategory, 
    Product, 
    ProductImage, 
    FAQS,
    HeroCarousel,
    ProductColor,
    ContactUs
    )
from product.submodules.order.models import Order
from django import forms
from django.utils.html import format_html

# Beautiful nature-inspired color presets for site themes
PRESET_THEMES = [
  # Earthy & Natural Tones
  { "name": "Forest", "primaryColor": "#2d6a4f", "secondaryColor": "#1b4332", "backgroundColor": "#f1f8f4" },
  { "name": "Mountain", "primaryColor": "#4b5563", "secondaryColor": "#374151", "backgroundColor": "#f8fafc" },
  { "name": "Sand", "primaryColor": "#d4a373", "secondaryColor": "#a98467", "backgroundColor": "#fdfcf7" },
  
  # Water-inspired
  { "name": "Ocean", "primaryColor": "#0077b6", "secondaryColor": "#023e8a", "backgroundColor": "#f0f7fc" },
  { "name": "River", "primaryColor": "#48cae4", "secondaryColor": "#0096c7", "backgroundColor": "#f0faff" },
  { "name": "Lake", "primaryColor": "#219ebc", "secondaryColor": "#126782", "backgroundColor": "#f0f9fc" },
  
  # Sky & Weather
  { "name": "Sunset", "primaryColor": "#fb8500", "secondaryColor": "#e85d04", "backgroundColor": "#fff4e6" },
  { "name": "Sky", "primaryColor": "#4cc9f0", "secondaryColor": "#0077b6", "backgroundColor": "#f0f9ff" },
  { "name": "Dawn", "primaryColor": "#ff9e6d", "secondaryColor": "#ff7b54", "backgroundColor": "#fff5f0" },
  
  # Flora-inspired
  { "name": "Green", "primaryColor": "#40916c", "secondaryColor": "#1b4332", "backgroundColor": "#f1f8f4" },
  { "name": "Brown", "primaryColor": "#a98467", "secondaryColor": "#6c584c", "backgroundColor": "#faf6f2" },
  { "name": "Red", "primaryColor": "#e63946", "secondaryColor": "#9d0208", "backgroundColor": "#fff1f2" },
  
  # Seasonal
  { "name": "Spring", "primaryColor": "#80b918", "secondaryColor": "#55a630", "backgroundColor": "#f4faf0" },
  { "name": "Summer", "primaryColor": "#ffd60a", "secondaryColor": "#faa307", "backgroundColor": "#fffbeb" },
  { "name": "Fall", "primaryColor": "#fb8500", "secondaryColor": "#dc2f02", "backgroundColor": "#fff4e6" },
  { "name": "Winter", "primaryColor": "#90e0ef", "secondaryColor": "#0077b6", "backgroundColor": "#f0f9ff" }
]


'''Registering all the models in admin panel'''

class CategoryInline(admin.TabularInline):
    model = Category
    extra = 1
    fields = ['title', 'created_at']


class SubCategoryInline(admin.TabularInline):
    model = SubCategory
    extra = 1
    fields = ['title', 'created_at']
    max_num = 10

class FAQInline(admin.TabularInline):
    model = FAQS
    extra = 1
    fields = ['question', 'answer']
    max_num = 10

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'caption']
    max_num = 5

class ProductColorInline(admin.TabularInline):
    model = ProductColor
    extra = 1
    fields = ['name', 'hex_code']
    max_num = 5

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    filter_horizontal = ('categories', 'sub_categories')
    inlines = [ProductImageInline,ProductColorInline, FAQInline]
    list_display = ('id', 'title', 'price', 'quantity','created_at', 'hot_deal')
    list_filter  = ('created_at','categories','sub_categories')
    search_fields = ('title',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'created_at']
    list_filter = ('created_at',)

@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'category', 'title', 'created_at']
    list_filter = ('created_at',)

@admin.register(HeroCarousel)
class HeroCarouselAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'created_at']
    list_filter = ('created_at',)


@admin.register(ContactUs)
class ContactUsAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'contact', 'created_at']
    list_filter = ('created_at',)


# @admin.register(Order)
# class OrderAdmin(admin.ModelAdmin):
#     list_display = ['id', 'first_name', 'last_name', 'address_name','total_amount', 'created_at']
#     list_filter = ('created_at',)