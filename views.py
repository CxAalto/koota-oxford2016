from django.shortcuts import render

from django.contrib.auth.decorators import login_required
import django.template
engine = django.template.engines['django']
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.html import escape
from django.utils.safestring import mark_safe

# Create your views here.

from kdata import devices
from kdata import models
from kdata.facebook import Facebook
from kdata.twitter import Twitter
from kdata.instagram import Instagram
from kdata.aware import AwareDevice, AwareDeviceValidCert


class BaseAction(object):
    def __init__(self, request):
        self.user = request.user
        self.request = request
    def __str__(self):
        return self.__class__.__name__
    def _qs(self):
        return models.Device.objects.filter(user=self.user,
                                            type=self.devtype,
                                            label__slug='primary')
    def exists(self):
        return self._qs().count() == 1
    def render(self):
        dev = self._qs().get()
        template = self.template

        template = engine.from_string(template)
        context = { }
        context.update(self.__dict__)
        context.update(locals())
        import django.template.context_processors as cp
        text = template.render(context=context, request=self.request)

        return text

    def load(self):
        pass


class LinkFacebook(BaseAction):
    devtype = Facebook.pyclass_name()
    name = 'Facebook'
    heading = 'Facebook'
    uname = 'Facebook'
    template = """\
{% if dev.status == 'linked'%}
Your account is linked, thank you!

{% elif dev.status == 'donthave' %}

So you don't have a account, that's OK.  If you do get an
account, you can <a href="{% url 'facebook-link' public_id=dev.public_id%}">link it here</a>.

{% else%}

Please link your facebook account, if you have one.  If you don't have
an account, that's OK, just let us know so we don't bug you anymore.

<p>
  <form method="post" style="display: inline" action="{% url 'facebook-link' public_id=dev.public_id%}">{%csrf_token%}
    <button type="submit" class="btn btn-xs btn-primary">Link Facebook</button>
  </form>
  <form method="post" style="display: inline" action="{% url 'mark-device-dont-have' public_id=dev.public_id %}">{%csrf_token%}
    <button type="submit" class="btn btn-xs">I don't have a Facebook account</button>
  </form>
  <form method="post" style="display: inline" action="{% url 'mark-device-not-linking' public_id=dev.public_id %}">{%csrf_token%}
    <input type="hidden" name="next" value="{{request.path}}">
    <button type="submit" class="btn btn-xs">I'd rather not link now</button>
  </form>
</p>


{% endif %}
"""

class LinkTwitter(LinkFacebook):
    heading = "Twitter"
    devtype = Twitter.pyclass_name()
    template = """\
{% if dev.status == 'linked'%}
Your account is linked, thank you!

{% elif dev.status == 'donthave' %}

So you don't have an account, that's OK.  If you do get an
account, you can <a href="{% url 'facebook-link' public_id=dev.public_id%}">link it here</a>.

{% else%}

Please link your account, if you have one.  If you don't have
an account, that's OK, just let us know so we don't bug you anymore.


<p>
  <form method="post" style="display: inline" action="{% url 'twitter-link' public_id=dev.public_id%}">{%csrf_token%}
    <button type="submit" class="btn btn-xs btn-primary">Link Twitter</button>
  </form>
  <form method="post" style="display: inline" action="{% url 'mark-device-dont-have' public_id=dev.public_id %}">{%csrf_token%}
    <button type="submit" class="btn btn-xs">I don't have a Twitter account</button>
  </form>
  <form method="post" style="display: inline" action="{% url 'mark-device-not-linking' public_id=dev.public_id %}">{%csrf_token%}
    <button type="submit" class="btn btn-xs">I'd rather not link now</button>
  </form>
</p>

{% endif %}
"""

class LinkInstagram(LinkFacebook):
    heading = "Instagram"
    devtype = Instagram.pyclass_name()
    template = """\
{% if dev.status == 'linked'%}
Your account is linked, thank you!

{% elif dev.status == 'donthave' %}

So you don't have a twitter account, that's OK.  If you do get an
account, you can <a href="{% url 'facebook-link' public_id=dev.public_id%}">link it here</a>.

{% else%}

Please link your account, if you have one.  If you don't have
an account, that's OK, just let us know so we don't bug you anymore.

<p>
  <form method="post" style="display: inline" action="{% url 'instagram-link' public_id=dev.public_id%}">{%csrf_token%}
    <button type="submit" class="btn btn-xs btn-primary">Link Instagram</button>
  </form>
  <form method="post" style="display: inline" action="{% url 'mark-device-dont-have' public_id=dev.public_id %}">{%csrf_token%}
    <button type="submit" class="btn btn-xs">I don't have an Instagram account</button>
  </form>
  <form method="post" style="display: inline" action="{% url 'mark-device-not-linking' public_id=dev.public_id %}">{%csrf_token%}
    <button type="submit" class="btn btn-xs">I'd rather not link now</button>
  </form>
</p>


{% endif %}
"""


class LinkAware(BaseAction):
    heading = "Your phone"
    template = """\
{% if android.has_data or ios.has_data%}

Your phone has been linked, thank you!

{% else %}


<p>Please link either your Android or iOS device.  Once it is linked and
some data has arrived, when you refresh the page it will tell you.</p>


<div class="container-fluid">
<div class=row>


<div class="col-md-6">
  <div class="panel panel-default">
    <div class="panel-heading">
      <h4>Android</h4>
    </div>
    <div class="panel-body">

      <p>Search for "Aware Framework" in the Google Play store and
      install this app.  Open it, and scan this QR code:</p>

      <img src="{% url 'aware-register-qr' public_id=android.public_id %}" style="width: 10em;">

      <p>Manual config URL: {{ android.get_class.qrcode_url }}</p>
    </div>
  </div>
</div>


<div class="col-md-6">
  <div class="panel panel-default">
    <div class="panel-heading">
      <h4>iOS</h4>
    </div>
    <div class="panel-body">

      <p>Search for "Aware Client" in the App store and install this app.  Scan
      this QR code:</p>

      <img src="{% url 'aware-register-qr' public_id=ios.public_id %}" style="width: 10em;">

      <p>Manual config URL: {{ ios.get_class.qrcode_url }}</p>
    </div>
  </div>
</div>


</div>
</div>

{% endif %}
"""
    def exists(self):
        return True
    def render(self):
        android = models.Device.objects.filter(user=self.user,
                                               type=AwareDevice.pyclass_name(),
                                               label__slug='primary').get()

        ios = models.Device.objects.filter(user=self.user,
                                           type=AwareDeviceValidCert.pyclass_name(),
                                           label__slug='primary').get()

        template = self.template

        template = engine.from_string(template)
        context = { }
        context.update(self.__dict__)
        context.update(locals())
        context['android'] = android
        context['ios'] = ios
        text = template.render(context=locals(), request=self.request)
        return text

actions = [LinkFacebook,
           LinkTwitter,
           LinkInstagram,
           LinkAware,
       ]


@login_required
def main(request):
    context = c = { }
    from django.shortcuts import render

    actions_ = c['actions'] = [A(request) for A in actions]
    c['a2'] = actions

    c['is_in_oxford_study'] = models.GroupSubject.objects.filter(user=request.user,
                                                group__slug__startswith='oxford2016').exists()

    return TemplateResponse(request, 'oxford2016/main.html', context)


import kdata.converter
from kdata.group import BaseGroup, _GroupConverter
class Oxford2016(BaseGroup):
    converters = [
        kdata.converter.PRTimestamps,
        kdata.converter.PRRecentDataCounts,
        kdata.converter.AwarePacketTimeRange,
        kdata.converter.AwareRecentDataCounts,
        kdata.converter.AwareTimestamps,
        ]

    def setup_user(self, user):
        super(Oxford2016, self).setup_user(user)
        import json
        if self.dbrow.pyclass_data:
          data = json.loads(self.dbrow.pyclass_data)
          if 'create_devices' in data:

            devs = [
                dict(cls=kdata.aware.AwareDevice, name="Phone"),
                dict(cls=kdata.aware.AwareDeviceValidCert, name="Phone"),
                dict(cls=Facebook, name="Facebook"),
                dict(cls=Twitter, name="Twitter"),
                dict(cls=Instagram, name="Instagram"),
                ]

            kdata.group.ensure_user_has_devices(user=user, devs=devs, group=self)
