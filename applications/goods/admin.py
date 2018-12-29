from django.contrib import admin

# Register your models here.
from .models import GoodsModel, TagClass, Advertising, MultipleGoods, DetailImage,\
    IntroduceImage, SuccessCaseImage, SingleGoods, SpecificationParameter

admin.site.register(GoodsModel)
admin.site.register(TagClass)
admin.site.register(Advertising)
admin.site.register(MultipleGoods)
admin.site.register(DetailImage)
admin.site.register(IntroduceImage)
admin.site.register(SuccessCaseImage)
admin.site.register(SingleGoods)
admin.site.register(SpecificationParameter)
