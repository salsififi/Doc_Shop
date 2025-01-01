from django.contrib.auth import get_user_model
from django.db import models
from django.templatetags.static import static
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify


class Product(models.Model):
    """A product in the store"""
    name = models.CharField(max_length=128)
    slug = models.SlugField(max_length=128, blank=True, unique=True)
    price = models.FloatField(default=0.0)
    stock = models.IntegerField(default=0)
    description = models.TextField(blank=True)
    thumbnail = models.ImageField(upload_to="products", blank=True, null=True)
    stripe_id = models.CharField(max_length=90, blank=True)

    class Meta:
        verbose_name = "Produit"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("store:product", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        if not self.slug or self.name != Product.objects.get(pk=self.pk).name:
            base_slug = slugify(self.name)
            slug = base_slug
            i = 1
            while Product.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{i}"
                i += 1
            self.slug = slug
        super().save()

    def thumbnail_url(self):
        if self.thumbnail and hasattr(self.thumbnail, 'url'):
            return self.thumbnail.url
        return static("img/default.jpg")


class Order(models.Model):
    """A product order"""
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    ordered = models.BooleanField(default=False)
    ordered_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = "Commande"

    def __str__(self):
        return f"{self.product} ({self.quantity})"


class Cart(models.Model):
    """A user cart"""
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name="cart")
    orders = models.ManyToManyField(Order)
    nb_products = models.IntegerField(default=0)
    ordered = models.BooleanField(default=False)
    ordered_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = "Panier"

    def __str__(self):
        return f"Panier de {self.user}"

    def delete(self, *args, **kwargs):
        for order in self.orders.all():
            order.ordered = True
            order.ordered_date = timezone.now()
            order.save()
        self.orders.clear()
        super().delete(*args, **kwargs)
