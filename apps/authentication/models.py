from django.db import models
from django.contrib.auth.models import User




class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    forget_password_token = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

def __str__(self):
        return f'{self.user.username}'
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    address = models.CharField(max_length=255, blank=True, null=True)
    
    
    def __str__(self):
        return f'{self.user.username} Profile'
  
class File(models.Model):
    file = models.FileField(upload_to="files")  
    
class TestOrderTable(models.Model):
    # Define your fields for TestOrderTable
    pass


class UploadedCSV(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    csv_file = models.FileField(upload_to='csv_files')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    def __str__(self):
       return f"{self.id} - {self.csv_file.name} - {self.user.username} - {self.uploaded_at}"

class ActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)    
    
    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.timestamp}"


        

  

    