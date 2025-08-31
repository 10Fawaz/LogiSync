    
from django.urls import path, include
from . import views

urlpatterns = [

# -------------------------------------------------------------- home / about --------------------------------------------------------------
    path('',views.home,name='home'),
    path('about/', views.about, name='about'),
    
# -------------------------------------------------------------- containers --------------------------------------------------------------
    path('containers/', views.ContainerList, name='container_list'),
    path('containers/create/', views.ContainerCreate.as_view(), name='container_create' ),
    path('containers/<int:container_id>/', views.ContainerDetail, name='container_detail' ),
    path('containers/<int:container_id>/location', views.ContainerLocation, name='container_location' ),
    path('containers/<int:pk>/update/', views.ContainerUpdate.as_view(), name='container_update' ),
    path('containers/<int:pk>/delete/', views.ContainerDelete.as_view(), name='container_delete' ),

    path('containers/<int:container_id>/assoc_package/<int:package_id>',views.assoc_package,name='assoc_package'),
    path('containers/<int:container_id>/unassoc_package/<int:package_id>',views.unassoc_package,name='unassoc_package'),
    
# -------------------------------------------------------------- Transport --------------------------------------------------------------
    path('transports/',views.TransportList, name='transport_list' ),
    path('transports/create/', views.TransportCreate.as_view(), name='transport_create'),
    path('transports/<int:pk>/', views.TransportDetails.as_view(), name='transport_detail'),
    path('transports/<int:pk>/update/', views.TransportUpdate.as_view(), name='transports_update'),
    path('transports/<int:pk>/delete/', views.TransportDelete.as_view(), name='transports_delete'),

# -------------------------------------------------------------- packages --------------------------------------------------------------
    path('packages/',views.PackageList.as_view(),name='packages_index'),
    path('packages/create',views.package_create,name='packages_create'),
    path('packages/<int:pk>',views.PackageDetails.as_view(),name='packages_detail'),
    path('packages/<int:pk>/delete',views.PackageDelete.as_view(),name='packages_delete'),
    path('packages/<int:pk>/update',views.PackageUpdate.as_view(),name='packages_update'),


# -------------------------------------------------------------- TransportType --------------------------------------------------------------
    path('transporttype/list/', views.TransportTypeList.as_view(), name='transport_type_list'),
    path('transporttype/create/', views.TransportTypeCreate.as_view(), name='transport_type_create'),
    path('transporttype/<int:pk>/update/', views.TransportTypeUpdate.as_view(), name='transport_type_update'),
    path('transporttype/<int:pk>/delete/', views.TransportTypeDelete.as_view(), name='transport_type_delete'),
    
# -------------------------------------------------------------- auth --------------------------------------------------------------
    path('accounts/signup/', views.signup, name='signup'),
    path('profile/', views.profile_detail, name='profile_detail'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),


# -------------------------------------------------------------- features --------------------------------------------------------------
    # path('search_transports', views.search_transports, name='search_transports'),


# -------------------------------------------------------------- locations(testing) --------------------------------------------------------------
    path('location/', views.map, name='map'),

    path('location/save',views.location_save,name='location_save'),
    path('location/load',views.location_load,name='location_load'),
    # path('location/load',views.location_load,name='location_load'),

]