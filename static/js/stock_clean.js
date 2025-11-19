// Enhanced Stock Management JavaScript - Clean Version
document.addEventListener('DOMContentLoaded', function() {
    console.log('✅ Stock Manager JavaScript loaded successfully!');
    
    const StockManager = {
        currentView: 'table',
        inventory: [],
        pendingOrders: [],
        suppliers: ['Pick N Pay', 'Checkers', 'Shoprite', 'Woolworths', 'Spar', 'Makro'],
        baseUrl: '/api/stock',
        
        async init() {
            console.log('🚀 Initializing Stock Manager...');
            try {
                this.bindEvents();
                await this.loadStockData();
                await this.loadPendingOrders();
                this.updateSummaryCards();
                this.initializeFilters();
                this.setupSelectAllCheckbox();
                this.setupRealTimeSearch();
                console.log('✅ Stock Manager initialized successfully');
            } catch (error) {
                console.error('❌ Failed to initialize Stock Manager:', error);
            }
        },

        async apiCall(endpoint, options = {}) {
            try {
                const url = `${this.baseUrl}${endpoint}`;
                const response = await fetch(url, {
                    headers: { 'Content-Type': 'application/json', ...options.headers },
                    ...options
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
                return await response.json();
            } catch (error) {
                console.error('API call failed:', error);
                this.showNotification(`API Error: ${error.message}`, 'error');
                throw error;
            }
        },

        async loadStockData() {
            try {
                const response = await this.apiCall('/items');
                if (response.success) {
                    this.inventory = response.items || response.data || [];
                } else {
                    this.loadFallbackData();
                }
            } catch (error) {
                console.error('Failed to load stock data:', error);
                this.loadFallbackData();
            }
            this.populateInventoryTable();
            this.updateFilteredResults();
        },

        loadFallbackData() {
            this.inventory = [
                { id: 1, name: 'Coffee Beans', sku: 'CB001', quantity: 3, unit: 'kg', location: 'Kitchen', status: 'Critical', supplier: 'Bean Co.', category: 'Food & Beverage', updated_at: new Date().toISOString() },
                { id: 2, name: 'Milk', sku: 'MK001', quantity: 10, unit: 'liters', location: 'Fridge', status: 'OK', supplier: 'Dairy Fresh', category: 'Food & Beverage', updated_at: new Date().toISOString() },
                { id: 3, name: 'Coffee Filters', sku: 'CF001', quantity: 25, unit: 'pieces', location: 'Store', status: 'OK', supplier: 'Office Plus', category: 'Office Supplies', updated_at: new Date().toISOString() },
                { id: 4, name: 'Printer Paper', sku: 'PP001', quantity: 2, unit: 'packs', location: 'Storage', status: 'Low', supplier: 'Paper World', category: 'Office Supplies', updated_at: new Date().toISOString() }
            ];
        },

        async loadPendingOrders() {
            try {
                const response = await this.apiCall('/orders?status=pending');
                if (response.success) {
                    this.pendingOrders = response.data || [];
                    this.displayPendingOrders();
                    this.updateOrderCount();
                }
            } catch (error) {
                console.error('Failed to load pending orders:', error);
                this.pendingOrders = [];
                this.displayPendingOrders();
            }
        },

        setupRealTimeSearch() {
            const searchInput = document.getElementById('searchFilter');
            if (searchInput) {
                let searchTimeout;
                searchInput.addEventListener('input', (e) => {
                    clearTimeout(searchTimeout);
                    searchTimeout = setTimeout(() => this.performSearch(e.target.value), 300);
                });
                searchInput.addEventListener('keydown', (e) => {
                    if (e.key === 'Escape') {
                        e.target.value = '';
                        this.performSearch('');
                    }
                });
            }
        },

        performSearch(query) {
            const filteredInventory = query.trim() 
                ? this.inventory.filter(item => 
                    item.name.toLowerCase().includes(query.toLowerCase()) ||
                    (item.sku && item.sku.toLowerCase().includes(query.toLowerCase())) ||
                    (item.supplier && item.supplier.toLowerCase().includes(query.toLowerCase())) ||
                    (item.location && item.location.toLowerCase().includes(query.toLowerCase()))
                )
                : this.inventory;

            this.populateInventoryTable(filteredInventory);
            this.updateFilteredResults(filteredInventory.length);
        },

        updateFilteredResults(count = null) {
            const resultCount = count !== null ? count : this.inventory.length;
            const headerText = document.querySelector('.inventory-section .section-header h3');
            if (headerText) {
                headerText.innerHTML = `<i class="fas fa-warehouse"></i> Current Inventory (${resultCount} items)`;
            }
        },

        displayPendingOrders() {
            const container = document.getElementById('pendingOrders');
            if (!container) return;

            if (this.pendingOrders.length === 0) {
                container.innerHTML = `
                    <div class="empty-state">
                        <i class="fas fa-inbox"></i>
                        <p>No pending orders</p>
                        <span>Your orders will appear here</span>
                    </div>
                `;
                return;
            }

            container.innerHTML = this.pendingOrders.map(order => `
                <div class="pending-order-card" data-order-id="${order.id}">
                    <div class="order-header">
                        <div class="order-info">
                            <h4>${order.item_name}</h4>
                            <span class="order-supplier">${order.supplier}</span>
                        </div>
                        <div class="order-priority priority-${order.priority}">
                            ${order.priority.toUpperCase()}
                        </div>
                    </div>
                    <div class="order-details">
                        <div class="order-quantity">
                            <strong>${order.quantity} ${order.unit}</strong>
                            ${order.weight_or_volume ? `<span class="weight-info">(${order.weight_or_volume} ${order.measurement_unit})</span>` : ''}
                        </div>
                        <div class="order-date">Ordered: ${new Date(order.created_at).toLocaleDateString()}</div>
                        ${order.expected_delivery ? `<div class="expected-delivery">Expected: ${new Date(order.expected_delivery).toLocaleDateString()}</div>` : ''}
                    </div>
                    <div class="order-actions">
                        <button class="btn btn-sm btn-success" onclick="StockManager.markOrderDelivered(${order.id})">
                            <i class="fas fa-check"></i> Mark Delivered
                        </button>
                        <button class="btn btn-sm btn-outline-secondary" onclick="StockManager.editOrder(${order.id})">
                            <i class="fas fa-edit"></i> Edit
                        </button>
                        <button class="btn btn-sm btn-outline-danger" onclick="StockManager.cancelOrder(${order.id})">
                            <i class="fas fa-times"></i> Cancel
                        </button>
                    </div>
                </div>
            `).join('');
        },

        updateOrderCount() {
            const summaryCard = document.querySelector('.summary-card.success .card-value');
            if (summaryCard) {
                summaryCard.textContent = this.pendingOrders.length;
            }
        },

        populateInventoryTable(data = null) {
            const tableBody = document.getElementById('inventoryTableBody');
            if (!tableBody) return;

            const inventoryData = data || this.inventory;

            if (inventoryData.length === 0) {
                tableBody.innerHTML = `
                    <tr>
                        <td colspan="8" class="text-center py-4">
                            <i class="fas fa-box-open fa-2x text-muted mb-2"></i>
                            <p class="text-muted">No stock items found</p>
                        </td>
                    </tr>
                `;
                return;
            }

            tableBody.innerHTML = inventoryData.map(item => `
                <tr data-item-id="${item.id}" data-status="${item.status}">
                    <td><input type="checkbox" class="item-checkbox" data-item-id="${item.id}"></td>
                    <td>
                        <div class="item-cell">
                            <div class="item-icon ${item.category?.toLowerCase() || 'default'}">
                                <i class="fas ${this.getItemIcon(item.category)}"></i>
                            </div>
                            <div class="item-info">
                                <span class="item-name">${item.name}</span>
                                <span class="item-sku">SKU: ${item.sku || 'N/A'}</span>
                            </div>
                        </div>
                    </td>
                    <td>
                        <div class="quantity-cell">
                            <span class="quantity-value">${item.quantity}</span>
                            <span class="quantity-unit">${item.unit}</span>
                        </div>
                    </td>
                    <td>
                        <span class="location-badge ${item.location?.toLowerCase() || 'unknown'}">
                            <i class="fas ${this.getLocationIcon(item.location)}"></i> ${item.location || 'Unknown'}
                        </span>
                    </td>
                    <td>
                        <span class="status-badge ${item.status?.toLowerCase() || 'unknown'}">
                            <i class="fas ${this.getStatusIcon(item.status)}"></i> ${item.status || 'Unknown'}
                        </span>
                    </td>
                    <td>
                        <div class="date-cell">
                            <span class="date-main">${new Date(item.updated_at || Date.now()).toLocaleDateString()}</span>
                            <span class="date-time">${new Date(item.updated_at || Date.now()).toLocaleTimeString()}</span>
                        </div>
                    </td>
                    <td>
                        <span class="supplier-link">${item.supplier || 'N/A'}</span>
                    </td>
                    <td>
                        <div class="action-buttons">
                            <button class="action-btn primary sm" onclick="StockManager.showOrderModal(${item.id})" title="Order">
                                <i class="fas fa-shopping-cart"></i>
                            </button>
                            <button class="action-btn secondary sm" onclick="StockManager.editItem(${item.id})" title="Edit">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="action-btn danger sm" onclick="StockManager.removeItem(${item.id})" title="Remove">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </td>
                </tr>
            `).join('');
        },

        getItemIcon(category) {
            const icons = { 'food & beverage': 'fa-coffee', 'office supplies': 'fa-file-alt', 'cleaning': 'fa-spray-can', 'equipment': 'fa-tools' };
            return icons[category?.toLowerCase()] || 'fa-box';
        },

        getLocationIcon(location) {
            const icons = { 'kitchen': 'fa-utensils', 'fridge': 'fa-snowflake', 'store': 'fa-store', 'storage': 'fa-archive' };
            return icons[location?.toLowerCase()] || 'fa-map-marker-alt';
        },

        getStatusIcon(status) {
            const icons = { 'ok': 'fa-check-circle', 'low': 'fa-exclamation-circle', 'critical': 'fa-exclamation-triangle' };
            return icons[status?.toLowerCase()] || 'fa-question-circle';
        },

        showOrderModal(itemId) {
            const item = this.inventory.find(i => i.id === itemId);
            if (!item) return;

            const modalHtml = `
                <div id="orderModal" class="modern-modal">
                    <div class="modal-overlay"></div>
                    <div class="modal-content">
                        <div class="modal-header">
                            <h3>Place Order - ${item.name}</h3>
                            <button class="modal-close" onclick="StockManager.closeOrderModal()">
                                <i class="fas fa-times"></i>
                            </button>
                        </div>
                        <div class="modal-body">
                            <form id="orderForm" class="modern-form">
                                <input type="hidden" id="orderItemId" value="${item.id}">
                                
                                <div class="form-row">
                                    <div class="form-group">
                                        <label for="orderQuantity">Quantity *</label>
                                        <input type="number" id="orderQuantity" min="1" step="0.01" required>
                                    </div>
                                    <div class="form-group">
                                        <label for="orderUnit">Unit *</label>
                                        <select id="orderUnit" required>
                                            <option value="">Select unit</option>
                                            <option value="kg">Kilograms (kg)</option>
                                            <option value="g">Grams (g)</option>
                                            <option value="liters">Liters (L)</option>
                                            <option value="ml">Milliliters (mL)</option>
                                            <option value="pieces">Pieces</option>
                                            <option value="packs">Packs</option>
                                            <option value="boxes">Boxes</option>
                                        </select>
                                    </div>
                                </div>

                                <div class="form-row weight-volume-section" style="display: none;">
                                    <div class="form-group">
                                        <label for="weightVolume">Weight/Volume</label>
                                        <input type="number" id="weightVolume" min="0" step="0.01" placeholder="Enter specific weight or volume">
                                    </div>
                                    <div class="form-group">
                                        <label for="measurementUnit">Measurement Unit</label>
                                        <select id="measurementUnit">
                                            <option value="">Select unit</option>
                                            <option value="g">Grams (g)</option>
                                            <option value="kg">Kilograms (kg)</option>
                                            <option value="ml">Milliliters (mL)</option>
                                            <option value="l">Liters (L)</option>
                                        </select>
                                    </div>
                                </div>

                                <div class="form-row">
                                    <div class="form-group">
                                        <label for="orderSupplier">Supplier (SA Retailer) *</label>
                                        <select id="orderSupplier" required>
                                            <option value="">Select supplier</option>
                                            ${this.suppliers.map(supplier => `<option value="${supplier}">${supplier}</option>`).join('')}
                                        </select>
                                    </div>
                                    <div class="form-group">
                                        <label for="orderPriority">Priority</label>
                                        <select id="orderPriority">
                                            <option value="normal">Normal</option>
                                            <option value="urgent">Urgent</option>
                                            <option value="critical">Critical</option>
                                        </select>
                                    </div>
                                </div>

                                <div class="form-row">
                                    <div class="form-group">
                                        <label for="expectedDelivery">Expected Delivery</label>
                                        <input type="date" id="expectedDelivery" min="${new Date().toISOString().split('T')[0]}">
                                    </div>
                                    <div class="form-group">
                                        <label for="totalCost">Total Cost (R)</label>
                                        <input type="number" id="totalCost" min="0" step="0.01" placeholder="0.00">
                                    </div>
                                </div>

                                <div class="form-group">
                                    <label for="orderNotes">Notes</label>
                                    <textarea id="orderNotes" rows="3" placeholder="Additional notes..."></textarea>
                                </div>

                                <div class="form-actions">
                                    <button type="button" class="action-btn secondary" onclick="StockManager.closeOrderModal()">Cancel</button>
                                    <button type="submit" class="action-btn primary">
                                        <i class="fas fa-shopping-cart"></i> Place Order
                                    </button>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            `;

            const existingModal = document.getElementById('orderModal');
            if (existingModal) existingModal.remove();

            document.body.insertAdjacentHTML('beforeend', modalHtml);

            const unitSelect = document.getElementById('orderUnit');
            const weightVolumeSection = document.querySelector('.weight-volume-section');
            
            unitSelect.addEventListener('change', (e) => {
                const selectedUnit = e.target.value;
                if (['kg', 'g', 'liters', 'ml'].includes(selectedUnit)) {
                    weightVolumeSection.style.display = 'flex';
                } else {
                    weightVolumeSection.style.display = 'none';
                }
            });

            document.getElementById('orderForm').addEventListener('submit', (e) => {
                e.preventDefault();
                this.submitOrder();
            });

            document.getElementById('orderModal').classList.add('show');
        },

        async submitOrder() {
            try {
                const orderData = {
                    item_id: parseInt(document.getElementById('orderItemId').value),
                    quantity: parseFloat(document.getElementById('orderQuantity').value),
                    unit: document.getElementById('orderUnit').value,
                    supplier: document.getElementById('orderSupplier').value,
                    priority: document.getElementById('orderPriority').value || 'normal',
                    expected_delivery: document.getElementById('expectedDelivery').value || null,
                    total_cost: parseFloat(document.getElementById('totalCost').value) || null,
                    notes: document.getElementById('orderNotes').value || null
                };

                const weightVolume = document.getElementById('weightVolume').value;
                const measurementUnit = document.getElementById('measurementUnit').value;
                
                if (weightVolume && measurementUnit) {
                    orderData.weight_or_volume = parseFloat(weightVolume);
                    orderData.measurement_unit = measurementUnit;
                }

                const response = await this.apiCall('/orders', {
                    method: 'POST',
                    body: JSON.stringify(orderData)
                });

                if (response.success) {
                    this.showNotification('Order placed successfully!', 'success');
                    this.closeOrderModal();
                    await this.loadPendingOrders();
                } else {
                    this.showNotification(`Failed to place order: ${response.error}`, 'error');
                }
            } catch (error) {
                this.showNotification(`Error placing order: ${error.message}`, 'error');
            }
        },

        closeOrderModal() {
            const modal = document.getElementById('orderModal');
            if (modal) modal.remove();
        },

        async markOrderDelivered(orderId) {
            try {
                const response = await this.apiCall(`/orders/${orderId}/deliver`, {
                    method: 'POST',
                    body: JSON.stringify({})
                });

                if (response.success) {
                    this.showNotification('Order marked as delivered and stock updated!', 'success');
                    await this.loadPendingOrders();
                    await this.loadStockData();
                } else {
                    this.showNotification(`Failed to mark order as delivered: ${response.error}`, 'error');
                }
            } catch (error) {
                this.showNotification(`Error: ${error.message}`, 'error');
            }
        },

        async cancelOrder(orderId) {
            if (!confirm('Are you sure you want to cancel this order?')) return;

            try {
                const reason = prompt('Reason for cancellation (optional):') || 'Cancelled by user';
                
                const response = await this.apiCall(`/orders/${orderId}`, {
                    method: 'DELETE',
                    body: JSON.stringify({ reason })
                });

                if (response.success) {
                    this.showNotification('Order cancelled successfully!', 'success');
                    await this.loadPendingOrders();
                } else {
                    this.showNotification(`Failed to cancel order: ${response.error}`, 'error');
                }
            } catch (error) {
                this.showNotification(`Error cancelling order: ${error.message}`, 'error');
            }
        },

        updateSummaryCards() {
            const lowStockCount = this.inventory.filter(item => item.status === 'Low' || item.status === 'Critical').length;
            
            const totalItemsEl = document.getElementById('totalItems');
            const lowStockEl = document.getElementById('lowStockItems');
            const pendingOrdersEl = document.getElementById('pendingOrders');
            
            if (totalItemsEl) totalItemsEl.textContent = this.inventory.length;
            if (lowStockEl) lowStockEl.textContent = lowStockCount;
            if (pendingOrdersEl) pendingOrdersEl.textContent = this.pendingOrders.length;
        },

        initializeFilters() {
            const statusFilter = document.getElementById('statusFilter');
            const locationFilter = document.getElementById('locationFilter');

            [statusFilter, locationFilter].forEach(filter => {
                if (filter) {
                    filter.addEventListener('change', () => this.applyFilters());
                }
            });
        },

        applyFilters() {
            const statusFilter = document.getElementById('statusFilter');
            const locationFilter = document.getElementById('locationFilter');
            const searchFilter = document.getElementById('searchFilter');
            
            const statusValue = statusFilter ? statusFilter.value : '';
            const locationValue = locationFilter ? locationFilter.value : '';
            const searchValue = searchFilter ? searchFilter.value : '';

            let filteredData = this.inventory;

            if (statusValue) {
                filteredData = filteredData.filter(item => item.status === statusValue);
            }

            if (locationValue) {
                filteredData = filteredData.filter(item => item.location === locationValue);
            }

            if (searchValue) {
                const query = searchValue.toLowerCase();
                filteredData = filteredData.filter(item => 
                    item.name.toLowerCase().includes(query) ||
                    (item.sku && item.sku.toLowerCase().includes(query)) ||
                    (item.supplier && item.supplier.toLowerCase().includes(query)) ||
                    (item.location && item.location.toLowerCase().includes(query))
                );
            }

            this.populateInventoryTable(filteredData);
            this.updateFilteredResults(filteredData.length);
        },

        setupSelectAllCheckbox() {
            const selectAllCheckbox = document.getElementById('selectAll');
            if (selectAllCheckbox) {
                selectAllCheckbox.addEventListener('change', (e) => {
                    const itemCheckboxes = document.querySelectorAll('.item-checkbox');
                    itemCheckboxes.forEach(checkbox => {
                        checkbox.checked = e.target.checked;
                    });
                });
            }
        },

        bindEvents() {
            const refreshBtn = document.getElementById('refreshBtn');
            if (refreshBtn) {
                refreshBtn.addEventListener('click', () => this.refreshData());
            }

            const addItemBtn = document.getElementById('addItemBtn');
            if (addItemBtn) {
                addItemBtn.addEventListener('click', () => this.showAddItemModal());
            }

            const exportBtn = document.getElementById('exportBtn');
            if (exportBtn) {
                exportBtn.addEventListener('click', () => this.exportData());
            }
        },

        async refreshData() {
            await this.loadStockData();
            await this.loadPendingOrders();
            this.updateSummaryCards();
            this.showNotification('Data refreshed successfully!', 'success');
        },

        showNotification(message, type = 'info') {
            const notification = document.createElement('div');
            notification.className = `notification notification-${type}`;
            notification.innerHTML = `
                <div class="notification-content">
                    <i class="fas ${type === 'success' ? 'fa-check-circle' : type === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle'}"></i>
                    <span>${message}</span>
                </div>
                <button class="notification-close">
                    <i class="fas fa-times"></i>
                </button>
            `;

            document.body.appendChild(notification);

            setTimeout(() => {
                if (notification.parentNode) {
                    notification.remove();
                }
            }, 5000);

            notification.querySelector('.notification-close').addEventListener('click', () => {
                notification.remove();
            });
        },

        // Placeholder methods
        async showAddItemModal() {
            this.showNotification('Add item feature coming soon!', 'info');
        },

        async editItem(itemId) {
            this.showNotification(`Edit item ${itemId} feature coming soon!`, 'info');
        },

        async removeItem(itemId) {
            if (!confirm('Are you sure you want to remove this item?')) return;
            this.showNotification(`Remove item ${itemId} feature coming soon!`, 'info');
        },

        async editOrder(orderId) {
            this.showNotification(`Edit order ${orderId} feature coming soon!`, 'info');
        },

        async exportData() {
            this.showNotification('Export feature coming soon!', 'info');
        }
    };

    // Initialize the system
    StockManager.init().catch(error => {
        console.error('Failed to initialize StockManager:', error);
    });

    // Make StockManager globally available
    window.StockManager = StockManager;
});