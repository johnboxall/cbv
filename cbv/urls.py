from django.conf import settings
from django.conf.urls import patterns, include, url
# from django.contrib import admin


from cbv.views import *

# admin.autodiscover()


urlpatterns = []

# urlpatterns += patterns("cbv.views",
#     url(r"^$", "home", name="home"),
#     url(r"^about/$", "about", name="about"),
#     url(r'^404$', "handler404", name="404"),
#     url(r"^user/new/$", "user_create", name="user_create"),
#     url(r"^user/detail/(?P<pk>[\w-]+)/$", "user_detail", name="user_detail"),
#     url(r"^user/edit/(?P<pk>[\w-]+)/$", "user_edit", name="user_edit"),
#     url(r"^user/list/$", "user_list", name="user_list"),
# )

urlpatterns += patterns("",
    url(r"^$", Home.as_view(), name="home"),
    url(r"^about/$", About.as_view(), name="about"),
    url(r'^404$', FourOhFour.as_view(), name="404"),
    #  url(r"^user/new/$", UserCreate.as_view(), name="user_create"),
    url(r"^user/new/$", MessageUserCreate.as_view(), name="user_create"),
    url(r"^user/detail/(?P<pk>[\w-]+)/$", UserDetail.as_view(), name="user_detail"),
    url(r"^user/edit/(?P<pk>[\w-]+)/$", MessageUserEdit.as_view(), name="user_edit"),
    url(r"^user/list/$", UserList.as_view(), name="user_list"),

   url(r"^_/$", UserListUserCreate.as_view(), name="_"),
)

# urlpatterns += patterns("",
#     url(r"^admin/", include(admin.site.urls)),
# )




handler404 = "cbv.views.handler404"