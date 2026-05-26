from django.db import models
from ckeditor.fields import RichTextField
from django.db.models import Q, UniqueConstraint

class Category(models.Model):
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
class SubCategory(models.Model):
    title = models.CharField(max_length=255)
    category = models.ForeignKey(Category, related_name='subcategories', on_delete=models.CASCADE)
    image = models.ImageField(upload_to="subcategory/image", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
class Product(models.Model):
    categories = models.ManyToManyField(Category, related_name='products_category', null=True, blank=True)
    sub_categories = models.ManyToManyField(SubCategory, related_name='products_subcategory', null=True, blank=True)
    title = models.CharField(max_length=255)
    description = RichTextField(blank=True, null=True)
    sub_description = RichTextField(blank=True, null=True)
    quantity = models.PositiveIntegerField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_per = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    average_rating = models.FloatField(null=True, blank=True)
    image = models.ImageField(upload_to="product/image", null=True, blank=True)
    add_image = models.ImageField(upload_to="product/image", null=True, blank=True)
    hot_deal = models.BooleanField(default=False, )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
    def update_average_rating(self):
        """
        Updates the average_rating of a TourPackage based on the ratings of all its reviews.
        
        This method is called when a Review is created or updated. It calculates the new average
        rating of the TourPackage and saves it to the model.
        """
        avg = Review.objects.filter(
        product=self
    ).aggregate(avg_rating=models.Avg('rating'))['avg_rating']
        self.average_rating = avg or 0
        self.save(update_fields=['average_rating'])

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product/image', null=True, blank=True)
    caption = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        from django.core.exceptions import ValidationError
        if not self.image :
            raise ValidationError("An image must be provided.")

class ProductColor(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='Product_colors')
    name = models.CharField(max_length=50)
    hex_code = models.CharField(max_length=7)

    def __str__(self):
        return self.name
        
class FAQS(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_faqs', null=True, blank=True)
    question = RichTextField()
    answer = RichTextField()
    created_at =  models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "FAQS"
        verbose_name_plural = "FAQS"
        ordering = ['-created_at']

    def __str__(self):
        """
        Returns a string representation of the FAQS, which is the question and answer.

        This method is called when a string representation of the object is needed.
        For example, when printing the object, or when using it in a template.

        Returns:
            str: The question and answer of the FAQS.
        """
        return f"{self.question} - {self.answer}"
 
class Review(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_reviews', null=True, blank=True)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    image = models.ImageField(upload_to="review/image", null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    rating = models.IntegerField(choices=RATING_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
        UniqueConstraint(
            fields=['product', 'email'],
            condition=Q(product__isnull=False),
            name='unique_product_review_per_email'
        )
    ]
        ordering = ['-created_at']

    def __str__(self):
        """
        Returns a string representation of the Review, which includes the reviewer's name and the date the review was created.

        This method is called when a string representation of the object is needed.
        For example, when printing the object, or when using it in a template.

        Returns:
            str: The name of the reviewer and the creation date of the review.
        """

        return f'Review by {self.name} on {self.created_at}'
    
    def save(self, *args, **kwargs):
        """
        Saves the Review to the database.

        Calls the parent's save method then updates the average rating of the related
        TourPackage or RentalPackage if it exists. 

        Args:
            *args: The positional arguments to pass to the parent's save method.
            **kwargs: The keyword arguments to pass to the parent's save method.
        """
        super().save(*args, **kwargs)
        if self.product and hasattr(self.product, 'update_average_rating'):
            self.product.update_average_rating()

    def delete(self, *args, **kwargs):
        """
        Deletes the Review from the database.

        Calls the parent's delete method then updates the average rating of the related
        TourPackage or RentalPackage if it exists.

        Args:
            *args: The positional arguments to pass to the parent's delete method.
            **kwargs: The keyword arguments to pass to the parent's delete method.
        """
        super().delete(*args, **kwargs)
        if self.product and hasattr(self.product, 'update_average_rating'):
            self.product.update_average_rating()
        

class HeroCarousel(models.Model):
    title = models.CharField(max_length=255)
    description = RichTextField(blank=True, null=True)
    image = models.ImageField(upload_to="hero/carousel/image", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
class ContactUs(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    contact = models.IntegerField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.contact}"
    

    class Meta:
        verbose_name = "Contact us"
        verbose_name_plural = "Contact us"
        ordering = ['-created_at']