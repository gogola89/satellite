from django.urls import path
from app.app_views import accounts_views as views


urlpatterns = [

    path('login/', views.MyTokenObtainPairView.as_view(),
         name='token_obtain_pair'),

    path('checkuser/', views.checkUser, name='check'),

    path('userscount/', views.UsersCount, name='usercount'),

    path('register/', views.registerUser, name='register'),

    path('reset_password/', views.resetPassword, name='reset_password'),

    path('profile/', views.getUserProfile, name="users-profile"),

    path('profile/update/', views.updateUserProfile, name="user-profile-update"),

    path('change_password/', views.changePassword, name="change_password"),

    path('forgot_password/', views.forgotPassword, name='forgot_password'),

    path('', views.getUsers, name="users"),

    path('<str:pk>/', views.getUserById, name='user'),

    path('update/<str:pk>/', views.updateUser, name='user-update'),

    path('delete/<str:pk>/', views.deleteUser, name='user-delete'),

]
