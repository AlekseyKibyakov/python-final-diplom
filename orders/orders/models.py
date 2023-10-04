from django.db import models


class User(models.Model):
    name = models.CharField(max_length=60)
    email = models.EmailField(unique=True)
    
    def __str__(self):
        return self.name


class Contact(models.Model):
    user = models.ForeignKey(User, related_name='contacts',
                             blank=True, on_delete=models.CASCADE)
    city = models.CharField(max_length=100)
    street = models.CharField(max_length=100)
    house = models.CharField(max_length=15)
    apartment = models.CharField(max_length=15, blank=True)
    phone = models.PhoneNumberField()
    
    def __str__(self):
        return f'{self.city} {self.street} {self.house} {self.apartment} - {self.phone}'


class Shop(models.Model):
    name = models.CharField(max_length=60)
    url = models.URLField(blank=True, null=True)
    
    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=60)
    shops = models.ManyToManyField(Shop, related_name='categories', blank=True)
    
    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=60)
    category = models.CharField(max_length=60)
    
    def __str__(self):
        return self.name


class ProductInfo(models.Model):
    product = models.ForeignKey(Product, related_name='product_infos', blank=True,
                                on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, related_name='product_infos', blank=True,
                                on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.PositiveIntegerField()
    price_rrc = models.PositiveIntegerField()
    
    def __str__(self):
        return self.name


class Parameter(models.Model):
    name = models.CharField(max_length=40)

    def __str__(self):
        return self.name


class ProductParameter(models.Model):
    product_info = models.ForeignKey(ProductInfo, related_name='product_parameters',
                                     blank=True, on_delete=models.CASCADE)
    parameter = models.ForeignKey(Parameter, related_name='product_parameters',
                                  blank=True, on_delete=models.CASCADE)
    value = models.CharField(max_length=100)


class Order(models.Model):
    user = models.ForeignKey(User, related_name='orders',
                             blank=True, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    state = models.BooleanField()
    contact = models.ForeignKey(Contact, blank=True, null=True,
                                on_delete=models.CASCADE)
    
    def __str__(self):
        return str(self.dt)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='ordered_items',
                              blank=True, on_delete=models.CASCADE)

    product_info = models.ForeignKey(ProductInfo, related_name='ordered_items',
                                     blank=True, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
