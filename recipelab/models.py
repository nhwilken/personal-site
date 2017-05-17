from django.db import models
from django.utils import timezone
# Create your models here.


class Recipe(models.Model):
    """
    This is the main list of recipes in the database
    """
    recipe_name = models.CharField(max_length=50)
    recipe_desc = models.TextField(null=True,
                                   blank=True)

    def latest_version(self):
        """
        Returns the next version number for that recipe
        :return:
        """
        # get the next number of version, this method assumes version are ordered
        # by version_num in descending order, so that the latest version is first

        version_list = self.versions.order_by('-version_num')

        if version_list:
            return version_list[0].version_num
        else:
            return 1

    def set_favorite_version(self, v_id):
        """
        sets the version in v_id as the favorite version for this recipe
        :param v_id: 
        :return: 
        """
        self.versions.update(favorite=False)
        self.versions.get(id=v_id).favorite = True


    def __str__(self):
        return self.recipe_name


class Version(models.Model):
    """
    Each version of a recipe will be in this list
    """
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name="versions")
    version_num = models.IntegerField(null=False,
                                      blank=True,
                                      default=0)
    favorite = models.BooleanField(default=False)
    date_created = models.DateTimeField("Date Created",
                                        default=timezone.now)
    # date_updated = models.DateField("Date Updated",
    #                                 default=timezone.now)
    method = models.TextField(blank=True,
                              default= '')
    change_note = models.TextField(blank=True,
                                   null=True)
    result_note = models.TextField(blank=True,
                                   null=True)
    notes = models.TextField(null=True,
                             blank=True)

    def items_as_text(self):

        item_list = []
        for item in self.items.all():
            if item.amount.is_integer():
                amount = int(item.amount)
            else:
                amount = item.amount
            line = [str(amount)]

            if item.unit is not None:
                line.append(item.unit)

            line.append(item.name)

            item_list.append(line)

        try:
            lines = [" ".join(line) for line in item_list]
            item_text = "\r\n".join(lines)
        except TypeError:
            print('There was a type error')
            item_text = ''

        return item_text

    def items_as_dict(self):
        """
        :return: items as dictionary as 'name':[amount, unit] 
        """
        item_dict = {}
        for item in self.items.all():
            item_dict[item.name] = [item.amount, item.unit]

        return item_dict

    def method_as_list(self):
        try:
            method_list = self.method.splitlines()
        except AttributeError:
            method_list = []
        return method_list

    def __str__(self):
        return "%s-%i" % (self.recipe, self.version_num)

    class Meta:
        ordering = ['-version_num']


class ItemList(models.Model):
    """
    The list of items included in a recipe including quantity
    """
    UNIT_TYPES = (
        ('ml', 'ml'),
        ('g', 'g'),
        ('kg', 'kg'),
        ('cup', 'cup'),
        ('None', ''),
        )

    version = models.ForeignKey(Version,
                                related_name="items",
                                on_delete=models.CASCADE)
    name = models.CharField(max_length=100,
                            default="")
    amount = models.FloatField(null=True,
                               default=0)

    unit = models.CharField(max_length=50,
                            choices=UNIT_TYPES,
                            null=True,
                            blank=True,
                            )

    def __str__(self):
        return self.name
