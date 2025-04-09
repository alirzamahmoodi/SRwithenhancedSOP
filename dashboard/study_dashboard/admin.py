from django.contrib import admin
from .models import Study, Transcription

@admin.register(Study)
class StudyAdmin(admin.ModelAdmin):
    list_display = ('study_key', 'status', 'received_timestamp', 'last_updated_timestamp')
    list_filter = ('status',)
    search_fields = ('study_key', 'dicom_path')
    readonly_fields = ('_id', 'received_timestamp', 'last_updated_timestamp') # Usually don't want to edit these
    list_per_page = 50

@admin.register(Transcription)
class TranscriptionAdmin(admin.ModelAdmin):
    list_display = ('study_key', 'transcription_timestamp', 'sr_path')
    search_fields = ('study_key', 'report_text', 'sr_path')
    readonly_fields = ('_id', 'transcription_timestamp')
    list_per_page = 50
    # If you had a ForeignKey link:
    # raw_id_fields = ('study',) 