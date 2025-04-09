from djongo import models

class Study(models.Model):
    # Djongo automatically uses MongoDB's _id as the primary key
    _id = models.ObjectIdField()
    study_key = models.CharField(max_length=255, unique=True) # Assuming study_key is unique
    dicom_path = models.CharField(max_length=1024, blank=True, null=True)
    status = models.CharField(max_length=50, default='unknown')
    received_timestamp = models.DateTimeField()
    last_updated_timestamp = models.DateTimeField()
    error_message = models.TextField(blank=True, null=True)

    # Metadata for Djongo
    class Meta:
        # managed = False # Use False if you don't want Django to manage the collection schema (e.g., create/delete)
        db_table = 'studies' # Explicitly set the collection name
        ordering = ['-last_updated_timestamp'] # Default ordering for queries

    def __str__(self):
        return f"{self.study_key} ({self.status})"

class Transcription(models.Model):
    _id = models.ObjectIdField()
    # Use a ForeignKey to link to the Study model/collection
    # Note: Djongo handles foreign keys differently than SQL ORMs.
    # Often, embedding or manual referencing (using study_key) is simpler.
    # Let's stick to referencing by study_key for simplicity here.
    # study = models.ForeignKey(Study, on_delete=models.CASCADE, related_name='transcriptions')
    study_key = models.CharField(max_length=255) # Reference study by its key
    report_text = models.TextField() # Storing report as potentially large text
    # For list storage, consider models.JSONField() if using newer Django/Djongo supporting it,
    # or store as a single text block with delimiters.
    sr_path = models.CharField(max_length=1024, blank=True, null=True)
    transcription_timestamp = models.DateTimeField()

    class Meta:
        # managed = False
        db_table = 'transcriptions'
        indexes = [
            models.Index(fields=['study_key']), # Index for faster lookup by study_key
        ]
        ordering = ['transcription_timestamp']

    def __str__(self):
        return f"Transcription for {self.study_key} at {self.transcription_timestamp}" 