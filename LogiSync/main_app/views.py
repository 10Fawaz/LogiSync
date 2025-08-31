from django.shortcuts import render,redirect
from django.http import HttpResponseForbidden
from .models import Package,Transport,Destination,Source, TransportType, Container, Profile
from django.views.generic.edit import CreateView,UpdateView,DeleteView 
from django.views.generic import ListView,DetailView
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json


from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import ProfileForm, CreationForm



listOfPackags = [
    {
        "code": "ITEM001",
        "owner": "Alice Johnson",
        "description": "A high-quality leather wallet.",
        "price": 50,
        "weight": 0.2,
        "receivedDate": "2023-08-01"
    },
    {
        "code": "ITEM002",
        "owner": "Bob Smith",
        "description": "Durable running shoes.",
        "price": 75,
        "weight": 1.0,
        "receivedDate": "2023-08-05"
    },
    {
        "code": "ITEM003",
        "owner": "Charlie Brown",
        "description": "Wireless Bluetooth headphones.",
        "price": 100,
        "weight": 0.3,
        "receivedDate": "2023-08-10"
    },
    {
        "code": "ITEM004",
        "owner": "Diana Prince",
        "description": "Smartwatch with health tracking.",
        "price": 150,
        "weight": 0.5,
        "receivedDate": "2023-08-15"
    },
    {
        "code": "ITEM005",
        "owner": "Ethan Hunt",
        "description": "Portable charger for devices.",
        "price": 30,
        "weight": 0.4,
        "receivedDate": "2023-08-20"
    }
]

# Authorization

class DenyCreate:
    def dispatch(self, request, *args, **kwargs):
        profile = getattr(request.user, 'profile', None)
        if profile and profile.role == 'supervisor':
            return HttpResponseForbidden('Supervisor cannot Create new records')
        return super().dispatch(request, *args, **kwargs)
    


# Create your views here.

# home / about 
def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

#Containers
class ContainerCreate(LoginRequiredMixin, DenyCreate, CreateView):

    model = Container


    fields = [  'description', 'weight_capacity','currnt_weight_capacity' ]


    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
    
class ContainerUpdate(LoginRequiredMixin, UpdateView):
    model = Container
    fields = ['description', 'weight_capacity','currnt_weight_capacity']

class ContainerDelete(LoginRequiredMixin, DeleteView):
    model = Container
    success_url = '/'

# def ContainerList(request,container_id):
#     container = Container.objects.get(id=container_id)
#     return render(request,'main_app/container_form.html',{'container':container})

@login_required  
def ContainerDetail(request,container_id):
    container = Container.objects.get(id=container_id)
    packages_doesnt_contain = Package.objects.exclude(inContainer=True)
    packages_exsist =Package.objects.filter(container=container_id) 
    print(packages_doesnt_contain)
    return render(request,'main_app/container_detail.html',{'container':container,'packages':packages_doesnt_contain,'packages_exsist':packages_exsist})

@login_required
def assoc_package(request,container_id,package_id):
    container=Container.objects.get(id=container_id)
    package=Package.objects.get(id=package_id)
    last_weight=container.weight_capacity
    new_weight=container.currnt_weight_capacity + package.weight
    print(new_weight)
    if new_weight>last_weight:
        packages_doesnt_contain = Package.objects.exclude(inContainer=True)
        packages_exsist =Package.objects.filter(container=container_id) 
        return render(request,'main_app/container_detail.html',{'container':container,'packages':packages_doesnt_contain,'packages_exsist':packages_exsist,'msg':'package weigth exceeds limit container weigth!!!'})
    container.currnt_weight_capacity=new_weight
    container.save() 
    package.container=container
    package.inContainer=True
    package.save()
    return redirect('container_detail',container_id=container_id)

@login_required
def unassoc_package(request,container_id,package_id):
    container=Container.objects.get(id=container_id)
    package=Package.objects.get(id=package_id)
    new_weight=container.currnt_weight_capacity - package.weight
    container.currnt_weight_capacity=round(new_weight, 3)
    package.inContainer=False
    package.container=None
    package.save()
    container.save()
    return redirect('container_detail',container_id=container_id)

def ContainerList(request):
    container = Container.objects.all()

    if request.method == "POST":
        searched = request.POST['searched']
        search_result = Container.objects.get(code=searched)

        return render(request, 'main_app/container_list.html', {'search_result': search_result})
    
    return render(request,'main_app/container_list.html',{'containers': container})


def ContainerLocation(request,container_id):
    return render(request,'track/admin_map.html',{'container_id':container_id})
# package
class PackageList(LoginRequiredMixin, ListView):
    model=Package
    def get_queryset(self):
        return Package.objects.filter(user=self.request.user)

class PackageDetails(LoginRequiredMixin, DetailView):
    model=Package

@login_required
def package_create( request):
    profile = getattr(request.user, 'profile', None)
    if profile and profile.role == 'supervisor':
        return HttpResponseForbidden('Supervisor cannot Create new records')
        
    for package in listOfPackags:
        # if(not Package.objects.get(code=package['code'])):
        newPackage = Package(
                code=package['code'],
                owner=package['owner'],
                description=package['description'],
                price=package['price'],
                weight=package['weight'],
                receivedDate=package['receivedDate'],
            )
        newPackage.save()
    return redirect('home')

class PackageUpdate(LoginRequiredMixin, UpdateView):
    model=Package
    fields = ['description','price','weight']

class PackageDelete(LoginRequiredMixin, DeleteView):
    model =Package
    success_url='/'


################## TRANSPORT TYPE ######################
class TransportTypeList(LoginRequiredMixin, ListView):
    models = TransportType
    fields = '__all__'

class TransportTypeCreate(DenyCreate, CreateView):
    model = TransportType
    fields = '__all__'
    template_name = 'main_app/type_form.html'

    def form_valid(self, form):
        self.object = form.save()
        return redirect('transport_type_create') 

class TransportTypeUpdate(LoginRequiredMixin, UpdateView):
    model = TransportType
    fields = ['code']

class TransportTypeDelete(LoginRequiredMixin, DeleteView):
    model = TransportType
    succes_url = '/transports/'

#################### TRANSPORT  ###########################

# class TransportList(LoginRequiredMixin,ListView):
#     model = Transport
#     def get_queryset(self):
#         return Transport.objects.all()
    

class TransportDetails(LoginRequiredMixin,DetailView):
    model = Transport

class TransportCreate(LoginRequiredMixin, DenyCreate, CreateView):
    model = Transport
    # fields = ['name','type','capacity','image','description','destination','source']
    fields = '__all__'
    # template_name = 'transport_form.html'
    
class TransportUpdate(LoginRequiredMixin,UpdateView):
    model = Transport
    fields = ['capacity','description','destination','source']


class TransportDelete(LoginRequiredMixin,DeleteView):
    model = Transport
    success_url = '/transports/'


def TransportList(request):
    transport = Transport.objects.all()

    if request.method == "POST":
        searched = request.POST['searched']
        search_result = Transport.objects.get(name=searched)

        return render(request, 'main_app/transport_list.html', {'search_result': search_result})
    
    return render(request,'main_app/transport_list.html',{'transports': transport})

# def ContainerList(request):
#     container = Container.objects.all()

#     if request.method == "POST":
#         searched = request.POST['searched']
#         search_result = Container.objects.get(code=searched)

#         return render(request, 'main_app/container_list.html', {'search_result': search_result})
    
#     return render(request,'main_app/container_list.html',{'containers': container})


####################  SOURCE  ###########################

class SourceList(LoginRequiredMixin, ListView):
    model = Source

class SourceCreate(LoginRequiredMixin, DenyCreate, CreateView):
    model = Source
    fields = '__all__'

class SourceUpdate(LoginRequiredMixin, UpdateView):
    model = Source
    fields = '__all__'

class SourceDelete(LoginRequiredMixin, DeleteView):
    model = Source
    succes_url = '/transports/'


####################  DESTINATION  ###########################

class DestinationList(LoginRequiredMixin, ListView):
    model = Destination

class DestinationCreate(LoginRequiredMixin,DenyCreate,  CreateView):
    model = Destination
    fields = '__all__'

class DestinationUpdate(LoginRequiredMixin, UpdateView):
    model = Destination
    fields = '__all__'

class DestinationDelete(LoginRequiredMixin, DeleteView):
    model = Destination
    succes_url = '/transports/'

####################  Location  ###########################
# def location_save(reauest):
def map(request):
    return render(request,'track/map.html')

@csrf_exempt
def location_save(request):
    data = json.loads(request.body)
    print(data)
    constiner=Container.objects.get(id=2)
    if not (constiner.latitude == float(data['lat']) and constiner.longitude == float(data['lng'])):
        constiner.longitude=float(data['lng'])
        constiner.latitude=float(data['lat'])
        constiner.save()
        return JsonResponse({'status': 'success', 'message': 'Location saved successfully!'})
    return JsonResponse({'status': 'success', 'message': 'Location exsist'})

@csrf_exempt
def location_load(request):
    data = json.loads(request.body)
    containerId=int(data['id'])
    constiner=Container.objects.get(id=containerId)
    if(constiner.longitude):
        return JsonResponse({'status': 'success','lng':constiner.longitude,'lat':constiner.latitude})
    return JsonResponse({'status': 'faild'})

####################  Auth  ###########################
def signup(request):
    error_message = ''
    if request.method == 'POST':

        form = CreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            role = form.cleaned_data['role']
            Profile.objects.create(user=user, role=role)
            
            login(request, user)
            return redirect('/')
        else:
            error_message = 'Invalid sign up - try again'
    form = CreationForm()
    context = {'form': form, 'error_message': error_message}
    return render(request, 'registration/signup.html', context)

@login_required
def profile_detail(request):
    profile = request.user.profile
    return render(request, 'profile_detail.html', {'profile': profile})

    

@login_required
def edit_profile(request):
    profile, created =Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile_detail')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'profile_edit.html' , {'form': form})

####################    ADDITIONAL FEATURES  ###########################

# def search_transports(request):
#     if request.method == "POST":
#         searched = request.POST['searched']
#         transports = Transport.objects.filter(name__contains=searched)

#         return render(request, 'search_tools/search_transports.html', {'searched': searched, 'transports': transports})

#     else:
#         return render(request,
#         'search_tools/search_transports.html',
#         {})

# def search_containers(request):
#     if request.method == "POST":
#         searched = request.POST['searched']
#         containers = Container.objects.filter(code__contains=searched)

#         return render(request, 'main_app/search_tools/search_containers.html', {'searched': searched, 'containers': containers})

#     else:
#         return render(request,
#         'main_app/search_tools/search_containers.html',
#         {})

