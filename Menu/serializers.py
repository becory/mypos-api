from rest_framework import serializers
from Stock.models import Material
from .models import Menu, Week, Status, MenuItem, Recipe


# Create your serializers here.
class MenuSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=10)
    customerAction = serializers.BooleanField(default=True)
    visible = serializers.BooleanField(default=True)


class MenuCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=10)
    customerAction = serializers.BooleanField(default=True)
    visible = serializers.BooleanField(default=True)

    UPDATE_FORBIDDEN = []

    def create(self, validated_data):
        return Menu.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for item in validated_data:
            if item not in self.UPDATE_FORBIDDEN:
                setattr(instance, item, validated_data[item])
        instance.save()
        return instance


class WeekSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=10)

    UPDATE_FORBIDDEN = []

    def create(self, validated_data):
        return Week.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for item in validated_data:
            if item not in self.UPDATE_FORBIDDEN:
                setattr(instance, item, validated_data[item])
        instance.save()
        return instance


class StatusSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=30)
    itemTypeChoices = (('N', 'Normal'), ('W', 'Special Week'), ('S', 'Special'), ('E', 'Weekend'), ('O', 'Off'),)
    itemType = serializers.ChoiceField(choices=itemTypeChoices)
    startDate = serializers.DateField(allow_null=True)
    endDate = serializers.DateField(allow_null=True)
    week = WeekSerializer(many=True)


class StatusCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=30)
    itemTypeChoices = (('N', 'Normal'), ('W', 'Special Week'), ('S', 'Special'), ('E', 'Weekend'), ('O', 'Off'),)
    itemType = serializers.ChoiceField(choices=itemTypeChoices)
    startDate = serializers.DateField(allow_null=True, required=False)
    endDate = serializers.DateField(allow_null=True, required=False)
    week = serializers.PrimaryKeyRelatedField(queryset=Week.objects.all(), many=True, allow_null=True, required=False)

    UPDATE_FORBIDDEN = []

    def create(self, validated_data):
        if 'week' in validated_data:
            weeks = validated_data.pop('week')
        instance = Status.objects.create(**validated_data)
        if weeks:
            instance.week.set(weeks)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        weeks = validated_data.pop('week')
        for item in validated_data:
            if item not in self.UPDATE_FORBIDDEN:
                setattr(instance, item, validated_data[item])
        instance.week.set(weeks)
        instance.save()
        return instance


class RecipeSerializer(serializers.Serializer):
    menuItem = serializers.PrimaryKeyRelatedField(queryset=MenuItem.objects.all())
    material = serializers.PrimaryKeyRelatedField(queryset=Material.objects.all())
    count = serializers.DecimalField(decimal_places=2, max_digits=8)


class RecipeForMenuItemSerializer(serializers.Serializer):
    label = serializers.PrimaryKeyRelatedField(source="material.label", read_only=True)
    material = serializers.PrimaryKeyRelatedField(queryset=Material.objects.all())
    count = serializers.DecimalField(decimal_places=2, max_digits=8)
    unit = serializers.CharField(source="material.unit.sign", read_only=True)


class MenuSetSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=30)
    # menu = MenuSerializer()
    # # image = serializers.ImageField(required=False, allow_empty_file=True)
    # price = serializers.DecimalField(decimal_places=2, max_digits=8)
    # recipes = RecipeForMenuItemSerializer(many=True, allow_null=True)
    # description = serializers.CharField(max_length=50)
    # status = StatusSerializer(default=1)


class MenuItemDashboardSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=30)
    price = serializers.DecimalField(decimal_places=2, max_digits=8)
    menuSet = MenuSetSerializer(many=True)


class MenuItemSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=30)
    menu = MenuSerializer()
    image = serializers.ImageField(required=False, allow_empty_file=True)
    price = serializers.DecimalField(decimal_places=2, max_digits=8)
    recipes = RecipeForMenuItemSerializer(many=True, allow_null=True)
    menuSet = MenuSetSerializer(many=True)
    description = serializers.CharField(max_length=50)
    status = StatusSerializer(default=1)


class MenuItemCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=30)
    menu = serializers.PrimaryKeyRelatedField(queryset=Menu.objects.all())
    # image = serializers.ImageField(required=False, allow_empty_file=True)
    price = serializers.DecimalField(decimal_places=2, max_digits=8)
    recipes = RecipeForMenuItemSerializer(many=True, allow_null=True, required=False)
    menuSet = serializers.PrimaryKeyRelatedField(queryset=MenuItem.objects.all(), allow_null=True, many=True,
                                                 required=False)
    description = serializers.CharField(max_length=50)
    status = serializers.PrimaryKeyRelatedField(queryset=Status.objects.all())

    UPDATE_FORBIDDEN = []

    def create(self, validated_data):
        if 'recipes' in validated_data:
            recipe_list = validated_data.pop('recipes')
        if 'menuSet' in validated_data:
            menu_sets = validated_data.pop('menuSet')
        instance = MenuItem.objects.create(**validated_data)
        if menu_sets:
            instance.menuSet.set(menu_sets)
        instance.save()
        if recipe_list:
            recipe_list = map(lambda item: Recipe(menuItem=instance, **dict(item)), recipe_list)
            Recipe.objects.bulk_create(recipe_list)
            instance.recipes.set(recipe_list)
        return instance

    def update(self, instance, validated_data):
        # print(validated_data)
        if 'recipes' in validated_data:
            recipe_list = validated_data.pop('recipes')
            instance.recipes.all().delete()
            recipe_list = map(lambda item: Recipe(menuItem=instance, **dict(item)), recipe_list)
            Recipe.objects.bulk_create(recipe_list)
        else:
            instance.recipes.all().delete()

        if 'menuSet' in validated_data:
            menu_sets = validated_data.pop('menuSet')
            instance.menuSet.set(menu_sets)
        else:
            instance.menuSet.all().delete()

        for item in validated_data:
            if item not in self.UPDATE_FORBIDDEN:
                setattr(instance, item, validated_data.get(item, getattr(instance, item)))
        instance.save()
        return instance


class MenuItemImageSerializer(serializers.Serializer):
    image = serializers.FileField(required=False, allow_empty_file=True)

    def update(self, instance, validated_data):
        file_obj = validated_data['image']
        file_ext = file_obj.name.split('.')[-1]
        file_obj.name = str(instance.id) + '_' + str(instance.name) + '.' + file_ext
        instance.image = file_obj
        instance.save()
        return instance
