// Cart Data
let cart = [];

// DOM Elements
const cartPopup = document.getElementById('cart-popup');
const cartItemsList = document.getElementById('cart-items');
const cartTotal = document.getElementById('cart-total');
const cartCount = document.getElementById('cart-count');
const searchInput = document.getElementById('search-input');
const categoryFilter = document.getElementById('category-filter');

// Add to Cart Function
function addToCart(name, price) {
    const existing = cart.find(item => item.name === name);
    if (existing) {
        existing.quantity += 1;
    } else {
        cart.push({ name, price, quantity: 1 });
    }
    updateCartUI();
    alert(`${name} added to cart!`);
}

// Update Cart Display
function updateCartUI() {
    cartItemsList.innerHTML = '';
    let total = 0;
    cart.forEach((item, index) => {
        total += item.price * item.quantity;
        const li = document.createElement('li');
        li.innerHTML = `
            <span>${item.name} (₹${item.price}) x ${item.quantity}</span>
            <div>
              <button class="qty-btn" onclick="changeQty(${index}, -1)">-</button>
              <button class="qty-btn" onclick="changeQty(${index}, 1)">+</button>
              <button class="remove-btn" onclick="removeItem(${index})">Remove</button>
            </div>
        `;
        cartItemsList.appendChild(li);
    });
    cartTotal.textContent = total;
    cartCount.textContent = cart.reduce((acc, item) => acc + item.quantity, 0);
}

// Change Quantity
function changeQty(index, delta) {
    cart[index].quantity += delta;
    if (cart[index].quantity <= 0) {
        cart.splice(index, 1);
    }
    updateCartUI();
}

// Remove Item
function removeItem(index) {
    cart.splice(index, 1);
    updateCartUI();
}

// Open Cart
document.getElementById('cart-btn').addEventListener('click', () => {
    cartPopup.style.display = 'block';
});

// Close Cart
function closeCart() {
    cartPopup.style.display = 'none';
}

// Search Functionality
searchInput.addEventListener('input', () => {
    const term = searchInput.value.toLowerCase();
    const products = document.querySelectorAll('.product');
    products.forEach(prod => {
        const name = prod.dataset.name.toLowerCase();
        prod.style.display = name.includes(term) ? 'block' : 'none';
    });
});

// Category Filter
categoryFilter.addEventListener('change', () => {
    const cat = categoryFilter.value;
    const products = document.querySelectorAll('.product');
    products.forEach(prod => {
        const prodCat = prod.dataset.category;
        prod.style.display = (cat === 'all' || prodCat === cat) ? 'block' : 'none';
    });
});

// Back to Top Button
const backBtn = document.getElementById("backTopBtn");
window.onscroll = function() { scrollFunction(); };

function scrollFunction() {
    if (document.body.scrollTop > 400 || document.documentElement.scrollTop > 400) {
        backBtn.style.display = "block";
    } else {
        backBtn.style.display = "none";
    }
}

backBtn.addEventListener('click', () => {
    document.body.scrollTop = 0;
    document.documentElement.scrollTop = 0;
});
