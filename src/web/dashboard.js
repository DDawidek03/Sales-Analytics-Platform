document.addEventListener("DOMContentLoaded", function () {
  setupNavigation();
  setupForms();
  setupHelpModal();
  setupFileUploads();
  initAnalytics();
  loadAllFormSelects();
  
  setTimeout(() => {
    const sellersTable = document.getElementById('sellersTable');
    if (sellersTable) {
      loadTableDataToSpecificTable('sellers', 'sellersTable');
    }
  }, 1000);

  console.log("[*] GlobalVista Dashboard initialized");
});

function populateSelectElement(select, data, valueField, textFields, placeholder) {
  if (!select || !data) return;
  
  const firstOption = select.querySelector('option[value=""]');
  select.innerHTML = '';
  
  if (firstOption || placeholder) {
    const opt = document.createElement('option');
    opt.value = '';
    opt.textContent = placeholder;
    select.appendChild(opt);
  }
  
  data.forEach(item => {
    const option = document.createElement('option');
    option.value = item[valueField];
    
    const textParts = textFields.map(field => item[field]).filter(v => v);
    if (textParts.length > 0) {
      option.textContent = `${item[valueField]} - ${textParts.join(' ')}`;
    } else {
      option.textContent = item[valueField];
    }
    
    select.appendChild(option);
  });
}

async function loadAllFormSelects() {
  try {
    console.log('[*] Loading data from API...');
    
    const customers = await fetch('/api/sql/customers').then(r => r.json()).catch(e => { console.error('Error loading customers:', e); return []; });
    await new Promise(resolve => setTimeout(resolve, 100));
    
    const sellers = await fetch('/api/sql/sellers').then(r => r.json()).catch(e => { console.error('Error loading sellers:', e); return []; });
    await new Promise(resolve => setTimeout(resolve, 100));
    
    const products = await fetch('/api/sql/products').then(r => r.json()).catch(e => { console.error('Error loading products:', e); return []; });
    await new Promise(resolve => setTimeout(resolve, 100));
    
    const categories = await fetch('/api/sql/categories').then(r => r.json()).catch(e => { console.error('Error loading categories:', e); return []; });
    await new Promise(resolve => setTimeout(resolve, 100));
    
    const countries = await fetch('/api/sql/countries').then(r => r.json()).catch(e => { console.error('Error loading countries:', e); return []; });
    await new Promise(resolve => setTimeout(resolve, 100));
    
    const regions = await fetch('/api/sql/regions').then(r => r.json()).catch(e => { console.error('Error loading regions:', e); return []; });
    await new Promise(resolve => setTimeout(resolve, 100));
    
    const orders = await fetch('/api/sql/orders').then(r => r.json()).catch(e => { console.error('Error loading orders:', e); return []; });
    
    console.log('[*] Loaded data:', { 
      customers: customers.length, 
      sellers: sellers.length, 
      products: products.length,
      categories: categories.length,
      countries: countries.length,
      regions: regions.length,
      orders: orders.length
    });
    
    document.querySelectorAll('label').forEach(label => {
      const labelText = label.textContent.trim();
      const select = label.nextElementSibling;
      if (!select || select.tagName !== 'SELECT') return;
      
      if (select.closest('#azure-insert-form')) return;
      
      if (labelText.includes('Klient') || labelText.includes('klient')) {
        populateSelectElement(select, customers, 'CustomerID', ['FirstName', 'LastName'], 'Wybierz klienta');
      } else if (labelText.includes('Sprzedawca') || labelText.includes('sprzedawca')) {
        populateSelectElement(select, sellers, 'SellerID', ['FirstName', 'LastName'], 'Wybierz sprzedawcę');
      } else if (labelText.includes('Produkt') || labelText.includes('produkt')) {
        populateSelectElement(select, products, 'ProductID', ['ProductName'], 'Wybierz produkt');
      } else if (labelText.includes('Kategoria') || labelText.includes('kategoria')) {
        populateSelectElement(select, categories, 'CategoryID', ['CategoryName'], 'Wybierz kategorię');
      } else if (labelText.includes('Kraj') || labelText.includes('kraj') || labelText.includes('wysyłki')) {
        populateSelectElement(select, countries, 'CountryID', ['CountryName'], 'Wybierz kraj');
      } else if (labelText.includes('Region') || labelText.includes('region')) {
        populateSelectElement(select, regions, 'RegionID', ['RegionName'], 'Wybierz region');
      } else if (labelText.includes('Zamówienie') || labelText.includes('zamówienie')) {
        populateSelectElement(select, orders, 'OrderID', ['OrderID'], 'Wybierz zamówienie');
      }
    });
    
    console.log('[+] Form selects populated with real data');
  } catch (error) {
    console.error('[!] Error loading form selects:', error);
  }
}

function setupNavigation() {
  const sidebarLinks = document.querySelectorAll(".sidebar-link");
  const dashboardSections = document.querySelectorAll(".dashboard-section");

  window.showSectionFromHash = function () {
    const hash = window.location.hash.substring(1) || "dashboard";
    showSection(hash);
  };

  window.showSection = function (sectionId) {
    dashboardSections.forEach((section) => section.classList.remove("active"));

    
    const targetSection =
      document.getElementById(sectionId) ||
      document.getElementById("dashboard");
    if (targetSection) {
      targetSection.classList.add("active");
      window.location.hash = sectionId;

      sidebarLinks.forEach((link) => {
        const linkSection = link.getAttribute("href").substring(1);
        if (linkSection === sectionId) {
          link.classList.add("active-link", "bg-blue-800", "text-white");
        } else {
          link.classList.remove("active-link", "bg-blue-800", "text-white");
        }
      });
      
      if (sectionId === 'mongo-transactions' && typeof refreshTransactions === 'function') {
        console.log("[*] Auto-loading transactions for mongo-transactions section");
        setTimeout(() => refreshTransactions(), 300);
      }
    }
  };

  sidebarLinks.forEach((link) => {
    link.addEventListener("click", function (e) {
      e.preventDefault();
      const sectionId = this.getAttribute("href").substring(1);
      showSection(sectionId);
    });
  });

  const tableTabs = document.querySelectorAll(".table-tab-btn");
  tableTabs.forEach((tab) => {
    tab.addEventListener("click", function () {
      const tabGroup = this.parentElement;
      const tableId = this.getAttribute("data-table");

      tabGroup
        .querySelectorAll(".table-tab-btn")
        .forEach((t) => t.classList.remove("active"));

      this.classList.add("active");

      
      const formContainer = tabGroup.parentElement;
      formContainer
        .querySelectorAll(".table-form")
        .forEach((form) => form.classList.remove("active"));

      const targetForm = document.getElementById(`${tableId}-form`);
      if (targetForm) targetForm.classList.add("active");
    });
  });

  showSectionFromHash();
}

function setupForms() {
  addFieldNames();

  document.querySelectorAll("form").forEach((form) => {
    form.addEventListener("submit", async function (e) {
      e.preventDefault();

      const formData = collectFormData(form);

      
      const section = form.closest(".dashboard-section");
      if (!section) return;

      const sectionId = section.id;
      let endpoint = getApiEndpoint(sectionId, form);

      if (endpoint) {
        try {
          const submitBtn = form.querySelector(".submit-btn");
          const originalText = submitBtn.innerHTML;
          submitBtn.innerHTML =
            '<i class="fas fa-spinner fa-spin mr-2"></i>Przetwarzanie...';
          submitBtn.disabled = true;

          const response = await fetch(endpoint, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(formData),
          });

          const result = await response.json();

          submitBtn.innerHTML = originalText;
          submitBtn.disabled = false;

          if (result.success) {
            showNotification("success", result.message);
            console.log("Wysłane dane:", formData);
            console.log("Odpowiedź serwera:", result);
            form.reset();
          } else {
            showNotification("error", result.message || "Wystąpił błąd");
          }
        } catch (error) {
          console.error("Błąd API:", error);
          showNotification("error", "Błąd połączenia z serwerem");

          const submitBtn = form.querySelector(".submit-btn");
          submitBtn.innerHTML = originalText;
          submitBtn.disabled = false;
        }
      } else {
        console.log("Dane formularza (bez API):", formData);
        showNotification(
          "info",
          "Dane odebrane, ale endpoint API nie jest skonfigurowany"
        );
        form.reset();
      }
    });
  });
}

function addFieldNames() {
  
  const customerFieldMap = {
    "np. Jan": "firstName",
    "np. Kowalski": "lastName",
    "np. jan@example.com": "email",
    "np. +48 123 456 789": "phone",
    "np. ul. Przykładowa 123, 00-001 Warszawa": "address",
  };

  const productFieldMap = {
    "np. Laptop Dell XPS 13": "productName",
    "np. 3999.99": "price",
    "np. 2999.99": "costPrice",
    "np. 50": "stock",
    "np. Wysokiej jakości laptop": "description",
  };

  const customerForm = document.getElementById("customers-form");
  if (customerForm) {
    assignNamesToFields(customerForm, customerFieldMap);
  }

  const productForm = document.getElementById("products-form");
  if (productForm) {
    assignNamesToFields(productForm, productFieldMap);
  }

  
  document.querySelectorAll("form").forEach((form) => {
    form.querySelectorAll("input, select, textarea").forEach((field) => {
      if (
        !field.hasAttribute("name") &&
        !["button", "submit"].includes(field.type)
      ) {
        
        const placeholder = field.getAttribute("placeholder");
        if (placeholder) {
          if (customerFieldMap[placeholder]) {
            field.setAttribute("name", customerFieldMap[placeholder]);
          } else if (productFieldMap[placeholder]) {
            field.setAttribute("name", productFieldMap[placeholder]);
          } else if (
            placeholder.includes("imię") ||
            placeholder.includes("Imię")
          ) {
            field.setAttribute("name", "firstName");
          } else if (
            placeholder.includes("nazwisko") ||
            placeholder.includes("Nazwisko")
          ) {
            field.setAttribute("name", "lastName");
          } else if (
            placeholder.includes("email") ||
            placeholder.includes("@")
          ) {
            field.setAttribute("name", "email");
          } else if (
            placeholder.includes("telefon") ||
            placeholder.includes("+")
          ) {
            field.setAttribute("name", "phone");
          } else if (
            placeholder.includes("adres") ||
            placeholder.includes("ul.")
          ) {
            field.setAttribute("name", "address");
          } else if (placeholder.includes("cena")) {
            field.setAttribute("name", "price");
          } else if (
            placeholder.includes("ilość") ||
            placeholder.includes("stan")
          ) {
            field.setAttribute("name", "quantity");
          } else {
            const label = field.previousElementSibling;
            if (label && label.tagName === "LABEL") {
              const labelText = label.textContent.trim().toLowerCase();
              const fieldName = labelText
                .replace(/[^a-zA-Z0-9]+(.)/g, (m, chr) => chr.toUpperCase())
                .replace(/[^a-zA-Z0-9]+$/, "")
                .replace(/^[A-Z]/, (firstChar) => firstChar.toLowerCase());

              field.setAttribute("name", fieldName);
            } else {
              const fieldName =
                field.id || `field_${Math.random().toString(36).substr(2, 5)}`;
              field.setAttribute("name", fieldName);
            }
          }
        } else {
          const label = field.previousElementSibling;
          if (label && label.tagName === "LABEL") {
            const labelText = label.textContent.trim().toLowerCase();
            const fieldName = labelText
              .replace(/[^a-zA-Z0-9]+(.)/g, (m, chr) => chr.toUpperCase())
              .replace(/[^a-zA-Z0-9]+$/, "")
              .replace(/^[A-Z]/, (firstChar) => firstChar.toLowerCase());

            field.setAttribute("name", fieldName);
          } else {
            const fieldName =
              field.id || `field_${Math.random().toString(36).substr(2, 5)}`;
            field.setAttribute("name", fieldName);
          }
        }

        console.log(`Dodano nazwę pola "${field.name}" dla elementu:`, field);
      }
    });
  });
}

function assignNamesToFields(form, fieldMap) {
  if (!form) return;

  form.querySelectorAll("input, select, textarea").forEach((field) => {
    const placeholder = field.getAttribute("placeholder");
    if (placeholder && fieldMap[placeholder]) {
      field.setAttribute("name", fieldMap[placeholder]);
      console.log(
        `Ustawiono nazwę pola "${fieldMap[placeholder]}" dla elementu z placeholderem "${placeholder}"`
      );
    }
  });
}

function collectFormData(form) {
  const formData = {};

  form.querySelectorAll("input, select, textarea").forEach((field) => {
    if (!["button", "submit"].includes(field.type) && field.name) {
      formData[field.name] = field.value || "";
    }
  });

  return formData;
}

function getApiEndpoint(sectionId, form) {
  
  if (sectionId.startsWith("sql-")) {
    if (sectionId === "sql-sellers") {
      return "/api/sql/sellers";
    } else {
      const activeTab = form
        .closest(".dashboard-section")
        .querySelector(".table-tab-btn.active");
      if (activeTab) {
        const tableType = activeTab.getAttribute("data-table");
        return sectionId === "sql-banking"
          ? `/api/sql/banking/${tableType}`
          : `/api/sql/${tableType}`;
      }
    }
  }
  
  else if (sectionId.startsWith("mongo-")) {
    return `/api/mongo/${sectionId.replace("mongo-", "")}`;
  }
  
  else if (sectionId.startsWith("azure-")) {
    return `/api/azure/${sectionId.replace("azure-", "")}`;
  }

  return null;
}


function setupHelpModal() {
  const helpBtn = document.getElementById("helpBtn");
  const helpModal = document.getElementById("helpModal");
  const closeHelpBtn = document.getElementById("closeHelpBtn");

  if (helpBtn && helpModal && closeHelpBtn) {
    helpBtn.addEventListener("click", () =>
      helpModal.classList.remove("hidden")
    );
    closeHelpBtn.addEventListener("click", () =>
      helpModal.classList.add("hidden")
    );

    
    helpModal.addEventListener("click", function (e) {
      if (e.target === helpModal) {
        helpModal.classList.add("hidden");
      }
    });
  }
}


window.showNotification = function (type, message) {
  const notification = document.createElement("div");

  
  const styles = {
    success: {
      bg: "bg-green-100 border-green-500 text-green-700",
      icon: "fa-check-circle",
      title: "Sukces!",
    },
    error: {
      bg: "bg-red-100 border-red-500 text-red-700",
      icon: "fa-exclamation-circle",
      title: "Błąd!",
    },
    info: {
      bg: "bg-blue-100 border-blue-500 text-blue-700",
      icon: "fa-info-circle",
      title: "Informacja",
    },
  };

  const style = styles[type] || styles.info;

  
  notification.className = `fixed bottom-4 right-4 p-4 rounded shadow-md z-50 flex items-center border-l-4 ${style.bg}`;
  notification.innerHTML = `
    <i class="fas ${style.icon} mr-3"></i>
    <div>
      <p class="font-medium">${style.title}</p>
      <p class="text-sm">${message}</p>
    </div>
  `;

  document.body.appendChild(notification);

  
  setTimeout(() => {
    notification.style.opacity = "0";
    notification.style.transition = "opacity 0.5s";

    setTimeout(() => {
      if (document.body.contains(notification)) {
        document.body.removeChild(notification);
      }
    }, 500);
  }, 4000);
};


function setupFileUploads() {
  document.querySelectorAll('input[type="file"]').forEach((input) => {
    input.addEventListener("change", function () {
      const form = this.closest("form");
      if (!form) return;

      const jsonArea = form.querySelector('textarea[placeholder*="JSON"]');
      if (jsonArea && this.files && this.files[0]) {
        const reader = new FileReader();
        reader.onload = function (e) {
          try {
            if (input.accept && input.accept.includes("json")) {
              const json = JSON.parse(e.target.result);
              jsonArea.value = JSON.stringify(json, null, 2);
            } else {
              jsonArea.value = e.target.result;
            }
          } catch (error) {
            jsonArea.value =
              "Błąd parsowania JSON: " +
              error.message +
              "\n\n" +
              e.target.result;
          }
        };
        reader.readAsText(this.files[0]);
      }
    });
  });
}


let activityChart;

function initAnalytics() {
  const customersEl = document.getElementById("kpi-customers");
  const sellersEl = document.getElementById("kpi-sellers");
  const categoriesEl = document.getElementById("kpi-categories");
  const totalEl = document.getElementById("kpi-total");
  const refreshBtn = document.getElementById("refreshAnalytics");

  if (!customersEl || !sellersEl || !categoriesEl || !totalEl) return;

  function setLoading(on) {
    [customersEl, sellersEl, categoriesEl, totalEl].forEach((el) => {
      if (on) {
        el.classList.add("skeleton");
        el.textContent = "—";
      } else {
        el.classList.remove("skeleton");
      }
    });
  }

  async function loadKpis() {
    setLoading(true);
    try {
      
      console.log("📊 Pobieranie statystyk z /api/sql/stats...");
      const res = await fetch("/api/sql/stats");
      
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}: ${res.statusText}`);
      }
      
      const statsArray = await res.json();
      console.log("📦 Otrzymane dane:", statsArray);
      
      const stats = Array.isArray(statsArray) ? statsArray[0] : statsArray;
      if (!stats) {
        throw new Error("Statystyki nie zawierają danych");
      }
      
      
      const customers = stats.customers || 0;
      const sellers = stats.sellers || 0;
      const categories = stats.categories || 0;
      const products = stats.products || 0;
      const orders = stats.orders || 0;
      const total = customers + sellers + categories + products + orders;

      console.log(`✓ Statystyki: Klienci=${customers}, Sprzedawcy=${sellers}, Kategorie=${categories}, Produkty=${products}, Zamówienia=${orders}, Razem=${total}`);

      customersEl.textContent = formatNumber(customers);
      sellersEl.textContent = formatNumber(sellers);
      categoriesEl.textContent = formatNumber(categories);
      totalEl.textContent = formatNumber(total);

      
      renderActivityChart(customers, sellers, categories);
    } catch (e) {
      console.error("❌ Błąd KPI:", e);
      showNotification("error", "Nie udało się odczytać statystyk: " + e.message);
      
      
      customersEl.textContent = "—";
      sellersEl.textContent = "—";
      categoriesEl.textContent = "—";
      totalEl.textContent = "—";
    } finally {
      setLoading(false);
    }
  }

  if (refreshBtn) refreshBtn.addEventListener("click", loadKpis);
  loadKpis();

  
  setupPowerBIButtons();
}


function setupPowerBIButtons() {
  const powerBiButtons = document.querySelectorAll(".analytics-btn.primary");

  powerBiButtons.forEach((btn) => {
    const text = btn.textContent.trim();
    if (text.includes("Power BI")) {
      btn.addEventListener("click", function () {
        
        showNotification(
          "info",
          "Integracja Power BI będzie dostępna wkrótce. Kontakt z administratorem."
        );

        
        
      });
    } else if (text.includes("Pobierz raport")) {
      btn.addEventListener("click", function () {
        showNotification(
          "info",
          "Funkcja pobierania raportów w przygotowaniu."
        );
        
      });
    } else if (text.includes("metryki")) {
      btn.addEventListener("click", function () {
        showNotification("info", "Panel metryk Azure w przygotowaniu.");
        
      });
    }
  });
}

async function fetchCount(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const data = await res.json();
  if (Array.isArray(data)) return data.length;
  if (data && typeof data === "object") return Object.keys(data).length;
  return 0;
}

function formatNumber(n) {
  try {
    return new Intl.NumberFormat("pl-PL").format(n);
  } catch (_) {
    return String(n);
  }
}

function renderActivityChart(c, s, k) {
  const ctx = document.getElementById("activityChart");
  if (!ctx) return;

  const labels = Array.from({ length: 8 }, (_, i) => `T${i + 1}`);
  const series = seededSeries(c, s, k, labels.length);

  const data = {
    labels,
    datasets: [
      {
        label: "Zdarzenia",
        data: series,
        borderColor: "#2563eb",
        backgroundColor: "rgba(37, 99, 235, 0.15)",
        tension: 0.35,
        fill: true,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      x: {
        ticks: { color: "#334155" },
        grid: { color: "rgba(100, 116, 139, 0.15)" },
      },
      y: {
        ticks: { color: "#334155" },
        grid: { color: "rgba(100, 116, 139, 0.15)" },
        beginAtZero: true,
      },
    },
    plugins: {
      legend: { labels: { color: "#334155" } },
      tooltip: { mode: "index", intersect: false },
    },
  };

  
  ctx.parentElement.style.height = "280px";

  if (activityChart) {
    activityChart.data = data;
    activityChart.options = options;
    activityChart.update();
  } else if (typeof Chart !== "undefined") {
    activityChart = new Chart(ctx, { type: "line", data, options });
  }
}

function seededSeries(a, b, c, len) {
  
  let seed = (a + 1) * 13 + (b + 1) * 7 + (c + 1) * 3;
  const out = [];
  for (let i = 0; i < len; i++) {
    seed = (seed * 9301 + 49297) % 233280;
    const rnd = seed / 233280;
    out.push(Math.round((rnd * (a + b + c + 10)) / 10 + i * 1.75));
  }
  return out;
}


let currentTableData = [];
let filteredData = [];
let currentPage = 1;
const rowsPerPage = 10;

window.loadTableData = async function (tableName) {
  try {
    
    document
      .querySelectorAll(".data-view-btn")
      .forEach((btn) => btn.classList.remove("active"));
    event.target.classList.add("active");

    const res = await fetch(`/api/sql/${tableName}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);

    const data = await res.json();
    currentTableData = Array.isArray(data) ? data : [];
    filteredData = [...currentTableData];
    currentPage = 1;

    renderTable();
    showNotification(
      "success",
      `Załadowano ${currentTableData.length} rekordów z tabeli ${tableName}`
    );
  } catch (err) {
    console.error("Error loading table:", err);
    showNotification("error", "Błąd podczas ładowania danych");
    currentTableData = [];
    filteredData = [];
    renderTable();
  }
};

window.refreshDataTable = function () {
  const activeBtn = document.querySelector(".data-view-btn.active");
  if (activeBtn) {
    activeBtn.click();
  }
};

function renderTable() {
  const thead = document.getElementById("dataTableHeader");
  const tbody = document.getElementById("dataTableBody");
  const pagination = document.getElementById("tablePagination");

  if (!filteredData.length) {
    thead.innerHTML = '<th class="px-4 py-3 text-left">Brak danych</th>';
    tbody.innerHTML = `
      <tr>
        <td class="px-4 py-8 text-center text-gray-500">
          <i class="fas fa-inbox text-4xl text-gray-300 mb-2"></i>
          <p>Brak danych do wyświetlenia</p>
        </td>
      </tr>
    `;
    pagination.classList.add("hidden");
    return;
  }

  
  const keys = Object.keys(filteredData[0]);
  thead.innerHTML = keys
    .map(
      (key) => `
    <th class="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider" onclick="sortTable('${key}')">
      ${key} <i class="fas fa-sort text-xs ml-1"></i>
    </th>
  `
    )
    .join("");

  
  const start = (currentPage - 1) * rowsPerPage;
  const end = start + rowsPerPage;
  const pageData = filteredData.slice(start, end);

  
  tbody.innerHTML = pageData
    .map(
      (row) => `
    <tr class="hover:bg-gray-50 transition-colors">
      ${keys
        .map(
          (key) =>
            `<td class="px-4 py-3 text-sm text-gray-700">${
              row[key] ?? "—"
            }</td>`
        )
        .join("")}
    </tr>
  `
    )
    .join("");

  
  pagination.classList.remove("hidden");
  document.getElementById("paginationInfo").textContent = `${
    start + 1
  }-${Math.min(end, filteredData.length)} z ${filteredData.length}`;
}

window.sortTable = function (key) {
  const isAsc = filteredData[0] && filteredData[0]._sortAsc;
  filteredData.sort((a, b) => {
    if (a[key] == null) return 1;
    if (b[key] == null) return -1;
    const compare = a[key] > b[key] ? 1 : a[key] < b[key] ? -1 : 0;
    return isAsc ? -compare : compare;
  });
  filteredData.forEach((r) => (r._sortAsc = !isAsc));
  renderTable();
};

window.prevPage = function () {
  if (currentPage > 1) {
    currentPage--;
    renderTable();
  }
};

window.nextPage = function () {
  const maxPage = Math.ceil(filteredData.length / rowsPerPage);
  if (currentPage < maxPage) {
    currentPage++;
    renderTable();
  }
};


const searchInput = document.getElementById("dataTableSearch");
if (searchInput) {
  searchInput.addEventListener("input", (e) => {
    const query = e.target.value.toLowerCase();
    filteredData = currentTableData.filter((row) => {
      return Object.values(row).some((val) =>
        String(val).toLowerCase().includes(query)
      );
    });
    currentPage = 1;
    renderTable();
  });
}


let allTransactions = [];
let filteredTransactions = [];
let currentTransactionType = "all";

window.loadTransactionsByType = function (type) {
  currentTransactionType = type;

  
  document
    .querySelectorAll(".transaction-filter-btn")
    .forEach((btn) => btn.classList.remove("active"));
  event.target.classList.add("active");

  filterAndDisplayTransactions();
};

window.refreshTransactions = async function () {
  try {
    console.log("[*] Fetching transactions from MongoDB...");
    
    
    const params = new URLSearchParams();
    params.append('limit', '100');
    
    const url = `/api/mongo/transactions?${params.toString()}`;
    console.log("[*] Requesting:", url);
    
    const response = await fetch(url);
    
    console.log("[*] Response status:", response.status);
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error("[!] Error response:", errorText);
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    console.log("[*] Received data:", data);
    
    
    if (!data || data.length === 0) {
      console.warn("[!] No transaction data received from MongoDB");
      showNotification("warning", "Brak transakcji w bazie MongoDB. Upewnij się, że dane zostały załadowane.");
      allTransactions = [];
      filteredTransactions = [];
      renderTransactionCards();
      updateTransactionStats();
      return;
    }
    
    
    allTransactions = data.map(t => {
      
      let mappedType = t.TransactionType.toLowerCase();
      if (mappedType === 'credit') mappedType = 'deposit';
      if (mappedType === 'debit') mappedType = 'withdrawal';
      
      return {
        id: t.TransactionID,
        accountNumber: t.AccountNumber,
        currency: t.Currency,
        amount: Math.abs(t.Amount),
        type: mappedType,
        description: t.Description || 'Brak opisu',
        date: new Date(t.TransactionDate).toLocaleDateString('pl-PL'),
        status: t.Status || 'completed',
        counterparty: t.Counterparty || '-',
        reference: t.ReferenceNumber || '-',
        seller: t.SellerName || 'N/A'
      };
    });
    
    console.log("[+] Transformed transactions:", allTransactions.length);
    
    filteredTransactions = [...allTransactions];

    filterAndDisplayTransactions();
    
    
    
    showNotification(
      "success",
      `Załadowano ${allTransactions.length} transakcji z MongoDB`
    );
  } catch (err) {
    console.error("[!] Error loading transactions:", err);
    showNotification("error", `Błąd podczas ładowania transakcji: ${err.message}`);
    
    
    const container = document.getElementById("transactionCardsContainer");
    if (container) {
      container.innerHTML = `
        <div class="col-span-full text-center py-12">
          <i class="fas fa-exclamation-triangle text-5xl text-red-300 mb-3"></i>
          <p class="text-red-600 font-medium mb-2">Błąd połączenia z MongoDB</p>
          <p class="text-gray-600 text-sm">${err.message}</p>
          <p class="text-gray-500 text-xs mt-2">Sprawdź konsolę przeglądarki aby zobaczyć szczegóły</p>
        </div>
      `;
    }
    
    
    document.getElementById('totalTransactions').textContent = '0';
    document.getElementById('totalDeposits').textContent = '0.00';
    document.getElementById('totalWithdrawals').textContent = '0.00';
    document.getElementById('totalBalance').textContent = '0.00';
  }
};

async function updateMongoTransactionStats() {
  try {
    console.log("[*] Fetching transaction stats from MongoDB...");
    const response = await fetch('/api/mongo/transaction-stats');
    
    if (!response.ok) {
      console.warn("[!] Stats request failed:", response.status);
      return;
    }
    
    const stats = await response.json();
    console.log("[*] Received stats:", stats);
    
    const statsData = stats[0] || stats;
    
    document.getElementById('totalTransactions').textContent = statsData.total || 0;
    document.getElementById('totalDeposits').textContent = statsData.deposits ? statsData.deposits.toFixed(2) : '0.00';
    document.getElementById('totalWithdrawals').textContent = statsData.withdrawals ? Math.abs(statsData.withdrawals).toFixed(2) : '0.00';
    document.getElementById('totalBalance').textContent = statsData.balance ? statsData.balance.toFixed(2) : '0.00';
    
    console.log("[+] Stats updated successfully");
  } catch (err) {
    console.error("[!] Error loading stats:", err);
  }
}

function filterAndDisplayTransactions() {
  const searchQuery =
    document.getElementById("transactionSearch")?.value.toLowerCase() || "";
  const currencyFilter = document.getElementById("currencyFilter")?.value || "";

  filteredTransactions = allTransactions.filter((t) => {
    const matchesType =
      currentTransactionType === "all" || t.type === currentTransactionType;
    const matchesSearch =
      !searchQuery ||
      t.accountNumber.toLowerCase().includes(searchQuery) ||
      t.amount.toString().includes(searchQuery) ||
      t.description.toLowerCase().includes(searchQuery);
    const matchesCurrency = !currencyFilter || t.currency === currencyFilter;

    return matchesType && matchesSearch && matchesCurrency;
  });

  renderTransactionCards();
  updateTransactionStats();
}

function renderTransactionCards() {
  const container = document.getElementById("transactionCardsContainer");
  if (!container) return;

  if (!filteredTransactions.length) {
    container.innerHTML = `
      <div class="col-span-full text-center py-12 text-gray-500">
        <i class="fas fa-inbox text-5xl text-gray-300 mb-3"></i>
        <p>Brak transakcji do wyświetlenia</p>
      </div>
    `;
    return;
  }

  container.innerHTML = filteredTransactions
    .map(
      (t) => `
    <div class="transaction-card ${t.type}">
      <div class="flex justify-between items-start mb-2">
        <div class="flex items-center gap-2">
          <i class="fas fa-${getTransactionIcon(t.type)} ${getTransactionColor(
        t.type
      )}"></i>
          <span class="font-semibold text-gray-800">${getTransactionTypeLabel(
            t.type
          )}</span>
        </div>
        <span class="text-xs text-gray-500">${t.date}</span>
      </div>
      <div class="mb-2">
        <div class="text-2xl font-bold ${getAmountColor(t.type)}">
          ${t.type === "withdrawal" ? "-" : "+"}${t.amount.toFixed(2)} ${
        t.currency
      }
        </div>
      </div>
      <div class="text-sm text-gray-600 mb-1">
        <i class="fas fa-university mr-1"></i> ${t.accountNumber}
      </div>
      <div class="text-sm text-gray-600 mb-2">
        ${t.description}
      </div>
      <div class="flex justify-between items-center pt-2 border-t border-gray-100">
        <span class="text-xs text-gray-500">ID: ${t.id}</span>
        <span class="px-2 py-1 rounded text-xs font-medium ${getStatusBadge(
          t.status
        )}">
          ${t.status}
        </span>
      </div>
    </div>
  `
    )
    .join("");
}

function updateTransactionStats() {
  
  const deposits = allTransactions.filter((t) => 
    t.type === "deposit" || t.type === "credit" || t.type === "incoming"
  );
  const withdrawals = allTransactions.filter((t) => 
    t.type === "withdrawal" || t.type === "debit" || t.type === "outgoing"
  );

  const totalDeposits = deposits.reduce((sum, t) => sum + t.amount, 0);
  const totalWithdrawals = withdrawals.reduce((sum, t) => sum + t.amount, 0);
  const balance = totalDeposits - totalWithdrawals;

  
  document.getElementById("totalTransactions").textContent = allTransactions.length;
  document.getElementById("totalDeposits").textContent = totalDeposits.toFixed(2);
  document.getElementById("totalWithdrawals").textContent = totalWithdrawals.toFixed(2);
  document.getElementById("totalBalance").textContent = balance.toFixed(2);
  
  console.log(`[+] Stats: ${allTransactions.length} total, ${deposits.length} deposits (${totalDeposits.toFixed(2)}), ${withdrawals.length} withdrawals (${totalWithdrawals.toFixed(2)}), balance: ${balance.toFixed(2)}`);
}

function generateMockTransactions(count) {
  const types = ["deposit", "withdrawal", "transfer"];
  const currencies = ["PLN", "EUR", "USD", "GBP"];
  const statuses = ["Completed", "Pending", "Processing"];
  const descriptions = [
    "Przelew przychodzący",
    "Wypłata z bankomatu",
    "Płatność kartą",
    "Przelew wychodzący",
    "Wpłata gotówki",
    "Zwrot transakcji",
    "Opłata serwisowa",
  ];

  return Array.from({ length: count }, (_, i) => ({
    id: `TRX${1000 + i}`,
    type: types[Math.floor(Math.random() * types.length)],
    amount: Math.random() * 5000 + 100,
    currency: currencies[Math.floor(Math.random() * currencies.length)],
    accountNumber: `PL${
      Math.floor(Math.random() * 90000000000000) + 10000000000000
    }`,
    description: descriptions[Math.floor(Math.random() * descriptions.length)],
    date: new Date(
      Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000
    ).toLocaleDateString("pl-PL"),
    status: statuses[Math.floor(Math.random() * statuses.length)],
  }));
}

function getTransactionIcon(type) {
  const icons = {
    deposit: "arrow-down",
    withdrawal: "arrow-up",
    transfer: "exchange-alt",
  };
  return icons[type] || "circle";
}

function getTransactionColor(type) {
  const colors = {
    deposit: "text-green-600",
    withdrawal: "text-red-600",
    transfer: "text-purple-600",
  };
  return colors[type] || "text-gray-600";
}

function getAmountColor(type) {
  const colors = {
    deposit: "text-green-700",
    withdrawal: "text-red-700",
    transfer: "text-purple-700",
  };
  return colors[type] || "text-gray-700";
}

function getTransactionTypeLabel(type) {
  const labels = {
    deposit: "Wpłata",
    withdrawal: "Wypłata",
    transfer: "Przelew",
  };
  return labels[type] || type;
}

function getStatusBadge(status) {
  const badges = {
    Completed: "bg-green-100 text-green-800",
    Pending: "bg-yellow-100 text-yellow-800",
    Processing: "bg-blue-100 text-blue-800",
  };
  return badges[status] || "bg-gray-100 text-gray-800";
}


const transactionSearch = document.getElementById("transactionSearch");
if (transactionSearch) {
  transactionSearch.addEventListener("input", filterAndDisplayTransactions);
}

const currencyFilter = document.getElementById("currencyFilter");
if (currencyFilter) {
  currencyFilter.addEventListener("change", filterAndDisplayTransactions);
}


function showNotification(type, message) {
  const notificationId = `notification-${Date.now()}`;
  const notificationHTML = `
    <div id="${notificationId}" class="fixed top-4 right-4 px-6 py-3 rounded-lg shadow-lg text-white z-50 animate-slide-up" style="background-color: ${
      type === 'success' ? '#10b981' :
      type === 'error' ? '#ef4444' :
      type === 'warning' ? '#f59e0b' :
      '#3b82f6'
    }">
      <div class="flex items-center gap-2">
        <i class="fas fa-${
          type === 'success' ? 'check-circle' :
          type === 'error' ? 'exclamation-circle' :
          type === 'warning' ? 'exclamation-triangle' :
          'info-circle'
        }"></i>
        <span>${message}</span>
      </div>
    </div>
  `;
  
  const notificationContainer = document.body;
  const notificationEl = document.createElement('div');
  notificationEl.innerHTML = notificationHTML;
  notificationContainer.appendChild(notificationEl.firstElementChild);
  
  
  setTimeout(() => {
    const el = document.getElementById(notificationId);
    if (el) {
      el.style.opacity = '0';
      el.style.transition = 'opacity 0.3s ease';
      setTimeout(() => el.remove(), 300);
    }
  }, 3000);
}


async function loadTableData(tableName) {
  console.log(`[*] Loading data for table: ${tableName}`);
  
  const targetTable = document.getElementById('dataTable');
  if (!targetTable) {
    console.error("[-] No dataTable element found");
    return;
  }
  
  try {
    
    const response = await fetch(`/api/sql/${tableName}`);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const data = await response.json();
    console.log(`[+] Received ${data.length} records for ${tableName}`);
    
    if (!data || data.length === 0) {
      showNotification('warning', `Brak danych dla tabeli ${tableName}`);
      return;
    }
    
    
    const columns = Object.keys(data[0]);
    console.log(`[*] Columns: ${columns.join(', ')}`);
    
    
    const thead = targetTable.querySelector('thead');
    const headerRow = thead.querySelector('tr');
    headerRow.innerHTML = '';
    
    columns.forEach(col => {
      const th = document.createElement('th');
      th.className = 'px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider';
      th.textContent = col;
      headerRow.appendChild(th);
    });
    
    
    const tbody = targetTable.querySelector('tbody');
    tbody.innerHTML = '';
    
    data.forEach((row, idx) => {
      const tr = document.createElement('tr');
      tr.className = 'border-b border-gray-200 hover:bg-gray-50';
      
      columns.forEach(col => {
        const td = document.createElement('td');
        td.className = 'px-4 py-3 text-sm text-gray-700';
        
        let value = row[col];
        
        
        if (value === null || value === undefined) {
          td.textContent = '—';
          td.className += ' text-gray-400';
        } else if (typeof value === 'boolean') {
          td.textContent = value ? 'Tak' : 'Nie';
        } else if (typeof value === 'number' && col.toLowerCase().includes('price')) {
          td.textContent = new Intl.NumberFormat('pl-PL', { style: 'currency', currency: 'PLN' }).format(value);
        } else if (typeof value === 'number' && value > 1000000) {
          
          td.textContent = new Date(value).toLocaleDateString('pl-PL');
        } else if (typeof value === 'string' && value.length > 50) {
          td.textContent = value.substring(0, 47) + '...';
          td.title = value;
        } else {
          td.textContent = String(value);
        }
        
        tr.appendChild(td);
      });
      
      tbody.appendChild(tr);
    });
    
    showNotification('success', `Zaladowano ${data.length} rekordow z tabeli ${tableName}`);
    
  } catch (error) {
    console.error(`[-] Error loading data: ${error}`);
    showNotification('error', `Blad podczas ladowania ${tableName}: ${error.message}`);
  }
}


async function loadTableDataToSpecificTable(tableName, tableElementId) {
  console.log(`[*] Loading data for ${tableName} to table #${tableElementId}`);
  
  const targetTable = document.getElementById(tableElementId);
  if (!targetTable) {
    console.error(`[-] No table element found with id: ${tableElementId}`);
    return;
  }
  
  try {
    
    const response = await fetch(`/api/sql/${tableName}`);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const data = await response.json();
    console.log(`[+] Received ${data.length} records for ${tableName}`);
    
    if (!data || data.length === 0) {
      console.warn(`[!] No data found for ${tableName}`);
      return;
    }
    
    
    const columns = Object.keys(data[0]);
    console.log(`[*] Columns: ${columns.join(', ')}`);
    
    
    const thead = targetTable.querySelector('thead');
    const headerRow = thead.querySelector('tr');
    headerRow.innerHTML = '';
    
    columns.forEach(col => {
      const th = document.createElement('th');
      th.className = 'px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider';
      th.textContent = col;
      headerRow.appendChild(th);
    });
    
    
    const tbody = targetTable.querySelector('tbody');
    tbody.innerHTML = '';
    
    data.slice(0, 20).forEach((row, idx) => {  
      const tr = document.createElement('tr');
      tr.className = 'border-b border-gray-200 hover:bg-gray-50';
      
      columns.forEach(col => {
        const td = document.createElement('td');
        td.className = 'px-4 py-3 text-sm text-gray-700';
        
        let value = row[col];
        
        
        if (value === null || value === undefined) {
          td.textContent = '—';
          td.className += ' text-gray-400';
        } else if (typeof value === 'boolean') {
          td.textContent = value ? 'Tak' : 'Nie';
        } else if (typeof value === 'number' && (col.toLowerCase().includes('price') || col.toLowerCase().includes('commission'))) {
          td.textContent = new Intl.NumberFormat('pl-PL', { style: 'currency', currency: 'PLN' }).format(value);
        } else if (typeof value === 'string' && value.length > 40) {
          td.textContent = value.substring(0, 37) + '...';
          td.title = value;
        } else {
          td.textContent = String(value);
        }
        
        tr.appendChild(td);
      });
      
      tbody.appendChild(tr);
    });
    
    console.log(`[+] Successfully loaded ${Math.min(data.length, 20)} records to #${tableElementId}`);
    
  } catch (error) {
    console.error(`[-] Error loading data to ${tableElementId}: ${error}`);
  }
}






async function checkAzureSQLTables() {
  try {
    const statusDiv = document.getElementById('azure-sql-tables-status');
    statusDiv.innerHTML = '<div class="spinner"></div><span class="text-gray-600">Sprawdzanie...</span>';
    
    const response = await fetch('/api/azure/sql/status');
    const data = await response.json();
    
    if (!data.success || !data.connected) {
      statusDiv.innerHTML = `
        <div class="bg-red-50 border-l-4 border-red-400 p-4">
          <div class="flex">
            <i class="fas fa-times-circle text-red-600 mr-3"></i>
            <div>
              <p class="text-sm text-red-700">Brak połączenia z Azure SQL Database</p>
              <p class="text-xs text-red-600 mt-1">${data.message || ''}</p>
            </div>
          </div>
        </div>`;
      document.getElementById('azure-sql-status').innerHTML = '<i class="fas fa-times-circle text-red-600 mr-2"></i><span class="text-red-600">Niepołączone</span>';
      return;
    }
    
    
    document.getElementById('azure-sql-status').innerHTML = '<i class="fas fa-check-circle text-green-600 mr-2"></i><span class="text-green-600">Połączono</span>';
    
    
    document.getElementById('azure-total-records').textContent = data.total_records.toLocaleString();
    document.getElementById('azure-populated-tables').textContent = data.populated_tables;
    document.getElementById('azure-empty-tables').textContent = data.empty_tables;
    
    
    let html = '<div class="space-y-1">';
    for (const [table, count] of Object.entries(data.tables)) {
      const status = count > 0 ? 'text-green-600' : 'text-gray-400';
      const icon = count > 0 ? 'check-circle' : 'circle';
      html += `
        <div class="flex justify-between items-center py-2 px-3 bg-gray-50 rounded">
          <div class="flex items-center">
            <i class="fas fa-${icon} ${status} mr-2"></i>
            <span class="font-medium">${table}</span>
          </div>
          <span class="${status} font-mono text-sm">${count >= 0 ? count.toLocaleString() : 'ERROR'}</span>
        </div>`;
    }
    html += '</div>';
    statusDiv.innerHTML = html;
    
  } catch (error) {
    console.error('Error checking Azure SQL:', error);
    document.getElementById('azure-sql-tables-status').innerHTML = `
      <div class="bg-red-50 border-l-4 border-red-400 p-4">
        <p class="text-sm text-red-700">Błąd: ${error.message}</p>
      </div>`;
  }
}


async function checkCosmosDBStatus() {
  try {
    const statusDiv = document.getElementById('azure-cosmos-collections-status');
    statusDiv.innerHTML = '<div class="spinner"></div><span class="text-gray-600">Sprawdzanie...</span>';
    
    const response = await fetch('/api/azure/cosmos/status');
    const data = await response.json();
    
    if (!data.success || !data.connected) {
      statusDiv.innerHTML = `
        <div class="bg-red-50 border-l-4 border-red-400 p-4">
          <div class="flex">
            <i class="fas fa-times-circle text-red-600 mr-3"></i>
            <div>
              <p class="text-sm text-red-700">Brak połączenia z Cosmos DB</p>
              <p class="text-xs text-red-600 mt-1">${data.message || ''}</p>
            </div>
          </div>
        </div>`;
      document.getElementById('azure-cosmos-status').innerHTML = '<i class="fas fa-times-circle text-red-600 mr-2"></i><span class="text-red-600">Niepołączone</span>';
      return;
    }
    
    
    document.getElementById('azure-cosmos-status').innerHTML = '<i class="fas fa-check-circle text-green-600 mr-2"></i><span class="text-green-600">Połączono</span>';
    
    
    document.getElementById('cosmos-total-documents').textContent = data.total_documents.toLocaleString();
    
    
    let html = '<div class="space-y-1">';
    for (const [collection, count] of Object.entries(data.collections)) {
      const status = count > 0 ? 'text-green-600' : 'text-gray-400';
      const icon = count > 0 ? 'check-circle' : 'circle';
      html += `
        <div class="flex justify-between items-center py-2 px-3 bg-gray-50 rounded">
          <div class="flex items-center">
            <i class="fas fa-${icon} ${status} mr-2"></i>
            <span class="font-medium">${collection}</span>
          </div>
          <span class="${status} font-mono text-sm">${count >= 0 ? count.toLocaleString() : 'ERROR'}</span>
        </div>`;
    }
    html += '</div>';
    statusDiv.innerHTML = html;
    
  } catch (error) {
    console.error('Error checking Cosmos DB:', error);
    document.getElementById('azure-cosmos-collections-status').innerHTML = `
      <div class="bg-red-50 border-l-4 border-red-400 p-4">
        <p class="text-sm text-red-700">Błąd: ${error.message}</p>
      </div>`;
  }
}


async function syncToAzureSQL() {
  try {
    const btn = document.getElementById('sync-btn');
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Synchronizacja...';
    
    
    const tables = [];
    const checkboxes = document.querySelectorAll('[id^="sync-"]');
    checkboxes.forEach(cb => {
      if (cb.checked) {
        const table = cb.id.replace('sync-', '');
        const tableName = table.charAt(0).toUpperCase() + table.slice(1);
        tables.push(tableName);
      }
    });
    
    if (tables.length === 0) {
      alert('Wybierz przynajmniej jedną tabelę do synchronizacji');
      btn.disabled = false;
      btn.innerHTML = '<i class="fas fa-cloud-upload-alt mr-2"></i>Rozpocznij Synchronizację';
      return;
    }
    
    
    const progressDiv = document.getElementById('azure-sql-sync-progress');
    progressDiv.classList.remove('hidden');
    const logDiv = document.getElementById('sync-log');
    logDiv.innerHTML = '';
    
    
    const response = await fetch('/api/azure/sql/sync', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ tables })
    });
    
    const data = await response.json();
    
    if (data.success) {
      let totalInserted = 0;
      let totalErrors = 0;
      
      for (const [table, result] of Object.entries(data.results)) {
        if (result.error) {
          logDiv.innerHTML += `<div class="text-red-600">❌ ${table}: ${result.error}</div>`;
        } else {
          logDiv.innerHTML += `<div class="text-green-600">✅ ${table}: ${result.inserted}/${result.total} rekordów (błędów: ${result.errors})</div>`;
          totalInserted += result.inserted;
          totalErrors += result.errors;
        }
      }
      
      logDiv.innerHTML += `<div class="text-blue-600 font-bold mt-2">Łącznie: ${totalInserted} rekordów zsynchronizowanych, ${totalErrors} błędów</div>`;
      
      
      setTimeout(() => checkAzureSQLTables(), 1000);
    } else {
      logDiv.innerHTML = `<div class="text-red-600">❌ Błąd: ${data.message}</div>`;
    }
    
  } catch (error) {
    console.error('Error syncing to Azure SQL:', error);
    alert('Błąd synchronizacji: ' + error.message);
  } finally {
    const btn = document.getElementById('sync-btn');
    btn.disabled = false;
    btn.innerHTML = '<i class="fas fa-cloud-upload-alt mr-2"></i>Rozpocznij Synchronizację';
  }
}


async function syncToCosmos() {
  try {
    const btn = document.getElementById('cosmos-sync-btn');
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Synchronizacja...';
    
    
    const collections = [];
    if (document.getElementById('sync-purchase-history')?.checked) collections.push('PurchaseHistories');
    if (document.getElementById('sync-customer-behavior')?.checked) collections.push('CustomerBehaviors');
    if (document.getElementById('sync-seller-profiles')?.checked) collections.push('SellerProfiles');
    
    if (collections.length === 0) {
      alert('Wybierz przynajmniej jedną kolekcję do synchronizacji');
      btn.disabled = false;
      btn.innerHTML = '<i class="fas fa-cloud-upload-alt mr-2"></i>Rozpocznij Synchronizację';
      return;
    }
    
    
    const progressDiv = document.getElementById('azure-cosmos-sync-progress');
    progressDiv.classList.remove('hidden');
    const logDiv = document.getElementById('cosmos-sync-log');
    logDiv.innerHTML = '';
    
    
    const response = await fetch('/api/azure/cosmos/sync', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ collections })
    });
    
    const data = await response.json();
    
    if (data.success) {
      let totalInserted = 0;
      let totalErrors = 0;
      
      for (const [collection, result] of Object.entries(data.results)) {
        if (result.error) {
          logDiv.innerHTML += `<div class="text-red-600">❌ ${collection}: ${result.error}</div>`;
        } else {
          logDiv.innerHTML += `<div class="text-green-600">✅ ${collection}: ${result.inserted}/${result.total} dokumentów (błędów: ${result.errors})</div>`;
          totalInserted += result.inserted;
          totalErrors += result.errors;
        }
      }
      
      logDiv.innerHTML += `<div class="text-blue-600 font-bold mt-2">Łącznie: ${totalInserted} dokumentów zsynchronizowanych, ${totalErrors} błędów</div>`;
      
      
      setTimeout(() => checkCosmosDBStatus(), 1000);
    } else {
      logDiv.innerHTML = `<div class="text-red-600">❌ Błąd: ${data.message}</div>`;
    }
    
  } catch (error) {
    console.error('Error syncing to Cosmos DB:', error);
    alert('Błąd synchronizacji: ' + error.message);
  } finally {
    const btn = document.getElementById('cosmos-sync-btn');
    btn.disabled = false;
    btn.innerHTML = '<i class="fas fa-cloud-upload-alt mr-2"></i>Rozpocznij Synchronizację';
  }
}


if (window.location.hash === '#azure-sql') {
  setTimeout(() => checkAzureSQLTables(), 500);
}
if (window.location.hash === '#azure-cosmos') {
  setTimeout(() => checkCosmosDBStatus(), 500);
}


async function loadSelectOptions(selectId, endpoint, valueField, textField) {
  try {
    const response = await fetch(`/api/sql/${endpoint}`);
    const data = await response.json();
    const select = document.getElementById(selectId);
    if (!select) return;
    
    
    const existingOptions = Array.from(select.options).filter(o => !o.value || o.value === '');
    select.innerHTML = '';
    existingOptions.forEach(opt => select.appendChild(opt));
    
    if (Array.isArray(data)) {
      data.forEach(item => {
        const option = document.createElement('option');
        option.value = item[valueField];
        
        
        let displayText = '';
        if (endpoint === 'customers' || endpoint === 'sellers') {
          displayText = `${item[valueField]} - ${item.FirstName || ''} ${item.LastName || ''}`.trim();
        } else if (endpoint === 'products') {
          displayText = `${item[valueField]} - ${item.ProductName || item[textField] || ''}`;
        } else {
          displayText = `${item[valueField]} - ${item[textField] || ''}`;
        }
        
        option.textContent = displayText;
        select.appendChild(option);
      });
    }
  } catch (error) {
    console.error(`Error loading ${endpoint}:`, error);
  }
}


async function updateAzureSQLInsertForm() {
  const table = document.getElementById('azure-insert-table').value;
  const formDiv = document.getElementById('azure-insert-form');
  const btn = document.getElementById('azure-insert-btn');
  
  if (!table) {
    formDiv.classList.add('hidden');
    btn.classList.add('hidden');
    return;
  }
  
  formDiv.classList.remove('hidden');
  btn.classList.remove('hidden');
  
  const forms = {
    customers: `
      <div class="grid grid-cols-2 gap-4">
        <div><label class="block text-sm font-medium text-gray-600 mb-1">Imię</label>
        <input type="text" id="firstName" class="form-input" required></div>
        <div><label class="block text-sm font-medium text-gray-600 mb-1">Nazwisko</label>
        <input type="text" id="lastName" class="form-input" required></div>
        <div><label class="block text-sm font-medium text-gray-600 mb-1">Email</label>
        <input type="email" id="email" class="form-input" required></div>
        <div><label class="block text-sm font-medium text-gray-600 mb-1">Telefon</label>
        <input type="text" id="phone" class="form-input"></div>
        <div class="col-span-2"><label class="block text-sm font-medium text-gray-600 mb-1">Adres</label>
        <input type="text" id="address" class="form-input"></div>
        <div><label class="block text-sm font-medium text-gray-600 mb-1">Kraj</label>
        <select id="countryId" class="form-input"></select></div>
      </div>
    `,
    products: `
      <div class="grid grid-cols-2 gap-4">
        <div><label class="block text-sm font-medium text-gray-600 mb-1">Nazwa produktu</label>
        <input type="text" id="productName" class="form-input" required></div>
        <div><label class="block text-sm font-medium text-gray-600 mb-1">Kategoria</label>
        <select id="categoryId" class="form-input"></select></div>
        <div><label class="block text-sm font-medium text-gray-600 mb-1">Sprzedawca</label>
        <select id="sellerId" class="form-input"></select></div>
        <div><label class="block text-sm font-medium text-gray-600 mb-1">Cena</label>
        <input type="number" step="0.01" id="price" class="form-input" required></div>
        <div><label class="block text-sm font-medium text-gray-600 mb-1">Koszt</label>
        <input type="number" step="0.01" id="costPrice" class="form-input"></div>
        <div><label class="block text-sm font-medium text-gray-600 mb-1">Ilość w magazynie</label>
        <input type="number" id="stockQuantity" class="form-input" value="0"></div>
        <div class="col-span-2"><label class="block text-sm font-medium text-gray-600 mb-1">Opis</label>
        <textarea id="description" class="form-input" rows="2"></textarea></div>
      </div>
    `,
    sellers: `
      <div class="grid grid-cols-2 gap-4">
        <div><label class="block text-sm font-medium text-gray-600 mb-1">Imię</label>
        <input type="text" id="firstName" class="form-input" required></div>
        <div><label class="block text-sm font-medium text-gray-600 mb-1">Nazwisko</label>
        <input type="text" id="lastName" class="form-input" required></div>
        <div><label class="block text-sm font-medium text-gray-600 mb-1">Email</label>
        <input type="email" id="email" class="form-input" required></div>
        <div><label class="block text-sm font-medium text-gray-600 mb-1">Telefon</label>
        <input type="text" id="phone" class="form-input"></div>
        <div><label class="block text-sm font-medium text-gray-600 mb-1">Typ</label>
        <select id="sellerType" class="form-input">
          <option value="Internal">Internal</option>
          <option value="External">External</option>
        </select></div>
        <div><label class="block text-sm font-medium text-gray-600 mb-1">Region</label>
        <select id="regionId" class="form-input"></select></div>
      </div>
    `,
    categories: `
      <div class="grid grid-cols-2 gap-4">
        <div><label class="block text-sm font-medium text-gray-600 mb-1">Nazwa kategorii</label>
        <input type="text" id="categoryName" class="form-input" required></div>
        <div><label class="block text-sm font-medium text-gray-600 mb-1">Kategoria nadrzędna</label>
        <select id="parentCategoryId" class="form-input">
          <option value="">-- Brak --</option>
        </select></div>
        <div class="col-span-2"><label class="block text-sm font-medium text-gray-600 mb-1">Opis</label>
        <textarea id="description" class="form-input" rows="2"></textarea></div>
      </div>
    `,
    countries: `
      <div class="grid grid-cols-2 gap-4">
        <div><label class="block text-sm font-medium text-gray-600 mb-1">Nazwa kraju</label>
        <input type="text" id="countryName" class="form-input" required></div>
        <div><label class="block text-sm font-medium text-gray-600 mb-1">Kontynent</label>
        <input type="text" id="continent" class="form-input" value="Europe"></div>
      </div>
    `,
    regions: `
      <div class="grid grid-cols-2 gap-4">
        <div><label class="block text-sm font-medium text-gray-600 mb-1">Nazwa regionu</label>
        <input type="text" id="regionName" class="form-input" required></div>
        <div><label class="block text-sm font-medium text-gray-600 mb-1">Kraj</label>
        <select id="countryId" class="form-input"></select></div>
      </div>
    `,
    orders: `
      <div class="grid grid-cols-2 gap-4">
        <div><label class="block text-sm font-medium text-gray-600 mb-1">Klient</label>
        <select id="customerId" class="form-input" required></select></div>
        <div><label class="block text-sm font-medium text-gray-600 mb-1">Sprzedawca</label>
        <select id="sellerId" class="form-input"></select></div>
        <div><label class="block text-sm font-medium text-gray-600 mb-1">Całkowity koszt</label>
        <input type="number" step="0.01" id="totalAmount" class="form-input" required></div>
        <div><label class="block text-sm font-medium text-gray-600 mb-1">Status</label>
        <select id="status" class="form-input">
          <option value="Pending">Pending</option>
          <option value="Processing">Processing</option>
          <option value="Shipped">Shipped</option>
          <option value="Delivered">Delivered</option>
          <option value="Cancelled">Cancelled</option>
        </select></div>
        <div class="col-span-2"><label class="block text-sm font-medium text-gray-600 mb-1">Adres wysyłki</label>
        <input type="text" id="shippingAddress" class="form-input"></div>
        <div><label class="block text-sm font-medium text-gray-600 mb-1">Kraj</label>
        <select id="countryId" class="form-input"></select></div>
        <div><label class="block text-sm font-medium text-gray-600 mb-1">Metoda płatności</label>
        <select id="paymentMethod" class="form-input">
          <option value="Credit Card">Karta kredytowa</option>
          <option value="Debit Card">Karta debetowa</option>
          <option value="PayPal">PayPal</option>
          <option value="Bank Transfer">Przelew</option>
          <option value="Cash">Gotówka</option>
        </select></div>
      </div>
    `,
    promotions: `
      <div class="grid grid-cols-2 gap-4">
        <div><label class="block text-sm font-medium text-gray-600 mb-1">Nazwa promocji</label>
        <input type="text" id="promotionName" class="form-input" required></div>
        <div><label class="block text-sm font-medium text-gray-600 mb-1">Procent rabatu (%)</label>
        <input type="number" step="0.01" id="discountPercentage" class="form-input" required></div>
        <div><label class="block text-sm font-medium text-gray-600 mb-1">Produkt</label>
        <select id="productId" class="form-input">
          <option value="">-- Wszystkie produkty --</option>
        </select></div>
        <div><label class="block text-sm font-medium text-gray-600 mb-1">Kategoria</label>
        <select id="categoryId" class="form-input">
          <option value="">-- Wszystkie kategorie --</option>
        </select></div>
        <div><label class="block text-sm font-medium text-gray-600 mb-1">Sprzedawca</label>
        <select id="sellerId" class="form-input">
          <option value="">-- Wszyscy sprzedawcy --</option>
        </select></div>
        <div><label class="block text-sm font-medium text-gray-600 mb-1">Data rozpoczęcia (ID)</label>
        <input type="number" id="startDateId" class="form-input" placeholder="opcjonalne"></div>
        <div><label class="block text-sm font-medium text-gray-600 mb-1">Data zakończenia (ID)</label>
        <input type="number" id="endDateId" class="form-input" placeholder="opcjonalne"></div>
      </div>
    `
  };
  
  formDiv.innerHTML = forms[table] || '<p class="text-gray-500">Formularz niedostępny dla tej tabeli</p>';
  
  
  await new Promise(resolve => setTimeout(resolve, 100)); 
  
  if (table === 'customers') {
    await loadSelectOptions('countryId', 'countries', 'CountryID', 'CountryName');
  } else if (table === 'products') {
    await loadSelectOptions('categoryId', 'categories', 'CategoryID', 'CategoryName');
    await loadSelectOptions('sellerId', 'sellers', 'SellerID', 'FirstName');
  } else if (table === 'sellers') {
    await loadSelectOptions('regionId', 'regions', 'RegionID', 'RegionName');
  } else if (table === 'categories') {
    await loadSelectOptions('parentCategoryId', 'categories', 'CategoryID', 'CategoryName');
  } else if (table === 'regions') {
    await loadSelectOptions('countryId', 'countries', 'CountryID', 'CountryName');
  } else if (table === 'orders') {
    await loadSelectOptions('customerId', 'customers', 'CustomerID', 'FirstName');
    await loadSelectOptions('sellerId', 'sellers', 'SellerID', 'FirstName');
    await loadSelectOptions('countryId', 'countries', 'CountryID', 'CountryName');
  } else if (table === 'promotions') {
    await loadSelectOptions('productId', 'products', 'ProductID', 'ProductName');
    await loadSelectOptions('categoryId', 'categories', 'CategoryID', 'CategoryName');
    await loadSelectOptions('sellerId', 'sellers', 'SellerID', 'FirstName');
  }
}


async function insertToAzureSQL() {
  try {
    const table = document.getElementById('azure-insert-table').value;
    if (!table) return;
    
    const btn = document.getElementById('azure-insert-btn');
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Dodawanie...';
    
    
    const formDiv = document.getElementById('azure-insert-form');
    const inputs = formDiv.querySelectorAll('input, select, textarea');
    const data = {};
    
    inputs.forEach(input => {
      if (input.value) {
        data[input.id] = input.value;
      }
    });
    
    
    const response = await fetch(`/api/sql/${table}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    
    const result = await response.json();
    
    if (result.success) {
      alert(`✅ Pomyślnie dodano rekord do Azure SQL (ID: ${result.id})`);
      
      inputs.forEach(input => {
        if (input.type !== 'number' || input.id.includes('Id')) {
          input.value = '';
        }
      });
      
      setTimeout(() => checkAzureSQLTables(), 500);
    } else {
      alert(`❌ Błąd: ${result.message}`);
    }
    
  } catch (error) {
    console.error('Error inserting to Azure SQL:', error);
    alert('Błąd podczas dodawania: ' + error.message);
  } finally {
    const btn = document.getElementById('azure-insert-btn');
    btn.disabled = false;
    btn.innerHTML = '<i class="fas fa-plus-circle mr-2"></i>Dodaj do Azure SQL';
  }
}


function validateCosmosJSON() {
  try {
    const jsonText = document.getElementById('cosmos-insert-json').value;
    if (!jsonText.trim()) {
      alert('⚠️ Wprowadź dokument JSON');
      return false;
    }
    
    const parsed = JSON.parse(jsonText);
    alert('✅ JSON jest poprawny!');
    return true;
  } catch (error) {
    alert('❌ Błędny JSON: ' + error.message);
    return false;
  }
}


async function insertToCosmos() {
  try {
    const collection = document.getElementById('cosmos-insert-collection').value;
    const jsonText = document.getElementById('cosmos-insert-json').value;
    
    if (!collection) {
      alert('Wybierz kolekcję');
      return;
    }
    
    if (!jsonText.trim()) {
      alert('Wprowadź dokument JSON');
      return;
    }
    
    
    let data;
    try {
      data = JSON.parse(jsonText);
    } catch (error) {
      alert('Błędny JSON: ' + error.message);
      return;
    }
    
    const btn = document.getElementById('cosmos-insert-btn');
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Dodawanie...';
    
    
    const response = await fetch(`/api/mongo/${collection}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    
    const result = await response.json();
    
    if (result.success) {
      alert('✅ Pomyślnie dodano dokument do Cosmos DB');
      document.getElementById('cosmos-insert-json').value = '';
      setTimeout(() => checkCosmosDBStatus(), 500);
    } else {
      alert(`❌ Błąd: ${result.message}`);
    }
    
  } catch (error) {
    console.error('Error inserting to Cosmos DB:', error);
    alert('Błąd podczas dodawania: ' + error.message);
  } finally {
    const btn = document.getElementById('cosmos-insert-btn');
    btn.disabled = false;
    btn.innerHTML = '<i class="fas fa-plus-circle mr-2"></i>Dodaj do Cosmos DB';
  }
}


function loadCosmosTemplate(type) {
  const templates = {
    purchase: {
      collection: 'purchase',
      json: {
        "idKlienta": 1,
        "email": "customer@example.com",
        "idKraju": 1,
        "idZamWienia": 1001,
        "dataZamWienia": "2024-01-15",
        "rok": 2024,
        "kwarta": 1,
        "miesiC": 1,
        "kwotaCaKowita": 199.99,
        "status": "completed",
        "idSprzedawcy": 1,
        "nazwaSprzedawcy": "Jan Kowalski",
        "produkty": [
          {
            "idProduktu": 101,
            "nazwaProduktu": "Laptop Dell XPS 15",
            "kategoria": "Electronics",
            "ilosc": 1,
            "cenaJednostkowa": 199.99
          }
        ]
      }
    },
    behavior: {
      collection: 'behavior',
      json: {
        "idKlienta": 1,
        "email": "customer@example.com",
        "dataRejestracji": "2023-01-01",
        "ostatniaAktywnosc": "2024-01-15",
        "liczbaZamWien": 15,
        "caKowitaWartoscZakupWw": 2999.99,
        "sredniWartoscKoszyka": 199.99,
        "najczesciejKupowanaKategoria": "Electronics",
        "ulubionySprzedawca": "Jan Kowalski",
        "preferencjeDostawy": "express",
        "segmentKlienta": "premium"
      }
    },
    profiles: {
      collection: 'profiles',
      json: {
        "idSprzedawcy": 1,
        "nazwaSprzedawcy": "Jan Kowalski",
        "dataRejestracji": "2022-01-01",
        "status": "active",
        "ocenaSprzedawcy": 4.8,
        "liczbaOpinii": 250,
        "liczbaProdukWw": 50,
        "liczbaSprzedanychProduktWw": 1500,
        "caKowitaWartoscSprzedazy": 75000.00,
        "kategorieProdukWw": ["Electronics", "Home & Garden", "Sports"],
        "certyfikaty": ["Verified Seller", "Top Rated"],
        "ostatniaAktualizacja": "2024-01-15"
      }
    }
  };

  const template = templates[type];
  if (template) {
    document.getElementById('cosmos-insert-collection').value = template.collection;
    document.getElementById('cosmos-insert-json').value = JSON.stringify(template.json, null, 2);
  }
}
