from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from app.models import Asset, Application, Configuration
from app.tools import get_asset_or_404
from app.utilities import greetings
from bancapis.abc.apis import send_email


@login_required(login_url='abcassetsmanager:login')
def workstation_deployment(request, asset_id):
    template = 'app/workstation_deployment.html'

    if request.method == 'POST':
        ad_name = request.POST.get('ad_name')
        apps = request.POST.getlist('apps[]')
        rmv = request.POST.getlist('rmv[]')
        print(apps)
        try:
            asset = get_asset_or_404(asset_id)
            print(asset)
            asset.active_directory_id = ad_name
            asset.save()

            for app in apps:
                install_this = Application.objects.get(name=app)
                asset.installed_applications.add(install_this)
            asset.save()
            Configuration.objects.create(asset=asset, configured_by=request.user).save()
        except Application.DoesNotExist:
            print("Application not found")

        except Asset.DoesNotExist:
            print("Asset not found")

        except BaseException as e:
            print(e)

        finally:
            asset.save()
            print(asset.active_directory_id)

    context = {
        'greetings': greetings,
        'applications': Application.objects.all(),
        'asset': get_asset_or_404(asset_id)
    }
    return render(request, template, context)
