from django.shortcuts import render

# Create your views here.
def home(request):
	return render(request, 'datapipeline/home.html', {'myCSS': 'home.css'})