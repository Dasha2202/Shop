from django.shortcuts import render
from .models import OrderItem
from .forms import OrderCreateForm
from cart.cart import Cart
from .tasks import OrderCreated
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import render_to_string
#import weasyprint
from django.shortcuts import render, get_object_or_404
from .models import OrderItem, Order
from django.contrib.admin.views.decorators import staff_member_required
#from cffi import cairocffi
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse



@staff_member_required
def AdminOrderPDF(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    html = render_to_string('orders/order/pdf.html', {'order': order})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename=order_{}.pdf'.format(order.id)
    weasyprint.HTML(string=html).write_pdf(response,
               stylesheets=[weasyprint.CSS(settings.STATIC_ROOT + 'css/bootstrap.min.css')])
    return response

@staff_member_required
def AdminOrderDetail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'admin/orders/order/detail.html', {'order': order})

def OrderCreate(request):
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            cart.clear()
            # Асинхронная отправка сообщения
            OrderCreated.delay(order.id)
            request.session['order_id'] = order.id
            return redirect(reverse('payment:process'))

