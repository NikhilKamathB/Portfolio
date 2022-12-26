from django.db import models


class Education(models.Model):

    class Meta:
        verbose_name = "Education"
        verbose_name_plural = "Education"
    
    school_name = models.CharField(max_length=250)
    degree = models.CharField(max_length=250)
    gpa = models.CharField(max_length=10)
    coursework = models.TextField(max_length=500, null=True, blank=True)
    address = models.TextField(max_length=500, null=True, blank=True)
    city = models.CharField(max_length=150, null=True, blank=True)
    state = models.CharField(max_length=150, null=True, blank=True)
    country = models.CharField(max_length=150, null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField(max_length=1000, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.school_name


class Work(models.Model):

    class Meta:
        verbose_name = "Work"
        verbose_name_plural = "Work"
    
    company_name = models.CharField(max_length=250)
    designation = models.CharField(max_length=250)
    address = models.TextField(max_length=500, null=True, blank=True)
    skills_used = models.TextField(max_length=500, null=True, blank=True)
    city = models.CharField(max_length=150, null=True, blank=True)
    state = models.CharField(max_length=150, null=True, blank=True)
    country = models.CharField(max_length=150, null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField(max_length=1000, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.company_name


class Project(models.Model):

    class Meta:
        verbose_name = "Project"
        verbose_name_plural = "Projects"
    
    project_title = models.CharField(max_length=250)
    skills_used = models.TextField(max_length=500, null=True, blank=True)
    github_link = models.URLField(max_length=200, null=True, blank=True)
    image = models.ImageField(upload_to="projects/")
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    has_paper = models.BooleanField(default=False)
    paper_link = models.URLField(max_length=200, null=True, blank=True)
    has_patent = models.BooleanField(default=False)
    patent_link = models.URLField(max_length=200, null=True, blank=True)
    description = models.TextField(max_length=1000, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.project_title