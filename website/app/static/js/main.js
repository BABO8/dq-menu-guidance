/**
 * DQ Menu Guidance - Main Interactive Scripts (2026 Production Edition)
 * Lightweight, accessible, no third-party framework dependencies.
 */

document.addEventListener('DOMContentLoaded', () => {
  initMobileNav();
  initLiveSearch();
  initTableSortingAndFilter();
  initDietaryAndTableFilters();
  initPriceTaxCalculator();
  initTableOfContents();
  initFaqAccordions();
  initKeyboardShortcuts();
});

// 1. Mobile Navigation
function initMobileNav() {
  const toggleBtn = document.querySelector('.mobile-toggle');
  const mobileNav = document.querySelector('.mobile-nav');
  if (!toggleBtn || !mobileNav) return;

  toggleBtn.addEventListener('click', () => {
    const isExpanded = toggleBtn.getAttribute('aria-expanded') === 'true';
    toggleBtn.setAttribute('aria-expanded', !isExpanded);
    mobileNav.classList.toggle('open');
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && mobileNav.classList.contains('open')) {
      mobileNav.classList.remove('open');
      toggleBtn.setAttribute('aria-expanded', 'false');
      toggleBtn.focus();
    }
  });
}

// 2. Live Search Autocomplete & Quick Lookup
function initLiveSearch() {
  const searchInput = document.querySelector('.search-input');
  const dropdown = document.querySelector('.search-dropdown');
  if (!searchInput || !dropdown) return;

  let debounceTimer = null;

  searchInput.addEventListener('input', (e) => {
    const val = e.target.value.trim();
    clearTimeout(debounceTimer);

    if (val.length < 2) {
      dropdown.classList.remove('active');
      dropdown.innerHTML = '';
      return;
    }

    debounceTimer = setTimeout(() => {
      fetch(`/api/search/suggestions?q=${encodeURIComponent(val)}`)
        .then(res => res.json())
        .then(data => {
          if (!data || data.length === 0) {
            dropdown.innerHTML = `
              <div style="padding: 14px 16px; color: var(--text-muted); font-size: 0.9rem;">
                No instant match for "<strong>${escapeHtml(val)}</strong>". Press enter to perform full site search.
              </div>
            `;
            dropdown.classList.add('active');
            return;
          }

          let html = '';
          data.forEach(item => {
            html += `
              <a href="${item.url}" class="search-item">
                <span style="font-weight: 500;">${escapeHtml(item.title)}</span>
                <span class="search-item-cat">${escapeHtml(item.category)}</span>
              </a>
            `;
          });
          html += `
            <a href="/search?q=${encodeURIComponent(val)}" class="search-item" style="background: var(--bg-subtle); font-weight: 600; color: var(--color-brand);">
              <span>View all results for "${escapeHtml(val)}" &rarr;</span>
            </a>
          `;
          dropdown.innerHTML = html;
          dropdown.classList.add('active');
        })
        .catch(() => {
          dropdown.classList.remove('active');
        });
    }, 200);
  });

  // Close dropdown on outside click
  document.addEventListener('click', (e) => {
    if (!searchInput.contains(e.target) && !dropdown.contains(e.target)) {
      dropdown.classList.remove('active');
    }
  });

  // Handle ESC in search input
  searchInput.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      dropdown.classList.remove('active');
    }
  });
}

// 3. Client-side Table Filter & Sort
function initTableSortingAndFilter() {
  const targetTables = document.querySelectorAll('.table-interactive');
  if (!targetTables || targetTables.length === 0) return;

  targetTables.forEach(targetTable => {
    // Column header sorting
    const headers = targetTable.querySelectorAll('th[data-sortable="true"]');
    headers.forEach((header, colIndex) => {
      header.style.cursor = 'pointer';
      header.title = 'Click to sort column';
      header.addEventListener('click', () => {
        const isAsc = header.classList.contains('sort-asc');
        headers.forEach(h => h.classList.remove('sort-asc', 'sort-desc'));
        
        const tbody = targetTable.querySelector('tbody');
        if (!tbody) return;
        const rows = Array.from(tbody.querySelectorAll('tr'));
        
        rows.sort((a, b) => {
          const cellA = a.children[colIndex] ? a.children[colIndex].textContent.trim() : '';
          const cellB = b.children[colIndex] ? b.children[colIndex].textContent.trim() : '';
          
          const numA = parseFloat(cellA.replace(/[^0-9.]/g, ''));
          const numB = parseFloat(cellB.replace(/[^0-9.]/g, ''));
          
          if (!isNaN(numA) && !isNaN(numB)) {
            return isAsc ? numB - numA : numA - numB;
          }
          return isAsc ? cellB.localeCompare(cellA) : cellA.localeCompare(cellB);
        });

        header.classList.add(isAsc ? 'sort-desc' : 'sort-asc');
        rows.forEach(r => tbody.appendChild(r));
      });
    });
  });
}

// 4. Dietary & Table Multi-Filter (Nutrition and Allergen Pages)
function initDietaryAndTableFilters() {
  const filterInput = document.getElementById('tableFilterInput');
  const filterPillBtns = document.querySelectorAll('.filter-pill-btn');
  const targetTables = document.querySelectorAll('#nutritionTable, #allergenTable, .table-interactive');
  if (!targetTables || targetTables.length === 0) return;

  let activeFilter = 'all';

  function applyFilters() {
    const query = filterInput ? filterInput.value.toLowerCase().trim() : '';

    targetTables.forEach(table => {
      const rows = table.querySelectorAll('tbody tr');
      rows.forEach(row => {
        let matchesQuery = true;
        let matchesPill = true;

        // 1. Text Search Filter
        if (query) {
          const text = row.textContent.toLowerCase();
          matchesQuery = text.includes(query);
        }

        // 2. Pill Filter
        if (activeFilter !== 'all') {
          const category = row.getAttribute('data-category') || '';
          const allergens = (row.getAttribute('data-allergens') || '').toLowerCase();
          const miniCal = parseInt(row.getAttribute('data-mini-cal') || '9999', 10);
          const smallCal = parseInt(row.getAttribute('data-small-cal') || '9999', 10);
          const isGf = row.getAttribute('data-is-gf') === 'true';
          const isDf = row.getAttribute('data-is-df') === 'true';

          switch (activeFilter) {
            case 'under-500':
              matchesPill = miniCal <= 500;
              break;
            case 'under-700':
              matchesPill = smallCal <= 700;
              break;
            case 'nut-free':
              matchesPill = !allergens.includes('peanuts') && !allergens.includes('treenuts');
              break;
            case 'fruit-light':
              matchesPill = category === 'fruit' || row.textContent.toLowerCase().includes('fruit') || row.textContent.toLowerCase().includes('strawberry') || row.textContent.toLowerCase().includes('apple');
              break;
            case 'seasonal':
              matchesPill = category === 'seasonal' || row.textContent.toLowerCase().includes('2026') || row.textContent.toLowerCase().includes('fall') || row.textContent.toLowerCase().includes('holiday');
              break;
            case 'gluten-free':
              matchesPill = isGf || row.textContent.toLowerCase().includes('gluten-free') || row.textContent.toLowerCase().includes('certified gf');
              break;
            case 'dairy-free':
              matchesPill = isDf || row.textContent.toLowerCase().includes('dairy-free') || row.textContent.toLowerCase().includes('vegan');
              break;
            case 'treats':
              matchesPill = category === 'treats' || row.textContent.toLowerCase().includes('blizzard') || row.textContent.toLowerCase().includes('dilly') || row.textContent.toLowerCase().includes('cone');
              break;
            case 'hot-food':
              matchesPill = category === 'hot-food' || row.textContent.toLowerCase().includes('burger') || row.textContent.toLowerCase().includes('chicken') || row.textContent.toLowerCase().includes('fries') || row.textContent.toLowerCase().includes('rings');
              break;
            default:
              matchesPill = true;
          }
        }

        row.style.display = (matchesQuery && matchesPill) ? '' : 'none';
      });
    });
  }

  if (filterInput) {
    filterInput.addEventListener('input', applyFilters);
  }

  filterPillBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      filterPillBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      activeFilter = btn.getAttribute('data-filter') || 'all';
      applyFilters();
    });
  });
}

// 5. U.S. State Price & Sales Tax Estimator Calculator
function initPriceTaxCalculator() {
  const calcWidgets = document.querySelectorAll('.calculator-widget');
  if (!calcWidgets || calcWidgets.length === 0) return;

  const itemsCatalog = {
    'mini-blizzard': { name: 'Mini Blizzard® (6 oz)', basePrice: 4.69, cal: '350 - 450 kcal' },
    'small-blizzard': { name: 'Small Blizzard® (12 oz)', basePrice: 5.59, cal: '560 - 740 kcal' },
    'medium-blizzard': { name: 'Medium Blizzard® (16 oz)', basePrice: 6.29, cal: '760 - 1,030 kcal' },
    'large-blizzard': { name: 'Large Blizzard® (21 oz)', basePrice: 7.19, cal: '980 - 1,390 kcal' },
    'stackburger-combo': { name: 'Bacon Two Cheese 1/3 lb Stackburger Combo', basePrice: 9.99, cal: '1,180 kcal' },
    'flamethrower-combo': { name: 'FlameThrower® 1/3 lb Stackburger Combo', basePrice: 10.19, cal: '1,220 kcal' },
    'chicken-basket-4pc': { name: '4-Pc Crispy Chicken Strip Basket', basePrice: 9.99, cal: '1,030 kcal' },
    'chicken-basket-6pc': { name: '6-Pc Crispy Chicken Strip Basket', basePrice: 13.49, cal: '1,380 kcal' },
    'meal-deal-7': { name: '$7 Meal Deal (Cheeseburger or 3pc Strips)', basePrice: 7.00, cal: '960 - 1,050 kcal' },
    'round-cake-8': { name: '8" Round Ice Cream Cake (Serves 8-10)', basePrice: 31.99, cal: '4,100 kcal' },
    'sheet-cake-11x14': { name: '11" x 14" Sheet Cake (Serves 20-24)', basePrice: 43.99, cal: '9,600 kcal' }
  };

  const regionTiers = {
    'avg': { name: 'Average U.S. Baseline (FL, GA, NC, AZ, PA, MI)', multiplier: 1.00, taxRate: 0.0700, tag: 'Standard Franchise Tier' },
    'low': { name: 'Low-Cost U.S. Tier (TX, OH, IN, OK, MO, TN)', multiplier: 0.93, taxRate: 0.0625, tag: '-7% Menu Discount Tier' },
    'high': { name: 'High-Cost U.S. Tier (CA, NY, WA, MA, NJ, HI)', multiplier: 1.12, taxRate: 0.0888, tag: '+12% Metro Overhead Tier' }
  };

  calcWidgets.forEach(widget => {
    const itemSelect = widget.querySelector('.calc-item-select');
    const regionSelect = widget.querySelector('.calc-region-select');
    const qtyInput = widget.querySelector('.calc-qty-input') || { value: 1 };
    
    // Output fields
    const basePriceEl = widget.querySelector('.calc-base-price');
    const adjPriceEl = widget.querySelector('.calc-adj-price');
    const taxEl = widget.querySelector('.calc-tax');
    const totalEl = widget.querySelector('.calc-total');
    const calEl = widget.querySelector('.calc-calories');
    const noteEl = widget.querySelector('.calc-note');

    if (!itemSelect || !regionSelect) return;

    function recalculate() {
      const itemKey = itemSelect.value;
      const regionKey = regionSelect.value;
      const qty = Math.max(1, parseInt(qtyInput.value || '1', 10));

      const item = itemsCatalog[itemKey] || itemsCatalog['small-blizzard'];
      const tier = regionTiers[regionKey] || regionTiers['avg'];

      const adjUnitPrice = Math.round(item.basePrice * tier.multiplier * 100) / 100;
      const subtotal = adjUnitPrice * qty;
      const estimatedTax = Math.round(subtotal * tier.taxRate * 100) / 100;
      const finalTotal = subtotal + estimatedTax;

      if (basePriceEl) basePriceEl.textContent = `$${(item.basePrice * qty).toFixed(2)}`;
      if (adjPriceEl) adjPriceEl.textContent = `$${subtotal.toFixed(2)}`;
      if (taxEl) taxEl.textContent = `$${estimatedTax.toFixed(2)} (${(tier.taxRate * 100).toFixed(2)}%)`;
      if (totalEl) totalEl.textContent = `$${finalTotal.toFixed(2)}`;
      if (calEl) calEl.textContent = item.cal;
      if (noteEl) {
        noteEl.innerHTML = `<strong>${tier.tag}:</strong> Estimated state sales tax calculated at ${(tier.taxRate * 100).toFixed(2)}%. Independent franchisees set final store prices.`;
      }
    }

    itemSelect.addEventListener('change', recalculate);
    regionSelect.addEventListener('change', recalculate);
    if (qtyInput.addEventListener) {
      qtyInput.addEventListener('input', recalculate);
    }

    recalculate();
  });
}

// 6. Dynamic Table of Contents for Editorial Articles
function initTableOfContents() {
  const prose = document.querySelector('.editorial-prose');
  const tocContainer = document.getElementById('tocContainer');
  const tocList = document.getElementById('tocList');
  if (!prose || !tocContainer || !tocList) return;

  const headings = prose.querySelectorAll('h2');
  if (headings.length < 2) return;

  tocList.innerHTML = '';
  headings.forEach((h2, idx) => {
    if (!h2.id) {
      const slug = h2.textContent
        .toLowerCase()
        .replace(/[^a-z0-9]+/g, '-')
        .replace(/(^-|-$)/g, '');
      h2.id = slug || `heading-${idx + 1}`;
    }

    const li = document.createElement('li');
    const a = document.createElement('a');
    a.href = `#${h2.id}`;
    a.textContent = h2.textContent;
    a.style.color = 'var(--text-secondary)';
    a.style.textDecoration = 'none';
    a.addEventListener('mouseenter', () => a.style.color = 'var(--color-brand)');
    a.addEventListener('mouseleave', () => a.style.color = 'var(--text-secondary)');
    li.appendChild(a);
    tocList.appendChild(li);
  });

  tocContainer.style.display = 'block';
}

// 7. FAQ Accordion Handling
function initFaqAccordions() {
  const faqHeaders = document.querySelectorAll('.faq-toggle');
  faqHeaders.forEach(toggle => {
    toggle.addEventListener('click', () => {
      const content = toggle.nextElementSibling;
      const isOpen = toggle.getAttribute('aria-expanded') === 'true';
      toggle.setAttribute('aria-expanded', !isOpen);
      content.style.display = isOpen ? 'none' : 'block';
      const icon = toggle.querySelector('span:last-child');
      if (icon) {
        icon.innerHTML = isOpen ? '&plus;' : '&minus;';
      }
    });
  });
}

// 8. Global Keyboard Shortcuts
function initKeyboardShortcuts() {
  document.addEventListener('keydown', (e) => {
    if (e.key === '/' && document.activeElement.tagName !== 'INPUT' && document.activeElement.tagName !== 'TEXTAREA') {
      const mainSearch = document.querySelector('.search-input');
      if (mainSearch) {
        e.preventDefault();
        mainSearch.focus();
      }
    }
  });
}

function escapeHtml(str) {
  return str.replace(/[&<>'"]/g, 
    tag => ({
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      "'": '&#39;',
      '"': '&quot;'
    }[tag] || tag)
  );
}
