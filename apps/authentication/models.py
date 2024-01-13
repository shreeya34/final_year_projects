from django.db import models
from django.contrib.auth.models import User




class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    forget_password_token = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

def __str__(self):
        return f'{self.user.username}'
  
class File(models.Model):
    file = models.FileField(upload_to="files")  
    
    from django.db import models

class TestOrderTable(models.Model):
    # Define your fields for TestOrderTable
    pass

class UploadedCSV(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    csv_file = models.FileField(upload_to='csv_files')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"UploadedCSV: {self.csv_file.name} by {self.user.username}"
  

    