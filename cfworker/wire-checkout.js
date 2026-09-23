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

  /* Card payments through Stripe, when the Worker has a Stripe key.
     Any failure falls back to the page's PayPal card checkout. */
  function cardViaStripe(){
    if (typeof validateCheckout === 'function' && !validateCheckout()) { if (typeof goStep === 'function') goStep(2); return; }
    var btn = document.getElementById('placeOrderBtn');
    var label = btn ? btn.innerHTML : '';
    if (btn) { btn.disabled = true; btn.textContent = 'Opening secure checkout\u2026'; }
    var v = function(id){ return typeof coVal === 'function' ? coVal(id) : ''; };
    fetch('/api/checkout', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        qty: window.qty, carrier: window.carrier,
        first: v('coFirst'), last: v('coLast'), email: v('coEmail'), phone: v('coPhone'),
        addr1: v('coAddr1'), addr2: v('coAddr2'), city: v('coCity'), state: v('coState'), zip: v('coZip')
      })
    })
      .then(function(r){ return r.json().then(function(j){ if (!r.ok || !j.url) throw new Error(j.error || r.status); return j; }); })
      .then(function(j){
        if (typeof fuTrack === 'function' && typeof orderTotal === 'function') fuTrack('AddPaymentInfo', { value: orderTotal(window.qty), currency: 'USD' });
        window.location.href = j.url;
      })
      .catch(function(){
        if (btn) { btn.disabled = false; btn.innerHTML = label; }
        if (typeof checkoutPayPal === 'function') checkoutPayPal();
      });
  }

  function setupCard(){
    if (!window.FU_CARD_CHECKOUT || typeof window.placeOrder !== 'function') return;
    var sub = document.querySelector('label[for="pmCard"] .pm-sub');
    if (sub) sub.textContent = 'Processed securely by Stripe.';
    var original = window.placeOrder;
    window.placeOrder = function(){
      if (window.payMethod === 'card') return cardViaStripe();
      return original.apply(this, arguments);
    };
  }

  function start(){ wire(); setupCard(); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start);
  else start();
})();
