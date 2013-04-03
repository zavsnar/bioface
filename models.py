

# from django.db import models
# from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# class MyUserManager(BaseUserManager):
#     def create_user(self, email, first_name, last_name, patronymic, password=None):
#         if not email:
#             raise ValueError('Users must have an email address')
        
#         user = self.model(
#             email=MyUserManager.normalize_email(email),
#             first_name=first_name,
#             last_name=first_name,
#             patronymic=patronymic,
#         )
        
#         user.set_password(password)
#         user.save(using=self._db)
        
#         return user
    
#     def create_superuser(self, username, first_name, last_name, patronymic, password=None):
#         user = self.create_user(
#             username,
#             password=password,
#             first_name=first_name,
#             last_name=last_name,
#             patronymic=patronymic,
#         )
        
#         user.is_admin = True
#         user.save(using=self._db)
#         return user


# class MyUser(AbstractBaseUser):
#     email = models.CharField(u'login', max_length=75)
#     first_name = models.CharField(u'first_name', max_length=30)
#     last_name = models.CharField(u'last_name', max_length=30)
#     patronymic = models.CharField(u'patronymic', max_length=50)
#     is_active = models.BooleanField(default=True)
#     is_admin = models.BooleanField(default=False)
    
#     objects = MyUserManager()
    
#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = ['first_name', 'last_name', 'patronymic']
    
#     def get_full_name(self):
#         return u'%s %s %s' % (self.first_name, self.patronymic, self.last_name)

#     def get_short_name(self):
#         return u'%s' % self.first_name
    
#     def __unicode__(self):
#         return self.email
    
#     def has_perm(self, perm, obj=None):
#         return True

#     def has_module_perms(self, app_label):
#         return True

#     @property
#     def is_staff(self):
#         return self.is_admin