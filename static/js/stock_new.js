// Modern Stock Management JavaScript with API Integration
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Stock Management System
    const StockManager = {
        currentView: 'table',
        inventory: [],
        pendingOrders: [],
        baseUrl: '/api/stock',
        
        // Initialize the system
        async init() {
            this.bindEvents();
            await this.loadStockData();
            await this.loadStockAlerts();
            await this.loadOrderPartial();
            await this.updateSummaryCards();
            this.initializeFilters();
            this.setupSelectAllCheckbox();
        },

        // API helper method
        async apiCall(endpoint, options = {}) {
            try {
                const url = `${this.baseUrl}${endpoint}`;
                const response = await fetch(url, {
                    headers: {
                        'Content-Type': 'application/json',
                        ...options.headers
                    },
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

        // Load stock data from API
        async loadStockData() {
            try {
                const response = await this.apiCall('/items');
                if (response.success) {
                    this.inventory = response.items;
                    this.populateInventoryTable();
                    this.updateFilteredResults();
                } else {
                    console.error('Failed to load stock data:', response.error);
                }
            } catch (error) {
                console.error('Failed to load stock data:', error);
                // Continue with empty inventory if API fails
                this.inventory = [];
            }
        },

        // Populate inventory table with data
        populateInventoryTable() {
            const tbody = document.getElementById('inventoryTableBody');
            if (!tbody) return;

            tbody.innerHTML = '';

            this.inventory.forEach(item => {
                const row = this.createInventoryRow(item);
                tbody.appendChild(row);
            });
        },

        // Create table row for inventory item
        createInventoryRow(item) {
            const row = document.createElement('tr');
            row.setAttribute('data-item', item.name);
            row.setAttribute('data-qty', item.quantity);
            row.setAttribute('data-location', item.location);
            row.setAttribute('data-status', item.status);

            const statusClass = item.status.toLowerCase();
            const iconClass = this.getItemIcon(item.name);
            const locationClass = item.location.toLowerCase().replace(/\s+/g, '');

            row.innerHTML = `
                <td><input type="checkbox" class="item-checkbox" data-item="${item.name}" data-id="${item.id}"></td>
                <td>
                    <div class="item-cell">
                        <div class="item-icon ${item.name.toLowerCase().replace(/\s+/g, '')}">
                            <i class="${iconClass}"></i>
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
                        <span class="quantity-unit">${item.unit || ''}</span>
                    </div>
                </td>
                <td>
                    <span class="location-badge ${locationClass}">
                        <i class="fas fa-map-marker-alt"></i> ${item.location}
                    </span>
                </td>
                <td>
                    <span class="status-badge ${statusClass}">
                        <i class="fas ${this.getStatusIcon(item.status)}"></i> ${item.status}
                    </span>
                </td>
                <td>
                    <div class="date-cell">
                        <span class="date-main">${this.formatDate(item.last_updated)}</span>
                        <span class="date-time">${this.formatTime(item.last_updated)}</span>
                    </div>
                </td>
                <td>
                    <span class="supplier-link">${item.supplier || 'N/A'}</span>
                </td>
                <td>
                    <div class="action-buttons">
                        <button class="action-btn primary sm" onclick="StockManager.restockItem('${item.name}', ${item.id})" title="Restock">
                            <i class="fas fa-plus"></i>
                        </button>
                        <button class="action-btn secondary sm" onclick="StockManager.editItem('${item.name}', ${item.id})" title="Edit">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="action-btn danger sm" onclick="StockManager.removeItem('${item.name}', ${item.id})" title="Remove">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </td>
            `;

            return row;
        },

        // Get status icon
        getStatusIcon(status) {
            const icons = {
                'OK': 'fa-check-circle',
                'Low': 'fa-exclamation-circle',
                'Critical': 'fa-exclamation-triangle'
            };
            return icons[status] || 'fa-question-circle';
        },

        // Get appropriate icon for item type
        getItemIcon(item) {
            const icons = {
                'coffee': 'fas fa-coffee',
                'milk': 'fas fa-glass-whiskey',
                'filter': 'fas fa-filter',
                'paper': 'fas fa-file-alt',
                'default': 'fas fa-box'
            };

            const itemType = item.toLowerCase();
            for (const [key, icon] of Object.entries(icons)) {
                if (itemType.includes(key)) return icon;
            }
            return icons.default;
        },

        // Format date
        formatDate(dateString) {
            if (!dateString) return 'N/A';
            const date = new Date(dateString);
            return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
        },

        // Format time
        formatTime(dateString) {
            if (!dateString) return '';
            const date = new Date(dateString);
            return date.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
        },

        // Update summary cards with real data
        async updateSummaryCards() {
            try {
                const response = await this.apiCall('/summary');
                if (response.success) {
                    const summary = response.summary;
                    document.getElementById('totalItems').textContent = summary.total_items;
                    document.getElementById('lowStockItems').textContent = summary.low_stock_items + summary.critical_stock_items;
                    document.getElementById('pendingOrders').textContent = summary.pending_orders;
                    document.getElementById('totalLocations').textContent = summary.total_locations;
                }
            } catch (error) {
                console.error('Failed to update summary cards:', error);
                // Fall back to counting from current inventory
                this.updateSummaryFromInventory();
            }
        },

        // Fallback method to update summary from current inventory
        updateSummaryFromInventory() {
            const totalItems = this.inventory.length;
            const lowStockItems = this.inventory.filter(item => item.status === 'Low' || item.status === 'Critical').length;
            const locations = new Set(this.inventory.map(item => item.location)).size;

            document.getElementById('totalItems').textContent = totalItems;
            document.getElementById('lowStockItems').textContent = lowStockItems;
            document.getElementById('totalLocations').textContent = locations;
        },

        // Load and populate alerts section
        async loadStockAlerts() {
            try {
                const response = await this.apiCall('/alerts');
                if (response.success) {
                    this.populateAlertsSection(response.alerts);
                }
            } catch (error) {
                console.error('Failed to load stock alerts:', error);
            }
        },

        // Populate alerts section
        populateAlertsSection(alerts) {
            const alertsContainer = document.querySelector('.alerts-container');
            const alertCount = document.querySelector('.alert-count');
            
            if (!alertsContainer || !alertCount) return;

            alertCount.textContent = `${alerts.length} items need attention`;
            alertsContainer.innerHTML = '';

            alerts.forEach(alert => {
                const alertCard = document.createElement('div');
                alertCard.className = `alert-card ${alert.type === 'critical' ? 'urgent' : 'warning'}`;
                alertCard.setAttribute('data-item', alert.item);

                alertCard.innerHTML = `
                    <div class="alert-content">
                        <div class="alert-item">
                            <i class="${this.getItemIcon(alert.item)}"></i>
                            <span class="item-name">${alert.item}</span>
                        </div>
                        <div class="alert-status">
                            <span class="status-badge ${alert.type}">
                                ${alert.type === 'critical' ? 'Critical' : 'Low'} - ${alert.current_quantity} ${alert.unit} left
                            </span>
                            <span class="recommendation">Recommended: Order ${alert.recommended_order} ${alert.unit}</span>
                        </div>
                    </div>
                    <button class="alert-action-btn" onclick="StockManager.quickOrderFromAlert('${alert.item}', ${alert.recommended_order}, ${alert.id})">
                        <i class="fas fa-shopping-cart"></i> Order Now
                    </button>
                `;

                alertsContainer.appendChild(alertCard);
            });
        },

        // Bind all event listeners
        bindEvents() {
            // Header actions
            document.getElementById('addItemBtn')?.addEventListener('click', () => this.openItemModal());
            document.getElementById('exportBtn')?.addEventListener('click', () => this.exportData());
            document.getElementById('refreshBtn')?.addEventListener('click', () => this.refreshData());

            // View toggle
            document.querySelectorAll('.toggle-btn').forEach(btn => {
                btn.addEventListener('click', (e) => this.switchView(e.target.dataset.view));
            });

            // Filters
            document.getElementById('statusFilter')?.addEventListener('change', () => this.applyFilters());
            document.getElementById('locationFilter')?.addEventListener('change', () => this.applyFilters());
            document.getElementById('searchFilter')?.addEventListener('input', () => this.debounceFilter());

            // Modal events
            this.bindModalEvents();

            // Bulk actions
            document.getElementById('bulkActionsBtn')?.addEventListener('click', () => this.showBulkActions());
        },

        // API Methods for stock operations
        async restockItemAPI(itemId, quantity, reference = 'Manual restock', notes = '') {
            try {
                const response = await this.apiCall(`/items/${itemId}/restock`, {
                    method: 'POST',
                    body: JSON.stringify({
                        quantity: quantity,
                        reference: reference,
                        notes: notes
                    })
                });

                if (response.success) {
                    this.showNotification(response.message, 'success');
                    await this.loadStockData();
                    await this.updateSummaryCards();
                    return true;
                }
                return false;
            } catch (error) {
                console.error('Restock failed:', error);
                return false;
            }
        },

        async createItemAPI(itemData) {
            try {
                const response = await this.apiCall('/items', {
                    method: 'POST',
                    body: JSON.stringify(itemData)
                });

                if (response.success) {
                    this.showNotification('Item created successfully!', 'success');
                    await this.loadStockData();
                    await this.updateSummaryCards();
                    return response.item;
                }
                return null;
            } catch (error) {
                console.error('Item creation failed:', error);
                return null;
            }
        },

        async updateItemAPI(itemId, itemData) {
            try {
                const response = await this.apiCall(`/items/${itemId}`, {
                    method: 'PUT',
                    body: JSON.stringify(itemData)
                });

                if (response.success) {
                    this.showNotification('Item updated successfully!', 'success');
                    await this.loadStockData();
                    await this.updateSummaryCards();
                    return true;
                }
                return false;
            } catch (error) {
                console.error('Item update failed:', error);
                return false;
            }
        },

        async deleteItemAPI(itemId) {
            try {
                const response = await this.apiCall(`/items/${itemId}`, {
                    method: 'DELETE'
                });

                if (response.success) {
                    this.showNotification('Item deleted successfully!', 'success');
                    await this.loadStockData();
                    await this.updateSummaryCards();
                    return true;
                }
                return false;
            } catch (error) {
                console.error('Item deletion failed:', error);
                return false;
            }
        },

        async bulkOperationAPI(operation, itemIds, data = {}) {
            try {
                const response = await this.apiCall('/items/bulk-update', {
                    method: 'POST',
                    body: JSON.stringify({
                        operation: operation,
                        item_ids: itemIds,
                        ...data
                    })
                });

                if (response.success) {
                    this.showNotification(response.message, 'success');
                    await this.loadStockData();
                    await this.updateSummaryCards();
                    return response.updated_items;
                }
                return null;
            } catch (error) {
                console.error('Bulk operation failed:', error);
                return null;
            }
        },

        async createOrderAPI(orderData) {
            try {
                const response = await this.apiCall('/orders', {
                    method: 'POST',
                    body: JSON.stringify(orderData)
                });

                if (response.success) {
                    this.showNotification(response.message, 'success');
                    return response.order_id;
                }
                return null;
            } catch (error) {
                console.error('Order creation failed:', error);
                return null;
            }
        },

        // Debounced filter for search input
        debounceFilter() {
            clearTimeout(this.filterTimeout);
            this.filterTimeout = setTimeout(() => this.applyFilters(), 300);
        },

        // Apply all filters
        applyFilters() {
            const status = document.getElementById('statusFilter')?.value || '';
            const location = document.getElementById('locationFilter')?.value || '';
            const search = document.getElementById('searchFilter')?.value.toLowerCase() || '';

            const rows = document.querySelectorAll('#inventoryTableBody tr');
            let visibleCount = 0;

            rows.forEach(row => {
                const itemStatus = row.dataset.status || '';
                const itemLocation = row.dataset.location || '';
                const itemName = row.querySelector('.item-name')?.textContent.toLowerCase() || '';
                
                const matchesStatus = !status || itemStatus === status;
                const matchesLocation = !location || itemLocation === location;
                const matchesSearch = !search || itemName.includes(search);

                if (matchesStatus && matchesLocation && matchesSearch) {
                    row.style.display = '';
                    visibleCount++;
                } else {
                    row.style.display = 'none';
                }
            });

            this.updateFilterResults(visibleCount);
        },

        // Update filter results count
        updateFilterResults(count) {
            const existingCount = document.querySelector('.filter-results');
            if (existingCount) existingCount.remove();

            if (count < document.querySelectorAll('#inventoryTableBody tr').length) {
                const countElement = document.createElement('span');
                countElement.className = 'filter-results';
                countElement.style.cssText = 'margin-left: 1rem; color: var(--stock-gray-600); font-size: 0.875rem;';
                countElement.textContent = `Showing ${count} items`;
                document.querySelector('.section-header h3').appendChild(countElement);
            }
        },

        // Initialize filter dropdowns with data from inventory
        initializeFilters() {
            const statusFilter = document.getElementById('statusFilter');
            const locationFilter = document.getElementById('locationFilter');

            if (this.inventory.length > 0) {
                // Populate location filter
                const locations = [...new Set(this.inventory.map(item => item.location))];
                locations.forEach(location => {
                    if (location && !Array.from(locationFilter.options).some(opt => opt.value === location)) {
                        const option = document.createElement('option');
                        option.value = location;
                        option.textContent = location;
                        locationFilter.appendChild(option);
                    }
                });
            }
        },

        // Switch between table and grid view
        switchView(view) {
            this.currentView = view;
            
            document.querySelectorAll('.toggle-btn').forEach(btn => {
                btn.classList.toggle('active', btn.dataset.view === view);
            });

            const tableView = document.getElementById('tableView');
            const gridView = document.getElementById('gridView');

            if (view === 'table') {
                tableView?.classList.remove('hidden');
                gridView?.classList.add('hidden');
            } else {
                tableView?.classList.add('hidden');
                gridView?.classList.remove('hidden');
                this.populateGridView();
            }
        },

        // Populate grid view
        populateGridView() {
            const gridContainer = document.querySelector('.inventory-grid');
            if (!gridContainer) return;

            const visibleRows = Array.from(document.querySelectorAll('#inventoryTableBody tr')).filter(row => 
                row.style.display !== 'none'
            );
            
            let gridHTML = '';

            visibleRows.forEach(row => {
                const item = row.dataset.item;
                const qty = row.dataset.qty;
                const location = row.dataset.location;
                const status = row.dataset.status;
                const icon = this.getItemIcon(item);

                gridHTML += `
                    <div class="grid-item ${status.toLowerCase()}" data-item="${item}">
                        <div class="grid-item-header">
                            <div class="item-icon ${item.toLowerCase().replace(/\s+/g, '')}">
                                <i class="${icon}"></i>
                            </div>
                            <span class="status-badge ${status.toLowerCase()}">${status}</span>
                        </div>
                        <div class="grid-item-content">
                            <h4>${item}</h4>
                            <p class="quantity">${qty} units</p>
                            <p class="location">📍 ${location}</p>
                        </div>
                        <div class="grid-item-actions">
                            <button class="action-btn primary sm" onclick="StockManager.restockItem('${item}')">
                                <i class="fas fa-plus"></i> Restock
                            </button>
                            <button class="action-btn secondary sm" onclick="StockManager.editItem('${item}')">
                                <i class="fas fa-edit"></i>
                            </button>
                        </div>
                    </div>
                `;
            });

            gridContainer.innerHTML = gridHTML;
        },

        // Setup select all checkbox functionality
        setupSelectAllCheckbox() {
            const selectAll = document.getElementById('selectAll');
            
            selectAll?.addEventListener('change', (e) => {
                const itemCheckboxes = document.querySelectorAll('.item-checkbox');
                itemCheckboxes.forEach(checkbox => {
                    if (!checkbox.closest('tr').style.display || checkbox.closest('tr').style.display !== 'none') {
                        checkbox.checked = e.target.checked;
                    }
                });
                this.updateBulkActionsVisibility();
            });

            // Update select all when individual checkboxes change
            document.addEventListener('change', (e) => {
                if (e.target.classList.contains('item-checkbox')) {
                    const itemCheckboxes = document.querySelectorAll('.item-checkbox');
                    const visibleCheckboxes = Array.from(itemCheckboxes).filter(cb => 
                        !cb.closest('tr').style.display || cb.closest('tr').style.display !== 'none'
                    );
                    const checkedVisible = visibleCheckboxes.filter(cb => cb.checked);
                    
                    selectAll.indeterminate = checkedVisible.length > 0 && checkedVisible.length < visibleCheckboxes.length;
                    selectAll.checked = checkedVisible.length === visibleCheckboxes.length && visibleCheckboxes.length > 0;
                    
                    this.updateBulkActionsVisibility();
                }
            });
        },

        // Update bulk actions button visibility
        updateBulkActionsVisibility() {
            const checkedItems = document.querySelectorAll('.item-checkbox:checked');
            const bulkBtn = document.getElementById('bulkActionsBtn');
            
            if (checkedItems.length > 0) {
                bulkBtn?.classList.add('active');
                bulkBtn.innerHTML = `<i class="fas fa-tasks"></i> Bulk Actions (${checkedItems.length})`;
            } else {
                bulkBtn?.classList.remove('active');
                bulkBtn.innerHTML = '<i class="fas fa-tasks"></i> Bulk Actions';
            }
        },

        // Show bulk actions menu
        showBulkActions() {
            const checkedItems = Array.from(document.querySelectorAll('.item-checkbox:checked'));
            if (checkedItems.length === 0) {
                this.showNotification('Please select items for bulk actions', 'warning');
                return;
            }

            const itemIds = checkedItems.map(cb => parseInt(cb.dataset.id)).filter(id => !isNaN(id));
            const itemNames = checkedItems.map(cb => cb.dataset.item);
            
            const actions = [
                { 
                    label: 'Restock Selected', 
                    action: () => this.bulkRestock(itemIds, itemNames) 
                },
                { 
                    label: 'Update Location', 
                    action: () => this.bulkUpdateLocation(itemIds, itemNames) 
                },
                { 
                    label: 'Export Selected', 
                    action: () => this.exportSelected(itemNames) 
                },
                { 
                    label: 'Delete Selected', 
                    action: () => this.bulkDelete(itemIds, itemNames), 
                    danger: true 
                }
            ];

            this.showContextMenu(actions);
        },

        // Show context menu
        showContextMenu(actions) {
            const existingMenu = document.querySelector('.context-menu');
            if (existingMenu) existingMenu.remove();

            const menu = document.createElement('div');
            menu.className = 'context-menu';
            menu.style.cssText = `
                position: fixed;
                background: white;
                border-radius: 8px;
                box-shadow: 0 10px 25px rgba(0,0,0,0.15);
                z-index: 1000;
                padding: 0.5rem 0;
                min-width: 200px;
            `;

            actions.forEach(action => {
                const item = document.createElement('button');
                item.textContent = action.label;
                item.className = `context-menu-item ${action.danger ? 'danger' : ''}`;
                item.style.cssText = `
                    width: 100%;
                    padding: 0.75rem 1rem;
                    border: none;
                    background: none;
                    text-align: left;
                    cursor: pointer;
                    transition: background-color 0.2s ease;
                    ${action.danger ? 'color: var(--stock-danger);' : ''}
                `;
                item.addEventListener('click', () => {
                    action.action();
                    menu.remove();
                });
                item.addEventListener('mouseenter', () => {
                    item.style.backgroundColor = action.danger ? 'rgba(220, 38, 38, 0.1)' : 'var(--stock-gray-50)';
                });
                item.addEventListener('mouseleave', () => {
                    item.style.backgroundColor = 'transparent';
                });
                menu.appendChild(item);
            });

            document.body.appendChild(menu);
            
            // Position menu near the bulk actions button
            const bulkBtn = document.getElementById('bulkActionsBtn');
            const rect = bulkBtn.getBoundingClientRect();
            menu.style.top = `${rect.bottom + 5}px`;
            menu.style.left = `${rect.left}px`;

            // Close menu when clicking outside
            const closeMenu = (e) => {
                if (!menu.contains(e.target)) {
                    menu.remove();
                    document.removeEventListener('click', closeMenu);
                }
            };
            setTimeout(() => document.addEventListener('click', closeMenu), 100);
        },

        // Bulk restock
        async bulkRestock(itemIds, itemNames) {
            const quantity = prompt('Enter quantity to add to all selected items:', '10');
            if (quantity && !isNaN(quantity) && parseInt(quantity) > 0) {
                const result = await this.bulkOperationAPI('restock', itemIds, { quantity: parseInt(quantity) });
                if (result) {
                    this.showNotification(`Restocked ${result.length} items`, 'success');
                }
            }
        },

        // Bulk update location
        async bulkUpdateLocation(itemIds, itemNames) {
            const location = prompt('Enter new location for selected items:', 'Storage');
            if (location && location.trim()) {
                const result = await this.bulkOperationAPI('update_location', itemIds, { location: location.trim() });
                if (result) {
                    this.showNotification(`Updated location for ${result.length} items`, 'success');
                }
            }
        },

        // Export selected items
        exportSelected(itemNames) {
            const selectedData = this.inventory.filter(item => itemNames.includes(item.name));
            
            const csvContent = "data:text/csv;charset=utf-8," 
                + "Item,Quantity,Location,Status,Supplier\n"
                + selectedData.map(item => `${item.name},${item.quantity},${item.location},${item.status},${item.supplier || ''}`).join('\n');

            const link = document.createElement('a');
            link.href = encodeURI(csvContent);
            link.download = `selected_stock_${new Date().toISOString().split('T')[0]}.csv`;
            link.click();

            this.showNotification('Selected items exported successfully!', 'success');
        },

        // Bulk delete
        async bulkDelete(itemIds, itemNames) {
            if (confirm(`Are you sure you want to delete ${itemNames.length} selected items? This action cannot be undone.`)) {
                const result = await this.bulkOperationAPI('delete', itemIds);
                if (result) {
                    this.showNotification(`Deleted ${result.length} items`, 'success');
                }
            }
        },

        // Modal event bindings
        bindModalEvents() {
            // Detail modal
            document.getElementById('modalClose')?.addEventListener('click', () => this.closeModal('detailModal'));

            // Item modal
            document.getElementById('itemModalClose')?.addEventListener('click', () => this.closeModal('itemModal'));
            document.getElementById('cancelItemBtn')?.addEventListener('click', () => this.closeModal('itemModal'));
            document.getElementById('itemForm')?.addEventListener('submit', (e) => this.handleItemSubmit(e));

            // Quick order modal
            document.getElementById('quickOrderClose')?.addEventListener('click', () => this.closeModal('quickOrderModal'));
            document.getElementById('quickOrderForm')?.addEventListener('submit', (e) => this.handleQuickOrder(e));

            // Close modals when clicking overlay
            document.querySelectorAll('.modal-overlay').forEach(overlay => {
                overlay.addEventListener('click', (e) => {
                    const modal = e.target.closest('.modern-modal');
                    if (modal) this.closeModal(modal.id);
                });
            });
        },

        // Open item modal for add/edit
        openItemModal(itemId = null) {
            const modal = document.getElementById('itemModal');
            const title = document.getElementById('itemModalTitle');
            const form = document.getElementById('itemForm');

            if (itemId) {
                title.textContent = 'Edit Item';
                this.populateItemForm(itemId);
            } else {
                title.textContent = 'Add New Item';
                form.reset();
            }

            this.showModal('itemModal');
        },

        // Populate item form with existing data
        populateItemForm(itemId) {
            const item = this.inventory.find(i => i.id === itemId);
            if (!item) return;

            document.getElementById('itemName').value = item.name;
            document.getElementById('itemSku').value = item.sku || '';
            document.getElementById('itemQuantity').value = item.quantity;
            document.getElementById('itemUnit').value = item.unit || '';
            document.getElementById('itemLocation').value = item.location;
            document.getElementById('itemSupplier').value = item.supplier || '';
            document.getElementById('itemThreshold').value = item.reorder_point || '';
            document.getElementById('itemCategory').value = item.category || '';
        },

        // Handle item form submission
        async handleItemSubmit(e) {
            e.preventDefault();
            
            const formData = new FormData(e.target);
            const itemData = Object.fromEntries(formData.entries());
            
            // Add loading state
            const submitBtn = e.target.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Saving...';
            submitBtn.disabled = true;

            try {
                const title = document.getElementById('itemModalTitle').textContent;
                let success = false;

                if (title === 'Add New Item') {
                    success = await this.createItemAPI(itemData);
                } else {
                    // For edit, we need to get the item ID
                    const itemName = document.getElementById('itemName').value;
                    const item = this.inventory.find(i => i.name === itemName);
                    if (item) {
                        success = await this.updateItemAPI(item.id, itemData);
                    }
                }

                if (success) {
                    this.closeModal('itemModal');
                }
            } finally {
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
            }
        },

        // Handle quick order
        async handleQuickOrder(e) {
            e.preventDefault();
            
            const item = document.getElementById('quickOrderItem').value;
            const quantity = document.getElementById('quickOrderQuantity').value;
            const supplier = document.getElementById('quickOrderSupplier').value;
            const priority = document.getElementById('quickOrderPriority').value;

            const orderData = { 
                supplier, 
                items: [{ name: item, quantity: parseInt(quantity) }], 
                priority 
            };
            
            const orderId = await this.createOrderAPI(orderData);
            if (orderId) {
                this.addPendingOrder({ ...orderData, id: orderId });
                this.closeModal('quickOrderModal');
            }
        },

        // Show modal
        showModal(modalId) {
            const modal = document.getElementById(modalId);
            if (modal) {
                modal.style.display = 'block';
                document.body.style.overflow = 'hidden';
                // Focus first input
                const firstInput = modal.querySelector('input, select, textarea');
                if (firstInput) {
                    setTimeout(() => firstInput.focus(), 100);
                }
            }
        },

        // Close modal
        closeModal(modalId) {
            const modal = document.getElementById(modalId);
            if (modal) {
                modal.style.display = 'none';
                document.body.style.overflow = '';
            }
        },

        // Load order partial (keeping existing functionality)
        loadOrderPartial() {
            const container = document.getElementById('orderPartialContainer');
            if (!container) return;

            // Create a simple order form since the partial might not exist
            container.innerHTML = `
                <div class="order-form">
                    <h4>Create Order</h4>
                    <div class="form-group">
                        <label for="orderSupplier">Supplier</label>
                        <select id="orderSupplier" class="form-control">
                            <option value="">Select supplier</option>
                            <option value="Pick N Pay">Pick N Pay</option>
                            <option value="Checkers">Checkers</option>
                            <option value="Shoprite">Shoprite</option>
                            <option value="Woolworths">Woolworths</option>
                            <option value="Spar">Spar</option>
                            <option value="Makro">Makro</option>
                        </select>
                    </div>
                    <div id="orderItems">
                        <div class="order-item-row" style="display: flex; gap: 8px; margin-bottom: 6px; align-items: center;">
                            <input class="form-control item-name" placeholder="Item name" style="flex:2;padding:8px;border:1px solid #ddd;border-radius:4px;">
                            <input class="form-control item-qty" type="number" min="1" value="1" style="width:80px;padding:8px;border:1px solid #ddd;border-radius:4px;">
                        </div>
                    </div>
                    <button id="addOrderItem" type="button" class="action-btn secondary" style="margin-bottom: 10px;">
                        <i class="fas fa-plus"></i> Add Item
                    </button>
                    <button id="submitExternalOrder" type="button" class="action-btn primary">
                        <i class="fas fa-shopping-cart"></i> Place Order
                    </button>
                </div>
            `;
            
            this.initOrderPartial();
        },

        // Initialize order partial functionality
        initOrderPartial() {
            const addBtn = document.getElementById('addOrderItem');
            const itemsContainer = document.getElementById('orderItems');
            const supplierEl = document.getElementById('orderSupplier');
            const submitBtn = document.getElementById('submitExternalOrder');

            if (!addBtn || !itemsContainer || !supplierEl || !submitBtn) return;

            addBtn.addEventListener('click', () => {
                const newRow = document.createElement('div');
                newRow.className = 'order-item-row';
                newRow.style.cssText = 'display: flex; gap: 8px; margin-bottom: 6px; align-items: center;';
                newRow.innerHTML = `
                    <input class="form-control item-name" placeholder="Item name" style="flex:2;padding:8px;border:1px solid #ddd;border-radius:4px;">
                    <input class="form-control item-qty" type="number" min="1" value="1" style="width:80px;padding:8px;border:1px solid #ddd;border-radius:4px;">
                    <button class="action-btn danger sm remove-item-row" type="button">
                        <i class="fas fa-trash"></i>
                    </button>
                `;
                itemsContainer.appendChild(newRow);
                
                // Add remove functionality
                newRow.querySelector('.remove-item-row').addEventListener('click', () => {
                    newRow.remove();
                });
            });

            submitBtn.addEventListener('click', () => this.handleExternalOrder(supplierEl, itemsContainer, submitBtn));
        },

        // Handle external order submission
        async handleExternalOrder(supplierEl, itemsContainer, submitBtn) {
            const supplier = supplierEl.value;
            if (!supplier) {
                this.showNotification('Please select a supplier', 'error');
                supplierEl.focus();
                return;
            }

            const rows = itemsContainer.querySelectorAll('.order-item-row');
            const items = [];
            
            rows.forEach(row => {
                const name = row.querySelector('.item-name')?.value?.trim();
                const qty = parseInt(row.querySelector('.item-qty')?.value || '0', 10);
                if (name && qty > 0) {
                    items.push({ name, quantity: qty });
                }
            });

            if (items.length === 0) {
                this.showNotification('Add at least one item', 'error');
                return;
            }

            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Placing...';

            try {
                const orderData = { supplier, items, priority: 'normal' };
                const orderId = await this.createOrderAPI(orderData);
                
                if (orderId) {
                    this.addPendingOrder({ ...orderData, id: orderId });
                    
                    // Reset form
                    supplierEl.value = '';
                    itemsContainer.querySelectorAll('.order-item-row').forEach((row, index) => {
                        if (index > 0) row.remove();
                        else {
                            row.querySelector('.item-name').value = '';
                            row.querySelector('.item-qty').value = '1';
                        }
                    });
                }
            } finally {
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<i class="fas fa-shopping-cart"></i> Place Order';
            }
        },

        // Add pending order to the list
        addPendingOrder(orderData) {
            const container = document.getElementById('pendingOrders');
            const emptyState = container.querySelector('.empty-state');
            if (emptyState) emptyState.style.display = 'none';

            const orderElement = document.createElement('div');
            orderElement.className = 'pending-order-item';
            orderElement.id = `order-${orderData.id}`;
            orderElement.style.cssText = `
                background: var(--stock-gray-50);
                border: 1px solid var(--stock-gray-200);
                border-radius: 8px;
                padding: 1rem;
                margin-bottom: 1rem;
                transition: all 0.2s ease;
            `;

            const itemsList = orderData.items.map(item => `${item.quantity}x ${item.name}`).join(', ');
            
            orderElement.innerHTML = `
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="font-weight: 600; margin-bottom: 0.25rem;">
                            Order #${orderData.id}
                        </div>
                        <div style="color: #666; font-size: 0.875rem;">
                            ${orderData.supplier} • ${itemsList}
                        </div>
                        <div style="margin-top: 0.5rem;">
                            <span class="status-badge" style="background: rgba(245, 158, 11, 0.1); color: #f59e0b;">
                                <i class="fas fa-clock"></i> Pending
                            </span>
                        </div>
                    </div>
                    <button class="action-btn danger sm" onclick="StockManager.cancelOrder('${orderData.id}')" title="Cancel Order">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            `;

            container.appendChild(orderElement);
            this.updateSummaryCards();
        },

        // Cancel order
        cancelOrder(orderId) {
            if (!confirm('Are you sure you want to cancel this order?')) return;

            const orderElement = document.getElementById(`order-${orderId}`);
            if (orderElement) {
                orderElement.style.animation = 'fadeOut 0.3s ease-out';
                setTimeout(() => {
                    orderElement.remove();
                    this.updateSummaryCards();
                    
                    // Show empty state if no orders left
                    const container = document.getElementById('pendingOrders');
                    if (!container.querySelector('.pending-order-item')) {
                        const emptyState = container.querySelector('.empty-state');
                        if (emptyState) emptyState.style.display = 'block';
                    }
                }, 300);
            }
        },

        // Refresh data
        async refreshData() {
            const refreshBtn = document.getElementById('refreshBtn');
            const icon = refreshBtn.querySelector('i');
            
            icon.classList.add('fa-spin');
            refreshBtn.disabled = true;

            try {
                await this.loadStockData();
                await this.loadStockAlerts();
                await this.updateSummaryCards();
                this.showNotification('Data refreshed!', 'success');
            } catch (error) {
                this.showNotification('Failed to refresh data', 'error');
            } finally {
                icon.classList.remove('fa-spin');
                refreshBtn.disabled = false;
            }
        },

        // Export data
        async exportData() {
            try {
                const response = await this.apiCall('/export');
                if (response.success) {
                    const link = document.createElement('a');
                    const blob = new Blob([response.data], { type: 'text/csv' });
                    link.href = URL.createObjectURL(blob);
                    link.download = response.filename;
                    link.click();
                    this.showNotification('Data exported successfully!', 'success');
                }
            } catch (error) {
                // Fallback to client-side export
                this.exportDataFallback();
            }
        },

        // Fallback export method
        exportDataFallback() {
            const csvContent = "data:text/csv;charset=utf-8," 
                + "Item,Quantity,Location,Status,Supplier\n"
                + this.inventory.map(item => `${item.name},${item.quantity},${item.location},${item.status},${item.supplier || ''}`).join('\n');

            const link = document.createElement('a');
            link.href = encodeURI(csvContent);
            link.download = `stock_inventory_${new Date().toISOString().split('T')[0]}.csv`;
            link.click();

            this.showNotification('Data exported successfully!', 'success');
        },

        // Show notification
        showNotification(message, type = 'info') {
            // Remove existing notification
            const existing = document.querySelector('.notification');
            if (existing) existing.remove();

            const notification = document.createElement('div');
            notification.className = `notification ${type}`;
            notification.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 1rem 1.5rem;
                border-radius: 8px;
                color: white;
                font-weight: 500;
                z-index: 1000;
                transform: translateX(100%);
                transition: transform 0.3s ease;
                max-width: 400px;
            `;

            const colors = {
                success: '#10b981',
                error: '#ef4444',
                warning: '#f59e0b',
                info: '#3b82f6'
            };

            notification.style.background = colors[type] || colors.info;
            notification.textContent = message;

            document.body.appendChild(notification);

            // Animate in
            setTimeout(() => {
                notification.style.transform = 'translateX(0)';
            }, 100);

            // Auto remove
            setTimeout(() => {
                notification.style.transform = 'translateX(100%)';
                setTimeout(() => notification.remove(), 300);
            }, 3000);
        }
    };

    // Global functions for inline event handlers
    window.quickOrder = (item, recommendedQty) => {
        document.getElementById('quickOrderItem').value = item;
        document.getElementById('quickOrderQuantity').value = recommendedQty;
        StockManager.showModal('quickOrderModal');
    };

    window.quickOrderFromAlert = (item, recommendedQty, itemId) => {
        document.getElementById('quickOrderItem').value = item;
        document.getElementById('quickOrderQuantity').value = recommendedQty;
        StockManager.showModal('quickOrderModal');
    };

    window.restockItem = async (item, itemId) => {
        const quantity = prompt(`Restock ${item}. Enter quantity to add:`, '10');
        if (quantity && !isNaN(quantity) && parseInt(quantity) > 0) {
            if (itemId) {
                await StockManager.restockItemAPI(itemId, parseInt(quantity));
            } else {
                StockManager.showNotification(`Added ${quantity} units to ${item}`, 'success');
            }
        }
    };

    window.editItem = (item, itemId) => {
        StockManager.openItemModal(itemId);
    };

    window.removeItem = async (item, itemId) => {
        if (confirm(`Are you sure you want to remove ${item} from inventory?`)) {
            if (itemId) {
                await StockManager.deleteItemAPI(itemId);
            } else {
                // Fallback for items without ID
                const row = document.querySelector(`tr[data-item="${item}"]`);
                if (row) {
                    row.style.animation = 'fadeOut 0.3s ease-out';
                    setTimeout(() => {
                        row.remove();
                        StockManager.updateSummaryCards();
                        StockManager.showNotification(`${item} removed from inventory`, 'success');
                    }, 300);
                }
            }
        }
    };

    // Make StockManager globally available
    window.StockManager = StockManager;

    // Initialize the system
    StockManager.init();

    // Add fadeOut animation CSS if not already present
    if (!document.querySelector('#fadeOutStyle')) {
        const style = document.createElement('style');
        style.id = 'fadeOutStyle';
        style.textContent = `
            @keyframes fadeOut {
                from { opacity: 1; transform: translateX(0); }
                to { opacity: 0; transform: translateX(20px); }
            }
            .fa-spin {
                animation: fa-spin 1s infinite linear;
            }
            @keyframes fa-spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        `;
        document.head.appendChild(style);
    }
});