from django.shortcuts import render, get_object_or_404
from django.http import Http404
from .models import Study, Transcription

def study_list(request):
    """Displays a list of all studies."""
    studies = Study.objects.all() # Retrieve all studies, ordered by Meta.ordering
    context = {
        'studies': studies,
        'page_title': 'Transcription Status' # Add a title for the page
    }
    return render(request, 'study_dashboard/study_list.html', context)

def study_detail(request, study_key):
    """Displays details for a specific study and its transcriptions."""
    # Use get_object_or_404 for the main study object
    study = get_object_or_404(Study, study_key=study_key)
    
    # Find related transcriptions using the study_key reference
    # Since we didn't use a ForeignKey in the model for simplicity with Djongo,
    # we filter the Transcription collection directly.
    try:
        transcriptions = Transcription.objects.filter(study_key=study.study_key).order_by('-transcription_timestamp')
    except Transcription.DoesNotExist:
        transcriptions = [] # Handle case where no transcriptions exist yet
        
    context = {
        'study': study,
        'transcriptions': transcriptions,
        'page_title': f'Details for {study.study_key}' # Dynamic title
    }
    return render(request, 'study_dashboard/study_detail.html', context) 