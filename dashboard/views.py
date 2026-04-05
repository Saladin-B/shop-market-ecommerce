from django.shortcuts import render

def home(request):
    """Render the home page displaying hero section and product collections."""
    return render(request, "home.html")

def about(request):
    """Render the about page with company story, values, and contact information."""
    return render(request, "about.html") 