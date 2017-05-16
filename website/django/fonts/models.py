from django.db import models
from enum import Enum

# Create your models here.
class FontName(models.Model):
    #A for sans, E for serif, C for calligraphic, and d for decorative
    HUMANIST_SANS = 0
    GEOMETRIC = 1
    GROTESQUE = 2
    NEO_GROTESQUE = 3
    MISC_SANS = 4
    HUMANIST_SERIF = 5
    GARALDE = 6
    TRANSITIONAL = 7
    DIDONE = 8
    MECHANISTIC = 9
    GLYPHIC = 10
    SCRIPT = 11
    MISC_CALLIGRAPHIC = 12
    PIC = 13
    MISC_DECORATIVE = 14


    name = models.CharField(max_length=256)
    filename = models.CharField(max_length=256)
    classification = models.CharField(max_length=256, default=(",".join(["0"]*15)))
    
    def add_classification(self, c):
        clist = self.classification.split(",")
        clist[c] = str(int(clist[c]) + 1)
        self.classification = ",".join(clist)
        
