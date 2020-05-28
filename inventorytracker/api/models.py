from django.db import models


class System(models.Model):
    name = models.CharField(max_length=100, primary_key=True)
    description = models.TextField(null=True)

    def __str__(self):
        return f"System: {self.name}"


class Part(models.Model):
    name = models.CharField(max_length=100, primary_key=True)
    description = models.TextField(null=True)
    msrp = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    sku = models.CharField(max_length=100, null=True)

    def __str__(self):
        return f"Part: {self.name}--- MSRP: {self.msrp}"


class Component(models.Model):
    name = models.CharField(max_length=100, primary_key=True)
    system = models.ForeignKey(System, on_delete=models.CASCADE)
    description = models.TextField(null=True)

    def __str__(self):
        return f"Component: {self.name}--- (In System: {self.system.name})"


# Joining table used to map components to parts in those components
class PartComponent(models.Model):
    part = models.ForeignKey(Part, on_delete=models.CASCADE)
    component = models.ForeignKey(Component, on_delete=models.CASCADE)

    def __str__(self):
        return f"Part: {self.part.name}--- Component: {self.component.name}"


class Order(models.Model):
    description = models.TextField(null=True)
    order_number = models.CharField(max_length=100, primary_key=True)

    def __str__(self):
        return f"Order ID: #{self.order_number}--- Description: {self.description}"


class OrderItem(models.Model):
    part = models.ForeignKey(Part, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    intake = models.BooleanField()

    def __str__(self):
        return f"Order: {self.order.pk}--- Part: {self.order.name}"

class Seedship(models.Model):
    def __str__(self):
        return f"Seedship: {self.pk}"

class Sensor(models.Model):
    # TODO: This makes it seem like my form is wrong.
    raw_sensors = models.ForeignKey(Seedship, on_delete=models.CASCADE)
    calibration_entity = models.ForeignKey('self', on_delete=models.DO_NOTHING)
    time_range_start = models.BigIntegerField()
    time_range_end = models.BigIntegerField()
    measurement = models.TextField()

    def __str__(self):
        return f"Sensor: {self.seedship_id}--- Calibration: {self.calibration_entity.name}"
