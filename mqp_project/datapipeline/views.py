from django.shortcuts import render

# Create your views here.
def home(request):
	return render(request, 'datapipeline/home.html', {'myCSS': 'home.css'})


def singleStudy(request):
    available_studies = [
		{
			'study_name': 'Exercise IQP',
			'description': 'Duis ultrices, velit vitae feugiat sagittis, ipsum dolor interdum risus, et pretium tellus nulla vitae quam. Nullam placerat dapibus lorem sit amet cursus. In ac mauris hendrerit, rutrum orci et, bibendum sem. Donec massa nisl, sagittis vel molestie elementum, semper sed leo. Nullam eros nulla, varius eget est quis, condimentum convallis quam. Praesent varius diam non libero ullamcorper, vel pulvinar erat commodo. Quisque tincidunt sollicitudin leo ut viverra.'
		},
		{
			'study_name': 'Covid',
			'description': 'Etiam purus libero, efficitur semper dui vitae, tempus molestie est. Fusce enim tellus, placerat et dolor rutrum, volutpat consectetur ex. In vel nulla accumsan, suscipit quam ac, varius diam. Quisque sed mauris quis nulla mattis sagittis. Etiam fringilla turpis nec nisi luctus elementum. Quisque in sodales elit, sed ornare felis. Quisque eget venenatis est, nec dictum tortor. Donec ultrices odio massa, quis vestibulum nulla blandit non. Cras ut fermentum velit. Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Suspendisse auctor neque id neque bibendum sagittis. Maecenas ac nunc eu risus congue ultricies.'
		},
	]
    context = {
		'studies': available_studies,
		'myCSS' : 'singleStudy.css'
	}
    
    test = request.POST.getlist('tag[]')
    print(test)
    
    print('Got Single Study Request')
    
    return render(request, 'datapipeline/singleStudy.html', context)



def crossStudy(request):
    available_studies = [
		{
			'study_name': 'Exercise IQP',
			'description': 'Duis ultrices, velit vitae feugiat sagittis, ipsum dolor interdum risus, et pretium tellus nulla vitae quam. Nullam placerat dapibus lorem sit amet cursus. In ac mauris hendrerit, rutrum orci et, bibendum sem. Donec massa nisl, sagittis vel molestie elementum, semper sed leo. Nullam eros nulla, varius eget est quis, condimentum convallis quam. Praesent varius diam non libero ullamcorper, vel pulvinar erat commodo. Quisque tincidunt sollicitudin leo ut viverra.'
		},
		{
			'study_name': 'Covid',
			'description': 'Etiam purus libero, efficitur semper dui vitae, tempus molestie est. Fusce enim tellus, placerat et dolor rutrum, volutpat consectetur ex. In vel nulla accumsan, suscipit quam ac, varius diam. Quisque sed mauris quis nulla mattis sagittis. Etiam fringilla turpis nec nisi luctus elementum. Quisque in sodales elit, sed ornare felis. Quisque eget venenatis est, nec dictum tortor. Donec ultrices odio massa, quis vestibulum nulla blandit non. Cras ut fermentum velit. Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Suspendisse auctor neque id neque bibendum sagittis. Maecenas ac nunc eu risus congue ultricies.'
		},
	]
    context = {
		'studies': available_studies,
		'myCSS' : 'singleStudy.css'
	}
    
    test = request.POST.getlist('tag[]')
    print(test)
    
    print('Got Cross Study Request')
    
    return render(request, 'datapipeline/crossStudy.html', context)