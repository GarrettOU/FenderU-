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

  function shipping(){
    var v = function(id){ return typeof coVal === 'function' ? coVal(id) : ''; };
    return {
      qty: window.qty,
      first: v('coFirst'), last: v('coLast'), email: v('coEmail'), phone: v('coPhone'),
      addr1: v('coAddr1'), addr2: v('coAddr2'), city: v('coCity'), state: v('coState'), zip: v('coZip')
    };
  }
  function postJson(url, body){
    return fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })
      .then(function(r){ return r.json().then(function(j){ if (!r.ok) throw new Error(j.error || r.status); return j; }); });
  }
  function track(){
    if (typeof fuTrack === 'function' && typeof orderTotal === 'function') fuTrack('AddPaymentInfo', { value: orderTotal(window.qty), currency: 'USD' });
  }

  /* Card payments through Stripe, when the Worker has a Stripe key.
     Any failure falls back to the page's PayPal card checkout. */
  function cardViaStripe(){
    var btn = document.getElementById('placeOrderBtn');
    var label = btn ? btn.innerHTML : '';
    if (btn) { btn.disabled = true; btn.textContent = 'Opening secure checkout\u2026'; }
    postJson('/api/checkout', shipping())
      .then(function(j){ if (!j.url) throw new Error('no url'); track(); window.location.href = j.url; })
      .catch(function(){
        if (btn) { btn.disabled = false; btn.innerHTML = label; }
        if (typeof checkoutPayPal === 'function') checkoutPayPal();
      });
  }

  /* One payment section, one Place Order button. The buyer picks how to pay
     above the button (credit card preselected, as most US buyers use it) and
     the button's label says where it goes next. */
  var method = 'card', venmoReady = false;
  var NOTES = {
    card: window.FU_CARD_CHECKOUT
      ? 'Secure checkout by Stripe. We never see or store your card number.'
      : 'Your card is processed on PayPal\u2019s secure page. No PayPal account needed. We never see or store your card number.',
    paypal: 'You\u2019ll finish paying on PayPal\u2019s secure page.',
    venmo: 'Approve the payment in your Venmo app.'
  };

  function option(value, name, sub){
    var l = document.createElement('label');
    l.className = 'pm-opt' + (value === method ? ' selected' : '');
    l.innerHTML = '<input type="radio" name="fuPay" value="' + value + '"' + (value === method ? ' checked' : '') + '>' +
      '<span class="pm-main"><span class="pm-name">' + name + '</span><span class="pm-sub">' + sub + '</span></span>';
    l.querySelector('input').addEventListener('change', function(){ choose(value); });
    return l;
  }

  function choose(m){
    method = m;
    all('#fuPayList .pm-opt').forEach(function(l){
      var on = l.querySelector('input').value === m;
      l.classList.toggle('selected', on);
      l.querySelector('input').checked = on;
    });
    var btn = document.getElementById('placeOrderBtn');
    var venmo = document.getElementById('fuVenmoBtn');
    if (btn) {
      var total = document.getElementById('placeTotal');
      var t = total ? total.textContent : '';
      var lead = m === 'paypal' ? 'Continue to PayPal' : 'Continue to Payment';
      btn.innerHTML = lead + ' \u2014 <span id="placeTotal">' + t + '</span>';
      btn.style.display = m === 'venmo' ? 'none' : '';
    }
    if (venmo) venmo.style.display = m === 'venmo' ? '' : 'none';
    var note = document.querySelector('#coStep3 .co-secure');
    if (note) note.textContent = '\ud83d\udd12 ' + NOTES[m];
  }

  function buildPayment(){
    var step = document.getElementById('coStep3');
    var old = step && step.querySelector('.pay-accepted');
    if (!old || document.getElementById('fuPayList')) return;
    var list = document.createElement('div');
    list.className = 'pm-list';
    list.id = 'fuPayList';
    list.setAttribute('role', 'radiogroup');
    list.appendChild(option('card', 'Credit or debit card', window.FU_CARD_CHECKOUT
      ? 'Visa, Mastercard, Amex, Discover, Apple Pay, Google Pay'
      : 'Visa, Mastercard, Amex, Discover'));
    list.appendChild(option('paypal', 'PayPal', 'Pay with your PayPal account'));
    old.parentNode.replaceChild(list, old);
    choose('card');
    if (window.FU_PAYPAL_CLIENT_ID) loadVenmo(list);
  }

  /* Venmo goes through PayPal's own Venmo button, which only PayPal can draw.
     It takes the Place Order button's spot when Venmo is chosen, so there is
     still one button. The option only appears when PayPal says this buyer can
     use Venmo. */
  function loadVenmo(list){
    var s = document.createElement('script');
    s.src = 'https://www.paypal.com/sdk/js?client-id=' + encodeURIComponent(window.FU_PAYPAL_CLIENT_ID) +
      '&components=buttons&enable-funding=venmo&currency=USD&intent=capture';
    s.onload = function(){
      if (!window.paypal || !paypal.Buttons) return;
      var orderId = null;
      var button = paypal.Buttons({
        fundingSource: paypal.FUNDING.VENMO,
        style: { height: 48, shape: 'rect' },
        onClick: function(data, actions){
          if (typeof validateCheckout === 'function' && !validateCheckout()) { if (typeof goStep === 'function') goStep(2); return actions.reject(); }
          track();
          return actions.resolve();
        },
        createOrder: function(){
          var b = shipping(); b.method = 'venmo';
          return postJson('/api/paypal/order', b).then(function(j){ orderId = j.id; return j.id; });
        },
        onApprove: function(data){
          return postJson('/api/paypal/capture', { id: data.orderID || orderId }).then(function(){
            window.location.href = window.location.pathname + '?thanks=1&q=' + (window.qty || 1);
          });
        },
        onError: function(){
          var note = document.querySelector('#coStep3 .co-secure');
          if (note) note.textContent = 'Venmo didn\u2019t go through. Nothing was charged. Please try again or choose another way to pay.';
        }
      });
      if (!button.isEligible()) return;
      var slot = document.createElement('div');
      slot.id = 'fuVenmoBtn';
      slot.style.cssText = 'flex:1;display:none';
      var btn = document.getElementById('placeOrderBtn');
      if (!btn) return;
      btn.parentNode.insertBefore(slot, btn.nextSibling);
      button.render(slot).then(function(){
        venmoReady = true;
        list.appendChild(option('venmo', 'Venmo', 'Pay with the Venmo app'));
      });
    };
    document.head.appendChild(s);
  }

  function setupPayment(){
    if (typeof window.placeOrder !== 'function') return;
    window.placeOrder = function(){
      if (typeof validateCheckout === 'function' && !validateCheckout()) { if (typeof goStep === 'function') goStep(2); return; }
      if (method === 'card' && window.FU_CARD_CHECKOUT) return cardViaStripe();
      if (typeof checkoutPayPal === 'function') return checkoutPayPal();
    };
    window.setPayMethod = function(m){ if (m === 'card' || m === 'paypal' || (m === 'venmo' && venmoReady)) choose(m); };
    buildPayment();
    /* The page's own total updater rewrites #placeTotal; keep the label. */
    if (typeof window.updateTotals === 'function') {
      var orig = window.updateTotals;
      window.updateTotals = function(){ var r = orig.apply(this, arguments); if (document.getElementById('fuPayList')) choose(method); return r; };
    }
  }

  function start(){ wire(); setupPayment(); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start);
  else start();
})();
