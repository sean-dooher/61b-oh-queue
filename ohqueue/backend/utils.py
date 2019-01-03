from django.http import Http404
from django.shortcuts import _get_queryset

def get_latest_object_or_404(klass, *args, **kwargs):
    """
    Uses get().latest() to return object, or raises a Http404 exception if
    the object does not exist.

    klass may be a Model, Manager, or QuerySet object. All other passed
    arguments and keyword arguments are used in the get() query.

    Note: Like with get(), an MultipleObjectsReturned will be raised if more than one
    object is found.
    """
    queryset = _get_queryset(klass)
    try:
        return queryset.filter(*args, **kwargs).latest()
    except queryset.model.DoesNotExist:
        raise Http404('No %s matches the given query.' % queryset.model._meta.object_name)

def get_earliest_object_or_404(klass, *args, **kwargs):
    """
    Uses get().latest() to return object, or raises a Http404 exception if
    the object does not exist.

    klass may be a Model, Manager, or QuerySet object. All other passed
    arguments and keyword arguments are used in the get() query.

    Note: Like with get(), an MultipleObjectsReturned will be raised if more than one
    object is found.
    """
    queryset = _get_queryset(klass)
    try:
        return queryset.filter(*args, **kwargs).earliest()
    except queryset.model.DoesNotExist:
        raise Http404('No %s matches the given query.' % queryset.model._meta.object_name)
