from django.db import models

class OtherCompetition(models.Model):
    
    Name = models.CharField(max_length=500)
    LogoPath = models.CharField(max_length=500, blank=True, null=True)
    Description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return " ".join([self.Name])