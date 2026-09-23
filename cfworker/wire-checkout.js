/* Reconnects fenderu.com's buttons to the checkout code already on the page.
   The deployed index.html lost its onclick/onchange attributes, so every
   button did nothing. This binds the same calls those attributes made.
   Elements that still carry their own handler are left alone. */
(function(){
  if (window.__fuWired) return;
  window.__fuWired = true;

  function on(el, ev, fn){
    if (!el || el.hasAttribute('on' + ev)) return;
    el.addEventListener(ev, fn);
  }
  function all(sel){ return Array.prototype.slice.call(document.querySelectorAll(sel)); }
  function call(name){
    var args = Array.prototype.slice.call(arguments, 1);
    return function(){ if (typeof window[name] === 'function') window[name].apply(null, args); };
  }

  function wire(){
    on(document.getElementById('cartBtn'), 'click', call('openCart'));
    all('.sb-btn, .btn-primary, .buy-btn, .big-cta-btn').forEach(function(b){ on(b, 'click', call('addToCart')); });

    var wrap = document.getElementById('modalWrap');
    on(wrap, 'click', function(e){ if (typeof handleModalBg === 'function') handleModalBg(e); });
    all('#modalWrap .modal-close').forEach(function(b){ on(b, 'click', call('closeModal')); });

    on(document.querySelector('[aria-label="Decrease quantity"]'), 'click', call('changeQty', -1));
    on(document.querySelector('[aria-label="Increase quantity"]'), 'click', call('changeQty', 1));
    all('.cart-remove').forEach(function(b){ on(b, 'click', call('removeFromCart')); });

    var step1 = document.getElementById('coStep1');
    if (step1) {
      var filled = document.getElementById('cartFilled'), empty = document.getElementById('cartEmpty');
      if (filled) all('#cartFilled .co-next').forEach(function(b){ on(b, 'click', call('goStep', 2)); });
      if (empty) all('#cartEmpty .co-next').forEach(function(b){ on(b, 'click', call('addToCart')); });
      all('#coStep1 .co-keep').forEach(function(b){ on(b, 'click', call('closeModal')); });
    }
    all('#coStep2 .co-back').forEach(function(b){ on(b, 'click', call('goStep', 1)); });
    all('#coStep2 .co-next').forEach(function(b){ on(b, 'click', call('goStep', 3)); });
    all('#coStep3 .co-back').forEach(function(b){ on(b, 'click', call('goStep', 2)); });
    on(document.getElementById('placeOrderBtn'), 'click', call('placeOrder'));

    all('input[name="carrier"]').forEach(function(r){
      on(r, 'change', function(){ if (typeof setCarrier === 'function') setCarrier(r.value); });
    });
    all('input[name="paymethod"]').forEach(function(r){
      on(r, 'change', function(){ if (typeof setPayMethod === 'function') setPayMethod(r.value); });
    });

    all('.faq-q').forEach(function(q){
      on(q, 'click', function(){ if (typeof toggleFaq === 'function') toggleFaq(q); });
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', wire);
  else wire();
})();
