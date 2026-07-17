"""
URL configuration for LiveProject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from ariadne_django.views import GraphQLView
from django.urls import path

from report_app.resolvers import schema
from report_app.views import token_view


urlpatterns = [
    path("graphql/", GraphQLView.as_view(schema=schema), name="graphql"),
    path("api/token/", token_view, name="token"),
]
