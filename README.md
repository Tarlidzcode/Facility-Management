# Office Management Portal Suite

A comprehensive collection of individual web portals for office management, each running as a standalone Flask application.

## 🏢 Portal Overview

The system consists of 6 independent portals that can run simultaneously or individually:

1. **Temperature Portal** (Port 5001) - HVAC monitoring and control
2. **Coffee Portal** (Port 5002) - Coffee machine management  
3. **Dashboard Portal** (Port 5003) - Office overview and metrics
4. **Employee Portal** (Port 5004) - Employee management and tracking
5. **Stock Portal** (Port 5005) - Inventory and supply management
6. **Presence Portal** (Port 5006) - Presence tracking and safety

## 🚀 Quick Start

### Prerequisites

- Python 3.8+ installed
- All dependencies installed (see requirements.txt)

### Installation

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Running the Portals

#### Option 1: Start All Portals at Once

**Windows:**
```powershell
.\start_all_portals.ps1
```

**Linux/Mac:**
```bash
chmod +x start_all_portals.sh
./start_all_portals.sh
```

#### Option 2: Use Portal Manager
```bash
python portal_manager.py
```

The portal manager provides an interactive interface to:
- Start/stop individual portals
- View portal status
- Open portals in browser
- Monitor health

#### Option 3: Start Individual Portals

Each portal can run independently:

```bash
# Temperature monitoring
python temperature_portal.py

# Coffee management  
python coffee_portal.py

# Office dashboard
python dashboard_portal.py

# Employee management
python employee_portal.py

# Inventory management
python stock_portal.py

# Presence tracking
python presence_portal.py
```

## 🌐 Portal URLs

Once running, access the portals at:

- **Temperature:** http://localhost:5001
- **Coffee:** http://localhost:5002  
- **Dashboard:** http://localhost:5003
- **Employee:** http://localhost:5004
- **Stock:** http://localhost:5005
- **Presence:** http://localhost:5006

## 📋 Features

### Temperature Portal
- Real-time temperature monitoring
- HVAC system control
- Temperature trend analysis
- Alert notifications
- Multi-zone management

### Coffee Portal
- Coffee machine status monitoring
- Brewing controls and scheduling
- Supply level tracking
- Maintenance alerts
- Usage analytics

### Dashboard Portal  
- Office overview metrics
- Real-time status indicators
- Performance charts
- System health monitoring
- Integrated alerts

### Employee Portal
- Employee information management
- Check-in/check-out tracking
- Department organization
- Contact management
- Activity logging

### Stock Portal
- Inventory level monitoring
- Low stock alerts
- Restock ordering
- Supplier management
- Usage tracking

### Presence Portal
- Real-time presence tracking
- Visitor management
- Safety monitoring
- Emergency procedures
- Access control

## 🛠 Technical Details

### Architecture
- **Framework:** Flask 2.3.3
- **Database:** SQLAlchemy with SQLite
- **Frontend:** HTML5, CSS3, JavaScript (ES6+)
- **API:** RESTful endpoints with JSON
- **Real-time:** Auto-refresh every 30 seconds

### Port Configuration
Each portal runs on a dedicated port to enable:
- Independent operation
- Isolated failures
- Parallel development
- Load balancing

### Data Management
- Mock data simulation for demonstration
- SQLAlchemy models for production data
- JSON API responses
- Real-time updates

## 🔧 Development

### Project Structure
```
eathon2/
├── *_portal.py          # Individual portal applications
├── portal_manager.py    # Central management utility
├── models.py           # Database models
├── requirements.txt    # Python dependencies
├── templates/          # HTML templates
│   ├── *_portal.html   # Portal-specific templates
│   └── base.html       # Base template
├── static/             # Static assets
│   ├── css/           # Stylesheets
│   ├── js/            # JavaScript files
│   └── pages/         # Page-specific assets
└── services/          # Backend services
    └── mock_data.py   # Data simulation
```

### Adding New Features
1. Update the relevant portal Python file
2. Modify the corresponding HTML template
3. Add new API endpoints as needed
4. Update mock data if required

### Testing
Run the test suite to validate all portals:
```bash
python test_portals.py
```

## 🔒 Security Considerations

- CORS enabled for development
- Input validation on all forms
- SQL injection protection via SQLAlchemy
- XSS protection with template escaping

## 📱 Mobile Support

All portals are fully responsive and work on:
- Desktop browsers
- Tablets  
- Mobile devices
- Touch interfaces

## 🆘 Troubleshooting

### Common Issues

1. **Port Already in Use:**
   - Stop existing processes on the ports
   - Use portal manager to check status

2. **Module Import Errors:**
   - Ensure all dependencies are installed
   - Check Python path configuration

3. **Database Errors:**
   - Initialize database with: `flask db upgrade`
   - Check file permissions

4. **Template Not Found:**
   - Verify templates directory exists
   - Check template file names

### Health Checks
Each portal provides a health endpoint:
- `GET /health` - Returns portal status

### Logs
Portal logs are displayed in the console when running in development mode.

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review console logs for errors
3. Ensure all dependencies are installed
4. Verify port availability

## 🎯 Future Enhancements

- Database persistence
- User authentication
- Real sensor integration
- Mobile apps
- Advanced analytics
- Multi-tenant support

---

**Ready to manage your office like never before!** 🏢✨