from app.models import AssetTransfer, TransferType, General_Ledger


def on_repairs(request):
    type = TransferType.objects.get(name="External")
    on_repairs = AssetTransfer.objects.filter(is_approved=True, type=type,
                                              returned=False)
    return {
        'on_repairs': on_repairs
    }


def gls(request):
    gls = General_Ledger.objects.all()

    return {
        'gls': gls
    }


def greetings(request):
    import app
    return {
        'greetings': app.utilities.greetings()
    }
