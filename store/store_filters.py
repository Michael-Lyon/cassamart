import django_filters

from store.models import Checkout, Product


class OrderFilter(django_filters.FilterSet):
    product = django_filters.CharFilter(
        field_name='cart__items__title', lookup_expr='icontains')


    class Meta:
        model = Checkout
        fields = ['status', 'received_status', 'product']


class ProductFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains')
    price = django_filters.RangeFilter()
    stock = django_filters.NumberFilter()
    available = django_filters.BooleanFilter()
    created = django_filters.DateFromToRangeFilter()
    updated = django_filters.DateFromToRangeFilter()

    class Meta:
        model = Product
        fields = ['title', 'price', 'stock', 'available', 'created', 'updated']







# import django_filters
# from django.db.models import Q
# from .models import Checkout, CartItem


# class OrderFilter(django_filters.FilterSet):
#     cart__items = django_filters.ModelMultipleChoiceFilter(
#         queryset=CartItem.objects.all(),
#         conjoined=True,
#         to_field_name='product__title',
#         label='product'
#     )

#     def filter_cart__items(self, queryset, name, value):
#         query = Q()
#         for item_title in value:
#             query |= Q(cart__items__product__title__icontains=item_title)
#         return queryset.filter(query).distinct()

#     class Meta:
#         model = Checkout
#         fields = {
#             'status': ['exact'],
#             'created': ['date__range'],
#             'received_status': ['exact'],
#             'cart__items': ['icontains'],
#         }
