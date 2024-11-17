from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Offer, OfferProduct, Product, CustomUser
from .forms import OfferForm, OfferProductForm, ProductForm
from django.http import JsonResponse
from django.utils import timezone
import logging
from django.http import HttpResponseBadRequest
from django.db.models import Q


logger = logging.getLogger(__name__)

@login_required
def home_view(request):
    user = request.user
    full_name = user.get_full_name()
    return render(request, "offers/home.html", {"full_name": full_name})


@login_required
def create_offer(request, offer=None):
    if request.method == "POST":
        offer_form = OfferForm(request.POST)
        print(offer_form)
        if offer_form.is_valid():
            print('Form is valid')
            print(offer_form.cleaned_data)
            offer = offer_form.save(commit=False)
            try:
                offer.executor = request.user.customuser
            except CustomUser.DoesNotExist:
                return render(
                    request,
                    "offers/create_offer.html",
                    {"error": "User has no customuser"},
                )

            offer.number = f"COM-{Offer.objects.count() + 1}"
            offer.date = timezone.now().strftime("%d.%m.%y")
            offer.save()

            for key in request.POST:
                if key.startswith("product-"):
                    product_form = OfferProductForm(request.POST, prefix=key)
                    if product_form.is_valid():
                        offer_product = product_form.save(commit=False)
                        offer_product.offer = offer
                        offer_product.save()

            return redirect("offer_detail", offer_id=offer.id)
    else:
        offer_form = OfferForm()
        next_offer_number = f"COM-{Offer.objects.count() + 1}"
        current_date = timezone.now().strftime("%d.%m.%y")

    offer_products = []
    if request.method == "POST":
        for key in request.POST:
            if key.startswith("product-"):
                product_form = OfferProductForm(request.POST, prefix=key)
                if product_form.is_valid():
                    offer_product = product_form.save(commit=False)
                    offer_product.offer = offer
                    offer_product.save()
                    offer_products.append(offer_product)
    else:
        for i in range(1):
            offer_products.append(OfferProductForm(prefix=f"product-{i}"))

    products = Product.objects.all()
    context = {
        "offer_form": offer_form,
        "offer_products": offer_products,
        "products": products,
        "next_offer_number": next_offer_number,
        "current_date": current_date,
    }
    return render(request, "offers/create_offer.html", context)


@login_required
def offer_detail(request, offer_id):
    offer = get_object_or_404(Offer, id=offer_id)
    offer_products = OfferProduct.objects.filter(offer=offer)
    form = OfferForm(instance=offer)
    context = {
        'offer': offer,
        'offer_products': offer_products,
        'form': form,
    }
    return render(request, 'offers/offer_detail.html', context)


@login_required
def offer_list(request):
    if request.method == 'POST':
        logger.debug("Received POST request with data: %s", request.POST)

        unique_number = f"COM-{Offer.objects.count() + 1}"
        customer = request.POST.get('customer')
        logger.debug("Customer value: %s", customer)

        if not customer:
            logger.error("Customer field is missing or empty")
            return HttpResponseBadRequest("Customer field is required")

        new_offer = Offer(
            number=unique_number,
            date=timezone.now().strftime("%d.%m.%Y"),
            executor=request.user,
            customer=customer,
            description=request.POST.get('remarks'),
            delivery=request.POST.get('delivery'),
            remarks=request.POST.get('payment_terms')
        )
        new_offer.save()

        total_price = 0
        for key in request.POST:
            if key.startswith("product-"):
                product_id = request.POST.get(f"{key}-product")
                logger.debug(f"Processing product with id: {product_id}")
                if product_id:
                    try:
                        product = Product.objects.get(id=product_id)
                        quantity = request.POST.get(f"{key}-quantity")
                        price = product.price
                        total_price += float(price) * int(quantity)
                        OfferProduct.objects.create(
                            offer=new_offer,
                            product=product,
                            quantity=quantity,
                            price=price
                        )
                    except Product.DoesNotExist:
                        logger.error(f"Product with id {product_id} does not exist")
                        return HttpResponseBadRequest(f"Product with id {product_id} does not exist")

        new_offer.total_price = total_price
        new_offer.save()

        return redirect('offer_list')

    search_query = request.GET.get('search')
    offers = Offer.objects.all().order_by('-date')

    if search_query:
        offers = offers.filter(
            Q(number__icontains=search_query) |
            Q(date__icontains=search_query) |
            Q(executor__first_name__icontains=search_query)
        )

    next_offer_number = f"COM-{Offer.objects.count() + 1}"
    context = {
        "offers": offers,
        "next_offer_number": next_offer_number,
    }
    return render(request, "offers/offer_list.html", context)


@login_required
def create_product(request):
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("product_list")
    else:
        form = ProductForm()
    return render(request, "offers/create_product.html", {"form": form})


@login_required
def product_list(request):
    search_query = request.GET.get('search')
    products = Product.objects.all()

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(tags__icontains=search_query) |
            Q(article__icontains=search_query)
        )

    context = {
        "products": products,
    }
    return render(request, "offers/product_list.html", context)


@login_required
def edit_offer(request, offer_id):
    offer = Offer.objects.get(id=offer_id)
    if request.method == "POST":
        form = OfferForm(request.POST, instance=offer)
        if form.is_valid():
            form.save()
            return redirect("offer_detail", offer_id=offer.id)
    else:
        form = OfferForm(instance=offer)
    return render(request, "offers/edit_offer.html", {"form": form})


@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect("product_list")
    else:
        form = ProductForm(instance=product)
    return render(request, "offers/edit_product.html", {"form": form})


def get_product_details(request, product_id):
    product = Product.objects.get(id=product_id)
    data = {"name": product.name, "price": float(product.price)}
    return JsonResponse(data)