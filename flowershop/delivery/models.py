from django.db import models

# Create your models here.


class Client(models.Model):
    '''Клиент'''
    username = models.CharField(max_length=50,
                                unique=True,
                                verbose_name='username клиента')
    address = models.CharField(max_length=200,
                               verbose_name='адрес клиента (куда доставить)')
    phone_number = models.CharField(max_length=12,
                                    verbose_name='номер телефона клиента')

    def __str__(self):
        return self.username


class Reason(models.Model):
    '''Повод'''
    name = models.CharField(max_length=200,
                            verbose_name='Название причины')


class BouquetReason(models.Model):
    '''Букет по поводу'''
    # bouquet = models.CharField('Название причины',
    #                         max_length=200)
    reason = models.ForeignKey(Reason, on_delete=models.CASCADE)


class Flower(models.Model):
    '''Цветок'''
    name = models.CharField(max_length=200,
                            verbose_name='Название цветка')


class BouquetFlower(models.Model):
    '''Букет с цветами'''
    # bouquet = models.CharField('Название букета',
    #                         max_length=200)
    flower = models.ForeignKey(Flower, on_delete=models.CASCADE)
    amount = models.IntegerField()


class Bouquet(models.Model):
    '''Букет'''
    title = models.CharField(max_length=200,
                             verbose_name='Название букета')
    reasons = models.ForeignKey(BouquetReason, on_delete=models.CASCADE)
    flowers = models.ForeignKey(BouquetFlower, on_delete=models.CASCADE)
    price = models.IntegerField()
    photo = models.ImageField(blank=True,
                              verbose_name='Фото')


class Master(models.Model):
    name = models.CharField(max_length=200,
                            verbose_name='Имя мастера')
    telegram_id = models.IntegerField()


class Courier(models.Model):
    name = models.CharField(max_length=200,
                            verbose_name='Имя курьера')
    telegram_id = models.IntegerField()
    orders_count = models.IntegerField()


class Order(models.Model):
    '''Заказ'''
    client_id = models.ForeignKey(Client, on_delete=models.CASCADE)
    bouquet_id = models.ForeignKey(Bouquet, on_delete=models.CASCADE)
    date_time = models.DateTimeField()
    master_id = models.ForeignKey(Master, on_delete=models.CASCADE)
    courier_id = models.ForeignKey(Courier, on_delete=models.CASCADE)
    total_price = models.IntegerField()
    answer_time = models.TimeField()
