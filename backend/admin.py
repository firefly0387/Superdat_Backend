from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.safestring import mark_safe
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from product.models import ContactUs
from product.submodules.order.models import Order


class CustomAdminSite(AdminSite):
    site_header = 'Super Dad'
    site_title = 'Super Dad Admin'
    index_title = 'Welcome to Super Dad Admin Portal'
    
    def get_app_list(self, request):
        """
        Override get_app_list to add unread counts to model names
        """
        app_list = super().get_app_list(request)
        
        # Define models with unread fields and their counts
        unread_counts = {
            'product': {
                'contactus': ContactUs.objects.filter(unread=True).count(),
            },
            'order': {
                'order': Order.objects.filter(unread=True).count(),
            }
        }
        
        # Update app list with unread counts
        for app in app_list:
            if app['app_label'] in unread_counts:
                for model in app['models']:
                    model_name = model['object_name'].lower()
                    if model_name in unread_counts[app['app_label']]:
                        count = unread_counts[app['app_label']][model_name]
                        if count > 0:
                            # Add count to the model name with visual indicator
                            original_name = model['name']
                            model['name'] = mark_safe(
                                f'{original_name} <span class="badge badge-danger badge-pill ml-1" style="font-size: 1em; color: red;">{count}</span>'
                            )
        
        return app_list


# Create custom admin site instance
custom_admin_site = CustomAdminSite(name='custom_admin')

custom_admin_site.register(User, UserAdmin)
custom_admin_site.register(Group, GroupAdmin)

# Register tour models
from product.admin import (
    ProductAdmin, CategoryAdmin, SubCategoryAdmin, HeroCarouselAdmin, ContactUsAdmin,
)
from product.models import (
    Product, Category, SubCategory, HeroCarousel, ContactUs,
)

custom_admin_site.register(Product, ProductAdmin)
custom_admin_site.register(Category, CategoryAdmin)
custom_admin_site.register(SubCategory, SubCategoryAdmin)
custom_admin_site.register(HeroCarousel, HeroCarouselAdmin)
custom_admin_site.register(ContactUs, ContactUsAdmin)

# Register booking models
from product.submodules.order.admin import OrderAdmin

custom_admin_site.register(Order, OrderAdmin)