from django.shortcuts import redirect


def redirect_root_view(request):
    return redirect('courseinfo_section_list_urlpattern')