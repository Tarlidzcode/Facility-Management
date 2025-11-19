// presence.js - Enhanced Presence Tracking with Interactivity
// MRI Corporate Colors: Primary #16636a (teal), Secondary colors for variety

class PresenceTracker {
    constructor() {
        this.API_ENDPOINTS = {
            OCCUPANTS: '/api/safety/occupants',
            VISITORS: '/api/safety/visitors',
            EMERGENCY: '/api/safety/emergency'
        };
        
        this.isEmergencyMode = false;
        this.employees = [];
        this.visitors = [];
        this.refreshInterval = null;
        this.searchTerm = '';
        this.filterStatus = 'all'; // all, online, offline
        this.showAllPresence = false; // For presence grid show more
        this.showAllEmployees = false; // For occupants list employees
        this.showAllVisitors = false; // For occupants list visitors
        this.INITIAL_PRESENCE_LIMIT = 4; // Show 4 tiles initially
        this.INITIAL_LIST_LIMIT = 5; // Show 5 per section initially
        this.lastRefreshTime = null;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.fetchOccupants();
        this.initializeAnimations();
    }
    
    setupEventListeners() {
        // Check-in/Check-out buttons
        const checkInBtn = document.getElementById('checkInBtn');
        const emergencyBtn = document.getElementById('emergencyBtn');
        const refreshBtn = document.getElementById('refreshBtn');
        const searchInput = document.getElementById('searchInput');
        const filterBtns = document.querySelectorAll('.filter-btn');
        
        if (checkInBtn) {
            checkInBtn.addEventListener('click', () => this.handleCheckIn());
        }
        
        if (emergencyBtn) {
            emergencyBtn.addEventListener('click', () => this.toggleEmergency());
        }
        
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.handleRefresh());
        }
        
        if (searchInput) {
            searchInput.addEventListener('input', (e) => this.handleSearch(e.target.value));
        }
        
        filterBtns.forEach(btn => {
            btn.addEventListener('click', (e) => this.handleFilter(e.target.dataset.filter));
        });
        
        // Delegate event for checkout buttons
        document.addEventListener('click', (e) => {
            if (e.target.closest('.btn-checkout')) {
                const id = e.target.closest('.btn-checkout').dataset.id;
                this.handleCheckOut(id);
            }
            
            // Handle employee check-in/check-out toggle
            if (e.target.closest('.employee-toggle')) {
                const employeeEl = e.target.closest('.presence-tile');
                this.toggleEmployeeStatus(employeeEl);
            }
        });
    }
    
    async fetchOccupants(showSuccessToast = false) {
        try {
            this.showLoading(true);
            const response = await fetch(this.API_ENDPOINTS.OCCUPANTS);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            // Update statistics
            this.updateStatistics(data);
            
            // Separate employees and visitors
            this.employees = data.occupants.filter(o => o.type === 'employee');
            this.visitors = data.occupants.filter(o => o.type === 'visitor');
            
            // Render current presence (employees)
            this.renderEmployeePresence();
            
            // Render all occupants list (employees + visitors)
            this.renderOccupantsList(data.occupants);
            
            // Update last refresh time
            this.lastRefreshTime = new Date();
            this.updateRefreshIndicator();
            
            this.showLoading(false);
            
            // Only show success message if explicitly requested (manual refresh)
            if (showSuccessToast) {
                this.showSuccessMessage('Data refreshed successfully');
            }
        } catch (err) {
            console.error('Error fetching occupants:', err);
            this.showError('Failed to load presence data');
            this.showLoading(false);
        }
    }
    
    updateStatistics(data) {
        // Update main statistics
        this.animateNumber('totalInBuilding', data.total);
        this.animateNumber('visitorsToday', data.visitors);
        
        const visitorsInsideMuted = document.getElementById('visitorsInsideMuted');
        if (visitorsInsideMuted) {
            visitorsInsideMuted.textContent = `${data.visitors} currently inside`;
        }
        
        const occupantBadge = document.getElementById('occupantBadge');
        if (occupantBadge) {
            occupantBadge.textContent = `${data.total} People`;
        }
        
        const bannerCount = document.getElementById('bannerCount');
        if (bannerCount) {
            bannerCount.textContent = data.total;
        }
        
        // Update presence count in header
        const presenceCount = document.getElementById('presenceCount');
        if (presenceCount) {
            presenceCount.textContent = `${data.employees} employees in office`;
        }
    }
    
    renderEmployeePresence() {
        const grid = document.querySelector('.presence-grid');
        if (!grid) return;
        
        // Use actual employees from database (fetched from API)
        // No hardcoded fallback - display empty state if no one is checked in
        if (this.employees.length === 0) {
            grid.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 40px; color: #718096;"><i class="fas fa-user-slash" style="font-size: 48px; margin-bottom: 16px; opacity: 0.3;"></i><p>No employees currently checked in</p><p style="font-size: 14px; margin-top: 8px;">Employees can check in at <a href="http://localhost:5002" target="_blank" style="color: #2B7A78; text-decoration: underline;">the login portal</a></p></div>';
            return;
        }
        
        // Set status for all employees as 'online' since they are checked in
        this.employees = this.employees.map(emp => {
            if (!emp.status) emp.status = 'online';
            return emp;
        });
        
        grid.innerHTML = '';
        
        // Determine how many to show
        const displayCount = this.showAllPresence ? this.employees.length : Math.min(this.employees.length, this.INITIAL_PRESENCE_LIMIT);
        const displayEmployees = this.employees.slice(0, displayCount);
        
        displayEmployees.forEach((emp, index) => {
            const status = emp.status || 'online';
            const tile = document.createElement('div');
            tile.className = 'presence-tile';
            tile.dataset.id = emp.id;
            tile.style.animationDelay = `${index * 0.1}s`;
            
            const initials = this.getInitials(emp.name);
            
            tile.innerHTML = `
                <div class="presence-avatar ${status}">
                    <span>${initials}</span>
                    <div class="presence-dot ${status}"></div>
                </div>
                <div class="presence-info">
                    <div class="presence-name">${emp.name}</div>
                    <small class="presence-dept">${emp.department}</small>
                    <div class="presence-status-badge ${status}">${this.getStatusText(status)}</div>
                </div>
                <div class="presence-actions">
                    <button class="btn-icon employee-toggle" title="Toggle status">
                        <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                            <path d="M8 0C3.58 0 0 3.58 0 8s3.58 8 8 8 8-3.58 8-8-3.58-8-8-8zm0 14c-3.31 0-6-2.69-6-6s2.69-6 6-6 6 2.69 6 6-2.69 6-6 6z"/>
                        </svg>
                    </button>
                </div>
            `;
            
            grid.appendChild(tile);
        });
        
        // Add "Show More" button if there are more employees
        if (this.employees.length > this.INITIAL_PRESENCE_LIMIT) {
            const showMoreBtn = document.createElement('div');
            showMoreBtn.className = 'presence-tile show-more-tile';
            showMoreBtn.innerHTML = `
                <button class="show-more-btn" id="presenceShowMoreBtn">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="${this.showAllPresence ? 'M5 12h14' : 'M12 5v14M5 12h14'}"/>
                    </svg>
                    <span>${this.showAllPresence ? 'Show Less' : `Show ${this.employees.length - this.INITIAL_PRESENCE_LIMIT} More`}</span>
                </button>
            `;
            grid.appendChild(showMoreBtn);
            
            // Add event listener
            const btn = document.getElementById('presenceShowMoreBtn');
            if (btn) {
                btn.addEventListener('click', () => {
                    this.showAllPresence = !this.showAllPresence;
                    this.renderEmployeesGrid();
                });
            }
        }
    }
    
    renderOccupantsList(occupants) {
        const container = document.getElementById('occupantList');
        if (!container) return;
        
        container.innerHTML = '';
        
        // Separate employees and visitors
        const employees = occupants.filter(o => o.type === 'employee');
        const visitors = occupants.filter(o => o.type === 'visitor');
        
        // Filter based on search
        let filteredEmployees = employees;
        let filteredVisitors = visitors;
        
        if (this.searchTerm) {
            const searchLower = this.searchTerm.toLowerCase();
            filteredEmployees = employees.filter(o => 
                o.name.toLowerCase().includes(searchLower) ||
                (o.department && o.department.toLowerCase().includes(searchLower))
            );
            filteredVisitors = visitors.filter(o =>
                o.name.toLowerCase().includes(searchLower) ||
                (o.company && o.company.toLowerCase().includes(searchLower)) ||
                (o.host && o.host.toLowerCase().includes(searchLower))
            );
        }
        
        // Check if we have any results
        if (filteredEmployees.length === 0 && filteredVisitors.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#16636a" stroke-width="2">
                        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                        <circle cx="12" cy="7" r="4"></circle>
                    </svg>
                    <p>No occupants found</p>
                </div>
            `;
            return;
        }
        
        // Create container for both sections side by side
        const sectionsContainer = document.createElement('div');
        sectionsContainer.className = 'occupants-sections-container';
        
        // Render Employees Section
        if (filteredEmployees.length > 0) {
            const employeesSection = document.createElement('div');
            employeesSection.className = 'occupants-section';
            
            const employeesHeader = document.createElement('button');
            employeesHeader.className = 'section-header';
            employeesHeader.innerHTML = `
                <div class="section-header-content">
                    <div class="section-icon">
                        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                            <circle cx="9" cy="7" r="4"></circle>
                            <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
                            <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
                        </svg>
                    </div>
                    <div class="section-header-info">
                        <h3 class="section-title">Employees</h3>
                        <span class="section-count">${filteredEmployees.length} in office</span>
                    </div>
                    <svg class="section-chevron" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M6 9l6 6 6-6"/>
                    </svg>
                </div>
            `;
            
            const employeeContainer = document.createElement('div');
            employeeContainer.className = 'occupants-list collapsed';
            employeeContainer.id = 'employeesList';
            
            const displayCount = this.showAllEmployees ? filteredEmployees.length : Math.min(filteredEmployees.length, this.INITIAL_LIST_LIMIT);
            const displayedEmployees = filteredEmployees.slice(0, displayCount);
            
            displayedEmployees.forEach((o, index) => {
                const div = this.createOccupantCard(o, index);
                employeeContainer.appendChild(div);
            });
            
            // Add show more button for employees if needed
            if (filteredEmployees.length > this.INITIAL_LIST_LIMIT) {
                const showMoreBtn = document.createElement('button');
                showMoreBtn.className = 'show-more-list-btn';
                showMoreBtn.innerHTML = `
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="${this.showAllEmployees ? 'M18 15l-6-6-6 6' : 'M6 9l6 6 6-6'}"/>
                    </svg>
                    ${this.showAllEmployees ? 'Show Less' : `Show ${filteredEmployees.length - this.INITIAL_LIST_LIMIT} More`}
                `;
                showMoreBtn.onclick = (e) => {
                    e.stopPropagation();
                    this.showAllEmployees = !this.showAllEmployees;
                    this.renderOccupantsList(occupants);
                };
                employeeContainer.appendChild(showMoreBtn);
            }
            
            // Toggle functionality
            employeesHeader.onclick = () => {
                employeeContainer.classList.toggle('collapsed');
                employeesHeader.classList.toggle('expanded');
            };
            
            employeesSection.appendChild(employeesHeader);
            employeesSection.appendChild(employeeContainer);
            sectionsContainer.appendChild(employeesSection);
        }
        
        // Render Visitors Section
        if (filteredVisitors.length > 0) {
            const visitorsSection = document.createElement('div');
            visitorsSection.className = 'occupants-section';
            
            const visitorsHeader = document.createElement('button');
            visitorsHeader.className = 'section-header visitor-header';
            visitorsHeader.innerHTML = `
                <div class="section-header-content">
                    <div class="section-icon visitor-icon">
                        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <circle cx="9" cy="7" r="4"></circle>
                            <path d="M3 21v-2a4 4 0 0 1 4-4h4a4 4 0 0 1 4 4v2"></path>
                            <line x1="19" y1="8" x2="19" y2="14"></line>
                            <line x1="22" y1="11" x2="16" y2="11"></line>
                        </svg>
                    </div>
                    <div class="section-header-info">
                        <h3 class="section-title">Visitors</h3>
                        <span class="section-count">${filteredVisitors.length} checked in</span>
                    </div>
                    <svg class="section-chevron" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M6 9l6 6 6-6"/>
                    </svg>
                </div>
            `;
            
            const visitorContainer = document.createElement('div');
            visitorContainer.className = 'occupants-list collapsed';
            visitorContainer.id = 'visitorsList';
            
            const displayCount = this.showAllVisitors ? filteredVisitors.length : Math.min(filteredVisitors.length, this.INITIAL_LIST_LIMIT);
            const displayedVisitors = filteredVisitors.slice(0, displayCount);
            
            displayedVisitors.forEach((o, index) => {
                const div = this.createOccupantCard(o, index);
                visitorContainer.appendChild(div);
            });
            
            // Add show more button for visitors if needed
            if (filteredVisitors.length > this.INITIAL_LIST_LIMIT) {
                const showMoreBtn = document.createElement('button');
                showMoreBtn.className = 'show-more-list-btn';
                showMoreBtn.innerHTML = `
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="${this.showAllVisitors ? 'M18 15l-6-6-6 6' : 'M6 9l6 6 6-6'}"/>
                    </svg>
                    ${this.showAllVisitors ? 'Show Less' : `Show ${filteredVisitors.length - this.INITIAL_LIST_LIMIT} More`}
                `;
                showMoreBtn.onclick = (e) => {
                    e.stopPropagation();
                    this.showAllVisitors = !this.showAllVisitors;
                    this.renderOccupantsList(occupants);
                };
                visitorContainer.appendChild(showMoreBtn);
            }
            
            // Toggle functionality
            visitorsHeader.onclick = () => {
                visitorContainer.classList.toggle('collapsed');
                visitorsHeader.classList.toggle('expanded');
            };
            
            visitorsSection.appendChild(visitorsHeader);
            visitorsSection.appendChild(visitorContainer);
            sectionsContainer.appendChild(visitorsSection);
        }
        
        container.appendChild(sectionsContainer);
    }
    
    createOccupantCard(o, index) {
        const div = document.createElement('div');
        div.className = 'occupant';
        div.dataset.id = o.id;
        div.style.animationDelay = `${index * 0.05}s`;
        
        if (o.type === 'visitor') {
            div.classList.add('visitor-occupant');
        }
        
        const initials = this.getInitials(o.name);
        const avatarClass = o.type === 'employee' ? 'avatar-employee' : 'avatar-visitor';
        
        div.innerHTML = `
            <div class="left">
                <div class="avatar ${avatarClass}">${initials}</div>
                <div class="meta">
                    <div class="name">
                        ${o.name} 
                        <span class="user-badge ${o.type}-badge">
                            ${o.type === 'employee' ? 'Employee' : 'Visitor'}
                        </span>
                    </div>
                    <div class="muted">
                        ${o.type === 'employee' ? o.department : o.company + (o.host ? ' • Visiting ' + o.host : '')}
                    </div>
                </div>
            </div>
            <div class="actions-row">
                <div class="check">
                    <span class="check-label">Check-in</span>
                    <span class="time">${o.time}</span>
                </div>
                ${o.type === 'visitor' ? `
                    <button class="btn btn-checkout" data-id="${o.id.substring(1)}">
                        <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                            <path d="M8 0C3.58 0 0 3.58 0 8s3.58 8 8 8 8-3.58 8-8-3.58-8-8-8zM7 11.41L3.59 8 5 6.59l2 2 4-4L12.41 6 7 11.41z"/>
                        </svg>
                        Check Out
                    </button>
                ` : ''}
            </div>
        `;
        
        return div;
    }
    
    async handleCheckIn() {
        const modal = this.createCheckInModal();
        document.body.appendChild(modal);
        
        const form = modal.querySelector('#checkInForm');
        const closeBtn = modal.querySelector('.modal-close');
        const cancelBtn = modal.querySelector('.btn-cancel');
        
        closeBtn.addEventListener('click', () => {
            this.closeModal(modal);
        });
        
        cancelBtn.addEventListener('click', () => {
            this.closeModal(modal);
        });
        
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const name = form.querySelector('#visitorName').value;
            const company = form.querySelector('#visitorCompany').value;
            const host = form.querySelector('#visitorHost').value;
            
            console.log('📤 Submitting visitor check-in:', { name, company, hostName: host });
            
            try {
                const response = await fetch(this.API_ENDPOINTS.VISITORS, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        name,
                        company,
                        hostName: host
                    })
                });
                
                console.log('📡 Response status:', response.status);
                const data = await response.json();
                console.log('📡 Response data:', data);
                
                if (!response.ok) {
                    throw new Error(data.error || 'Failed to check in visitor');
                }
                
                this.showSuccessMessage('Visitor checked in successfully');
                this.fetchOccupants();
                this.closeModal(modal);
            } catch (err) {
                console.error('❌ Error checking in visitor:', err);
                this.showError('Failed to check in visitor: ' + err.message);
            }
        });
        
        // Show modal with animation
        setTimeout(() => modal.classList.add('show'), 10);
    }
    
    async handleCheckOut(id) {
        if (!confirm('Check out this visitor?')) return;
        
        try {
            await fetch(`${this.API_ENDPOINTS.VISITORS}/${id}/checkout`, {
                method: 'POST'
            });
            
            this.showSuccessMessage('Visitor checked out successfully');
            this.fetchOccupants();
        } catch (err) {
            console.error('Error checking out visitor:', err);
            this.showError('Failed to check out visitor');
        }
    }
    
    async toggleEmergency() {
        try {
            await fetch(this.API_ENDPOINTS.EMERGENCY, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    active: !this.isEmergencyMode
                })
            });
            
            this.isEmergencyMode = !this.isEmergencyMode;
            this.updateEmergencyUI();
            this.fetchOccupants();
        } catch (err) {
            console.error('Error toggling emergency mode:', err);
            this.showError('Failed to toggle emergency mode');
        }
    }
    
    updateEmergencyUI() {
        const banner = document.getElementById('emergencyBanner');
        const btn = document.getElementById('emergencyBtn');
        const emergencyInfo = document.getElementById('emergencyInfo');
        
        if (this.isEmergencyMode) {
            banner.style.display = 'block';
            banner.classList.add('slide-down');
            btn.textContent = 'Deactivate Emergency';
            btn.classList.add('active');
            document.body.classList.add('emergency-mode');
            
            // Show emergency information section
            if (emergencyInfo) {
                emergencyInfo.style.display = 'block';
                setTimeout(() => {
                    emergencyInfo.classList.add('emergency-info-visible');
                }, 100);
            }
        } else {
            banner.classList.remove('slide-down');
            setTimeout(() => {
                banner.style.display = 'none';
            }, 300);
            btn.textContent = 'Emergency Mode';
            btn.classList.remove('active');
            document.body.classList.remove('emergency-mode');
            
            // Hide emergency information section
            if (emergencyInfo) {
                emergencyInfo.classList.remove('emergency-info-visible');
                setTimeout(() => {
                    emergencyInfo.style.display = 'none';
                }, 300);
            }
        }
    }
    
    toggleEmployeeStatus(employeeEl) {
        const dot = employeeEl.querySelector('.presence-dot');
        const statusBadge = employeeEl.querySelector('.presence-status-badge');
        const avatar = employeeEl.querySelector('.presence-avatar');
        
        const isOnline = dot.classList.contains('online');
        
        if (isOnline) {
            dot.classList.remove('online');
            dot.classList.add('offline');
            statusBadge.classList.remove('online');
            statusBadge.classList.add('offline');
            avatar.classList.remove('online');
            avatar.classList.add('offline');
            statusBadge.textContent = 'Offline';
        } else {
            dot.classList.remove('offline');
            dot.classList.add('online');
            statusBadge.classList.remove('offline');
            statusBadge.classList.add('online');
            avatar.classList.remove('offline');
            avatar.classList.add('online');
            statusBadge.textContent = 'In Office';
        }
        
        // Add pulse animation
        employeeEl.classList.add('pulse');
        setTimeout(() => employeeEl.classList.remove('pulse'), 600);
    }
    
    handleRefresh() {
        const btn = document.getElementById('refreshBtn');
        if (btn) {
            btn.classList.add('spinning');
            setTimeout(() => btn.classList.remove('spinning'), 1000);
        }
        this.fetchOccupants(true); // Show success toast on manual refresh
    }
    
    updateRefreshIndicator() {
        // Update presence count with last refresh time
        const presenceCount = document.getElementById('presenceCount');
        if (presenceCount && this.lastRefreshTime) {
            const timeStr = this.lastRefreshTime.toLocaleTimeString('en-US', { 
                hour: 'numeric', 
                minute: '2-digit',
                second: '2-digit'
            });
            const currentText = presenceCount.textContent.split('•')[0].trim();
            presenceCount.innerHTML = `${currentText} <span style="opacity: 0.6; font-size: 0.85em;">• Updated ${timeStr}</span>`;
        }
    }
    
    handleSearch(value) {
        this.searchTerm = value;
        this.fetchOccupants();
    }
    
    handleFilter(filter) {
        this.filterStatus = filter;
        
        // Update active filter button
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.classList.remove('active');
            if (btn.dataset.filter === filter) {
                btn.classList.add('active');
            }
        });
        
        this.fetchOccupants();
    }
    
    // Auto refresh disabled per request; manual refresh via button still available
    // startAutoRefresh() {
    //     this.refreshInterval = setInterval(() => {
    //         this.fetchOccupants();
    //     }, 10000);
    // }
    
    initializeAnimations() {
        // Add fade-in animation to cards
        const cards = document.querySelectorAll('.card');
        cards.forEach((card, index) => {
            card.style.animationDelay = `${index * 0.1}s`;
            card.classList.add('fade-in');
        });
    }
    
    createCheckInModal() {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Check In Visitor</h3>
                    <button class="modal-close">&times;</button>
                </div>
                <form id="checkInForm">
                    <div class="form-group">
                        <label for="visitorName">Visitor Name *</label>
                        <input type="text" id="visitorName" name="name" required placeholder="e.g. John Doe">
                    </div>
                    <div class="form-group">
                        <label for="visitorCompany">Company</label>
                        <input type="text" id="visitorCompany" name="company" placeholder="e.g. ABC Corp">
                    </div>
                    <div class="form-group">
                        <label for="visitorHost">Visiting Who?</label>
                        <input type="text" id="visitorHost" name="host" placeholder="e.g. Sarah Johnson">
                    </div>
                    <div class="modal-actions">
                        <button type="button" class="btn btn-cancel">Cancel</button>
                        <button type="submit" class="btn btn-primary">Check In</button>
                    </div>
                </form>
            </div>
        `;
        return modal;
    }
    
    closeModal(modal) {
        modal.classList.remove('show');
        setTimeout(() => {
            modal.remove();
        }, 300);
    }
    
    showLoading(show) {
        const loader = document.getElementById('loadingIndicator');
        if (loader) {
            loader.style.display = show ? 'block' : 'none';
        }
    }
    
    showSuccessMessage(message) {
        this.showToast(message, 'success');
    }
    
    showError(message) {
        this.showToast(message, 'error');
    }
    
    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        
        document.body.appendChild(toast);
        
        setTimeout(() => toast.classList.add('show'), 10);
        
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
    
    animateNumber(elementId, targetValue) {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        const currentValue = parseInt(element.textContent) || 0;
        const duration = 500;
        const steps = 20;
        const stepValue = (targetValue - currentValue) / steps;
        const stepDuration = duration / steps;
        
        let step = 0;
        const timer = setInterval(() => {
            step++;
            const newValue = Math.round(currentValue + (stepValue * step));
            element.textContent = newValue;
            
            if (step >= steps) {
                clearInterval(timer);
                element.textContent = targetValue;
            }
        }, stepDuration);
    }
    
    getInitials(name) {
        return name.split(' ')
            .map(s => s[0])
            .slice(0, 2)
            .join('')
            .toUpperCase();
    }
    
    getStatusText(status) {
        const statusMap = {
            'online': 'In Office',
            'offline': 'Offline',
            'remote': 'Remote',
            'meeting': 'In Meeting',
            'break': 'On Break'
        };
        return statusMap[status] || 'Unknown';
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new PresenceTracker();
});
