from django.shortcuts import render

# Create your views here.
def data_analysis(request):
	
	return render(request, 'analysis/dataAnalysis.html')