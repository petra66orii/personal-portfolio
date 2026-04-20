from django.shortcuts import render
from django.template import TemplateDoesNotExist
from django.template.loader import get_template

def permission_denied_view(request, exception=None):
    return render(request, '403.html', status=403)


def react_frontend_entry(request):
    """
    Serve a prerendered React route when available, otherwise fall back to SPA index.
    """
    normalized_path = request.path.strip("/")
    if normalized_path:
        prerender_template = f"prerender/{normalized_path}/index.html"
    else:
        prerender_template = "prerender/index.html"

    try:
        get_template(prerender_template)
        return render(request, prerender_template)
    except TemplateDoesNotExist:
        return render(request, "index.html")
