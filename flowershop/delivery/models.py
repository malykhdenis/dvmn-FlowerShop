from django.db import models

# Create your models here.


class Client(models.Model):
    '''Клиент'''
    username = models.CharField(max_length=50,
                                unique=True,
                                blank=True,
                                null=True,
                                verbose_name='username клиента')
    address = models.CharField(max_length=200,
                               blank=True,
                               null=True,
                               verbose_name='адрес клиента (куда доставить)')
    phone_number = models.CharField(max_length=12,
                                    blank=True,
                                    null=True,
                                    verbose_name='номер телефона клиента')

    def __str__(self):
        return self.username


class Reason(models.Model):
    '''Повод'''
    name = models.CharField(max_length=200,
                            blank=True,
                            null=True,
                            verbose_name='Название причины')


class Flower(models.Model):
    '''Цветок'''
    name = models.CharField(max_length=200,
                            blank=True,
                            null=True,
                            verbose_name='Название цветка')


class Bouquet(models.Model):
    '''Букет'''
    title = models.CharField(max_length=200,
                             blank=True,
                             null=True,
                             verbose_name='Название букета')
    reasons = models.ManyToManyField(Reason,
                                     through='BouquetReason',
                                     blank=True,
                                     verbose_name='Поводы')
    flowers = models.ManyToManyField(Flower,
                                     through="BouquetFlower",
                                     blank=True,
                                     verbose_name='Цветы')
    price = models.IntegerField(blank=True,
                                null=True,
                                verbose_name='Цена букета')
    photo = models.ImageField(blank=True,
                              null=True,
                              verbose_name='Фото')


class BouquetReason(models.Model):
    '''Букет по поводу'''
    bouquet = models.ForeignKey(Reason,
                                on_delete=models.CASCADE,
                                blank=True,
                                null=True)
    reason = models.ForeignKey(Reason,
                               on_delete=models.CASCADE,
                               blank=True,
                               null=True)


class BouquetFlower(models.Model):
    '''Букет с цветами'''
    bouquet = models.ForeignKey(Bouquet,
                                on_delete=models.CASCADE,
                                blank=True,
                                null=True,
                                verbose_name='Название букета')
    flower = models.ForeignKey(Flower,
                               on_delete=models.CASCADE,
                               blank=True,
                               null=True)
    amount = models.IntegerField(blank=True,
                                 null=True,
                                 verbose_name='Цена букета')


class Master(models.Model):
    '''Мастер'''
    name = models.CharField(max_length=200,
                            blank=True,
                            null=True,
                            verbose_name='Имя мастера')
    telegram_id = models.IntegerField(blank=True,
                                      null=True,
                                      verbose_name='telegram id мастера')


class Courier(models.Model):
    '''Курьер'''
    name = models.CharField(max_length=200,
                            blank=True,
                            null=True,
                            verbose_name='Имя курьера')
    telegram_id = models.IntegerField(blank=True,
                                      null=True,
                                      verbose_name='telegram id курьера')
    orders_count = models.IntegerField(blank=True,
                                       null=True,
                                       verbose_name='Цена доставки')


class Order(models.Model):
    '''Заказ'''
    client_id = models.ForeignKey(Client,
                                  on_delete=models.CASCADE,
                                  blank=True,
                                  null=True)
    bouquet_id = models.ForeignKey(Bouquet,
                                   on_delete=models.CASCADE,
                                   blank=True,
                                   null=True)
    date_time = models.DateTimeField(null=True,
                                     blank=True,
                                     verbose_name='Время заказа')
    master_id = models.ForeignKey(Master,
                                  on_delete=models.CASCADE,
                                  null=True,
                                  blank=True)
    courier_id = models.ForeignKey(Courier,
                                   on_delete=models.CASCADE,
                                   null=True,
                                   blank=True)
    total_price = models.IntegerField(blank=True,
                                      null=True,
                                      verbose_name='Цена букета c доставкой')
    answer_time = models.TimeField(null=True,
                                   blank=True,
                                   verbose_name='Время ответа')
