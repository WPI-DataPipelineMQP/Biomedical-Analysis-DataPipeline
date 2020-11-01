from django.shortcuts import render
import json

# Create your views here.
def home(request):
	return render(request, 'datapipeline/home.html', {'myCSS': 'home.css'})


def singleStudy(request):
    available_studies = [
		{
			"study_name": "Exercise IQP",
			"description": "Duis ultrices, velit vitae feugiat sagittis, ipsum dolor interdum risus, et pretium tellus nulla vitae quam. Nullam placerat dapibus lorem sit amet cursus. In ac mauris hendrerit, rutrum orci et, bibendum sem. Donec massa nisl, sagittis vel molestie elementum, semper sed leo. Nullam eros nulla, varius eget est quis, condimentum convallis quam. Praesent varius diam non libero ullamcorper, vel pulvinar erat commodo. Quisque tincidunt sollicitudin leo ut viverra."
		},
		{
			"study_name": "Covid",
			"description": "Etiam purus libero, efficitur semper dui vitae, tempus molestie est. Fusce enim tellus, placerat et dolor rutrum, volutpat consectetur ex. In vel nulla accumsan, suscipit quam ac, varius diam. Quisque sed mauris quis nulla mattis sagittis. Etiam fringilla turpis nec nisi luctus elementum. Quisque in sodales elit, sed ornare felis. Quisque eget venenatis est, nec dictum tortor. Donec ultrices odio massa, quis vestibulum nulla blandit non. Cras ut fermentum velit. Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Suspendisse auctor neque id neque bibendum sagittis. Maecenas ac nunc eu risus congue ultricies."
		},
	]
    context = {
		'studies': available_studies,
		'myCSS' : 'singleStudy.css'
	}
    
    print('\nGot Single Study Request\n')
    
    return render(request, 'datapipeline/singleStudy.html', context)



def crossStudy(request):
    available_studies = [
		{
			"study_name": "Exercise IQP",
			"description": "Duis ultrices, velit vitae feugiat sagittis, ipsum dolor interdum risus, et pretium tellus nulla vitae quam. Nullam placerat dapibus lorem sit amet cursus. In ac mauris hendrerit, rutrum orci et, bibendum sem. Donec massa nisl, sagittis vel molestie elementum, semper sed leo. Nullam eros nulla, varius eget est quis, condimentum convallis quam. Praesent varius diam non libero ullamcorper, vel pulvinar erat commodo. Quisque tincidunt sollicitudin leo ut viverra."
		},
		{
			"study_name": "Covid",
			"description": "Etiam purus libero, efficitur semper dui vitae, tempus molestie est. Fusce enim tellus, placerat et dolor rutrum, volutpat consectetur ex. In vel nulla accumsan, suscipit quam ac, varius diam. Quisque sed mauris quis nulla mattis sagittis. Etiam fringilla turpis nec nisi luctus elementum. Quisque in sodales elit, sed ornare felis. Quisque eget venenatis est, nec dictum tortor. Donec ultrices odio massa, quis vestibulum nulla blandit non. Cras ut fermentum velit. Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Suspendisse auctor neque id neque bibendum sagittis. Maecenas ac nunc eu risus congue ultricies."
		},
	]
    context = {
		'studies': available_studies,
		'myCSS' : 'singleStudy.css'
	}
    
    print('\nGot Cross Study Request\n')
    
    return render(request, 'datapipeline/crossStudy.html', context)


def getJSONVersion(raw_list):
    dictionaries = []
    
    for raw_dict in raw_list:
        reformatted = str(raw_dict).replace("'", '"')
        study = json.loads(reformatted)
        dictionaries.append(study)
        
    return dictionaries


def dataSelection(request):
    raw_studies = request.POST.getlist('studies[]')
    studies = getJSONVersion(raw_studies)

    data_categories = [
		{
			"name":"Heart Rate"
		},
		{
			"name":"Corsi"
		},
		{
			"name":"Flanker"
		},
	]
    
    context = {
		'myCSS': 'dataSelection.css',
		'studies': studies,
		'categories': data_categories
	}
    

    # TODO  
    # (1) make queries to get all the data categories from the selected study/studies
    	# (1.1) each data category needs to an object
	# (2) store the collected data categories to the context
		# (2.1) may need to make an inner dictionary to allow for different objects???
			# Potential Problem: How to Automate the listing of the Fields for each data category in the actual html?
				# Idea: Handle the data here and throw back a cleaner data set to work with to the client
    
    print('\nGot Data Selection Request\n')
    
    return render(request, 'datapipeline/dataSelection.html', context)
        