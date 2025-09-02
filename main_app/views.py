from django.shortcuts import render,redirect, get_object_or_404
from django.urls import reverse_lazy
from django.http import HttpResponseForbidden, HttpResponse
from .models import Package,Transport,Destination,Source, TransportType, Container, Profile
from django.views.generic.edit import CreateView,UpdateView,DeleteView 
from django.views.generic import ListView,DetailView
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import ProfileForm, CreationForm, AssignDriverForm
from .utils import generate_sequential_code
import qrcode
from io import BytesIO

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

# Create your views here.

# ----------------------------------------  Authorization  ----------------------------------------


class DenyCreate:
    def dispatch(self, request, *args, **kwargs):
        role = getattr(getattr(request.user, "profile", None), "role", "")
        if not (request.user.is_superuser or role == "supervisor"):
            return redirect('https://www.youtube.com/watch?v=xvFZjo5PgG0')
        return super().dispatch(request, *args, **kwargs)

# home / about 
def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

# ----------------------------------------  Containers  ----------------------------------------

class ContainerCreate(LoginRequiredMixin, DenyCreate, CreateView): 
    allowed_roles=''
    model = Container
    fields = ['description', 'weight_capacity', 'currnt_weight_capacity']
    template_name = 'main_app/container_form.html'
    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.user = self.request.user
        if not obj.code:
            obj.code = generate_sequential_code("C", Container)
        obj.save()
        return super().form_valid(form)
    
class ContainerUpdate(LoginRequiredMixin, DenyCreate,UpdateView):
    model = Container
    fields = ['description', 'weight_capacity','currnt_weight_capacity']

class ContainerDelete(LoginRequiredMixin,DenyCreate, DeleteView):
    model = Container
    success_url = '/'

@login_required
def ContainerDetail(request, container_id):
    container = Container.objects.get(id=container_id)
    packages_doesnt_contain = Package.objects.exclude(inContainer=True)
    packages_exsist = Package.objects.filter(container=container_id)

    role = getattr(getattr(request.user, "profile", None), "role", "")
    is_supervisor = request.user.is_superuser or (role == "supervisor")

    return render(request, 'main_app/container_detail.html', {
        'container': container,
        'packages': packages_doesnt_contain,
        'packages_exsist': packages_exsist,
        'is_supervisor': is_supervisor,
    })


@login_required
def assoc_package(request,container_id,package_id):
    if(request.user.profile.role=='driver'):
        return render(request,'errorDriver.html')
    role = getattr(getattr(request.user, "profile", None), "role", "")
    if not (request.user.is_superuser or role == "supervisor"):
        return HttpResponseForbidden("Only supervisors/admins may modify container packages")
    
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
    if(request.user.profile.role=='driver'):
        return redirect('https://youtu.be/xvFZjo5PgG0?si=IuE07tywqKYoohhA')
    role = getattr(getattr(request.user, "profile", None), "role", "")
    if not (request.user.is_superuser or role == "supervisor"):
        return HttpResponseForbidden("Only supervisors/admins may modify container packages")

    container=Container.objects.get(id=container_id)
    package=Package.objects.get(id=package_id)
    new_weight=container.currnt_weight_capacity - package.weight
    container.currnt_weight_capacity=round(new_weight, 3)
    package.inContainer=False
    package.container=None
    package.save()
    container.save()
    return redirect('container_detail',container_id=container_id)

@login_required
def ContainerList(request):
    containers = Container.objects.all().order_by('code')
    q = request.GET.get('searched', '').strip()
    status = request.GET.get('status')

    if q:
        try:
            search_result = Container.objects.get(code=q)
            return render(request, 'main_app/container_list.html', {'search_result': search_result})
        except Container.DoesNotExist:
            return render(request, 'main_app/container_list.html', {
                'message': 'Container not found, please try again!',
            })

    if status == 'assigned':
        containers = containers.filter(transport__isnull=False)
    elif status == 'unassigned':
        containers = containers.filter(transport__isnull=True)

    return render(request, 'main_app/container_list.html', {'containers': containers})



def ContainerLocation(request,container_id):
    return render(request,'track/admin_map.html',{'container_id':container_id})

# ----------------------------------------  Package  ----------------------------------------

class PackageList(LoginRequiredMixin, ListView):
    model=Package
    def get_queryset(self):
        return Package.objects.filter(user=self.request.user)

class PackageDetails(LoginRequiredMixin, DetailView):
    model=Package

@login_required
def package_create( request):
    if(request.user.profile.role=='driver'):
        return redirect('https://youtu.be/xvFZjo5PgG0?si=IuE07tywqKYoohhA')
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

class PackageUpdate(LoginRequiredMixin,DenyCreate, UpdateView):
    model=Package
    fields = ['description','price','weight']

class PackageDelete(LoginRequiredMixin,DenyCreate, DeleteView):
    model =Package
    success_url='/'


# ----------------------------------------  TRANSPORT TYPE  ----------------------------------------
class TransportTypeList(LoginRequiredMixin, ListView):
    models = TransportType
    fields = '__all__'

class TransportTypeCreate(LoginRequiredMixin,DenyCreate, CreateView):
    model = TransportType
    fields = '__all__'
    template_name = 'main_app/type_form.html'

    def form_valid(self, form):
        self.object = form.save()
        return redirect('transport_type_create') 

class TransportTypeUpdate(LoginRequiredMixin,DenyCreate, UpdateView):
    model = TransportType
    fields = ['code']

class TransportTypeDelete(LoginRequiredMixin,DenyCreate, DeleteView):
    model = TransportType
    succes_url = '/transports/'

    
# ----------------------------------------  TRANSPORT  ----------------------------------------

@login_required
def TransportDetails(request, transport_id):
    transport = Transport.objects.get(id=transport_id)
    container_doesnt_contain = Container.objects.exclude(inTrancport=True)
    container_exsist = Container.objects.filter(transport=transport_id)

    role = getattr(getattr(request.user, "profile", None), "role", "")
    is_supervisor = request.user.is_superuser or (role == "supervisor")

    return render(
        request,
        'main_app/transport_detail.html',
        {
            'transport': transport,
            'container_doesnt_contain': container_doesnt_contain,
            'container_exsist': container_exsist,
            'is_supervisor': is_supervisor,
        }
    )

@login_required
def assoc_container(request, transport_id, container_id):
    if(request.user.profile.role=='driver'):
        return redirect('https://youtu.be/xvFZjo5PgG0?si=IuE07tywqKYoohhA')
    role = getattr(getattr(request.user, "profile", None), "role", "")
    if not (request.user.is_superuser or role == "supervisor"):
        return HttpResponseForbidden("Only supervisors/admins may modify transports")

    transport = Transport.objects.get(id=transport_id)
    container = Container.objects.get(id=container_id)
    last_cap=transport.capacity
    new_cap=transport.currnt_capacity + 1
    print(new_cap)
    if new_cap>last_cap:
        print('here')
        container_doesnt_contain = Container.objects.exclude(inTrancport=True)
        container_exsist = Container.objects.filter(transport_id=transport_id)
        return render(request,'main_app/transport_detail.html',{
            'transport':transport,
            'container':container_doesnt_contain,
            'container_exsist':container_exsist,
            'msg':'containers caps exceeds limit transport cap !!!'
            })
    transport.currnt_capacity=new_cap
    transport.save() 
    container.transport=transport
    container.inTrancport=True
    container.save()
    print('here')
    return redirect('transport_detail',transport_id=transport_id)

@login_required
def unassoc_container(request, transport_id, container_id):
    if(request.user.profile.role=='driver'):
        return redirect('https://youtu.be/xvFZjo5PgG0?si=IuE07tywqKYoohhA')
    role = getattr(getattr(request.user, "profile", None), "role", "")
    if not (request.user.is_superuser or role == "supervisor"):
        return HttpResponseForbidden("Only supervisors/admins may modify transports")

    transport = Transport.objects.get(id=transport_id)
    container = Container.objects.get(id=container_id)
    new_cap=transport.currnt_capacity - 1
    transport.currnt_capacity=round(new_cap, 3)
    container.inTrancport=False
    container.transport=None
    container.save()
    transport.save()
    return redirect('transport_detail',transport_id=transport_id)



class TransportCreate(LoginRequiredMixin,DenyCreate, CreateView):
    model = Transport
    fields = ['name','driver','type','capacity','currnt_capacity','image','description','source','destination']
    template_name = 'main_app/transport_form.html'

    def form_valid(self, form):
        obj = form.save(commit=False)
        if not obj.code:
            type_prefix = (obj.type.code.upper() if obj.type and obj.type.code else "T")
            obj.code = generate_sequential_code(type_prefix, Transport)
        obj.save()
        return super().form_valid(form)
    
class TransportUpdate(LoginRequiredMixin,DenyCreate,UpdateView):
    model = Transport
    fields = ['capacity','description','destination','source']


class TransportDelete(LoginRequiredMixin,DenyCreate,DeleteView):
    model = Transport
    success_url = '/transports/'

def TransportList(request):
    transports = Transport.objects.all()

    is_supervisor = False
    try:
        is_supervisor = (
        request.user.is_superuser or
        (hasattr(request.user, "profile") and request.user.profile.role == "supervisor"))
    except Profile.DoesNotExist:
        is_supervisor = False

    if request.method == "POST" and request.POST.get("action") == "assign_driver":
        form = AssignDriverForm(request.POST)
        if form.is_valid() and is_supervisor:
            t = get_object_or_404(Transport, id=form.cleaned_data["transport_id"])
            t.driver = form.cleaned_data["driver"]
            t.save()
            return redirect("transport_list")

    if request.method == "POST" and request.POST.get("action") == "search":
        searched = request.POST.get('searched', '').strip()
        if searched:
            try:
                search_result = Transport.objects.get(name=searched)
                return render(request, 'main_app/transport_list.html', {'search_result': search_result})
            except Transport.DoesNotExist:
                return render(
                    request,
                    'main_app/transport_list.html',
                    {'message': "Transport is not found, please try again!", 'searched': searched}
                )

    transport_forms = []
    for transport in transports:
        form = AssignDriverForm(initial={"transport_id": transport.id, "driver": transport.driver_id})
        transport_forms.append((transport, form))

    return render(
        request,
        'main_app/transport_list.html',
        {'transport_forms': transport_forms, 'is_supervisor': is_supervisor}
    )

# ----------------------------------------  SOURCE  ----------------------------------------

class SourceList(LoginRequiredMixin, ListView):
    model = Source

class SourceCreate(LoginRequiredMixin, DenyCreate, CreateView):
    model = Source
    fields = ['name', 'location']
    template_name = 'main_app/source_form.html'
    success_url = reverse_lazy('transport_create')
    def form_valid(self, form):
        obj = form.save(commit=False)
        if not obj.code:
            obj.code = generate_sequential_code("SRC", Source)
        obj.save()
        return super().form_valid(form)

class SourceUpdate(LoginRequiredMixin,DenyCreate, UpdateView):
    model = Source
    fields = '__all__'

class SourceDelete(LoginRequiredMixin,DenyCreate, DeleteView):
    model = Source
    succes_url = '/transports/'


# ----------------------------------------  DESTINATION  ----------------------------------------


class DestinationList(LoginRequiredMixin, ListView):
    model = Destination

class DestinationCreate(LoginRequiredMixin,DenyCreate,  CreateView):
    model = Destination
    fields = ['name', 'location'] 
    template_name = 'main_app/destination_form.html'
    success_url = reverse_lazy('transport_create')

    def form_valid(self, form):
        obj = form.save(commit=False)
        if not obj.code:
            obj.code = generate_sequential_code("DST", Destination)
        obj.save()
        return super().form_valid(form)


class DestinationUpdate(LoginRequiredMixin,DenyCreate, UpdateView):
    model = Destination
    fields = '__all__'

class DestinationDelete(LoginRequiredMixin,DenyCreate, DeleteView):
    model = Destination
    succes_url = '/transports/'

    
# ----------------------------------------  Location  ----------------------------------------

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

# ----------------------------------------  Auth  ----------------------------------------

def signup(request):
    if(request.user.profile.role=='driver'):
        return redirect('https://youtu.be/xvFZjo5PgG0?si=IuE07tywqKYoohhA')
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

# ----------------------------------------  ADDITIONAL FEATURES   ----------------------------------------

def qr_code(request, pk):
    transport = Transport.objects.get(pk=pk)

    url = f"https://trello.com/b/zo6OdEIF/logisync" 

    img = qrcode.make(url)

    buffer = BytesIO()
    img.save(buffer, format='PNG')
    return HttpResponse(buffer.getvalue(), content_type="image/png")

