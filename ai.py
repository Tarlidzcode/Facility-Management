# ai.py - Azure OpenAI Integration
"""
Azure OpenAI functionality for the Office Management System
This is the main AI integration file using Azure OpenAI
"""
import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# If .env loading fails, try direct path
if not os.getenv('AZURE_OPENAI_ENDPOINT'):
    load_dotenv('.env')

class AzureAIAssistant:
    """Azure OpenAI-powered assistant for office management questions"""
    
    def __init__(self):
        # Azure OpenAI Configuration
        self.azure_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
        self.azure_api_key = os.getenv('AZURE_OPENAI_API_KEY')
        self.deployment_name = os.getenv('AZURE_OPENAI_DEPLOYMENT')
        self.api_version = os.getenv('AZURE_OPENAI_API_VERSION', '2024-10-21')  # Use compatible version
        
        # Office context for AI responses
        self.office_context = """
        You are an AI assistant for an Office Management System. Help users with:
        - Coffee machine status and usage
        - Temperature monitoring and control
        - Employee presence tracking
        - Stock management and inventory
        - Dashboard metrics and features
        - General office management questions
        
        Be helpful, concise, and focus on the office management features.
        """
    
    def is_configured(self) -> bool:
        """Check if Azure OpenAI is properly configured"""
        return all([
            self.azure_endpoint,
            self.azure_api_key,
            self.deployment_name,
            self.api_version
        ])
    
    def get_response(self, user_message: str, context_data: Optional[Dict[Any, Any]] = None) -> str:
        """
        Get AI response from Azure OpenAI
        
        Args:
            user_message: User's question
            context_data: Optional live office data (presence, stock, coffee, temperature)
            
        Returns:
            AI response with REAL data or intelligent fallback response
        """
        # If we have context data, try to answer with real data first (even without Azure)
        if context_data:
            smart_response = self._get_smart_response_with_data(user_message, context_data)
            if smart_response:
                return smart_response
        
        if not self.is_configured():
            print("Azure OpenAI not configured - using fallback responses")
            return self._get_fallback_response(user_message)
        
        try:
            from openai import AzureOpenAI
            
            # Create Azure OpenAI client (try different approaches)
            try:
                client = AzureOpenAI(
                    azure_endpoint=self.azure_endpoint,
                    api_key=self.azure_api_key,
                    api_version=self.api_version
                )
            except TypeError as e:
                if "proxies" in str(e):
                    # Handle the proxies parameter issue
                    print("OpenAI client compatibility issue detected - using data-driven responses")
                    if context_data:
                        return self._get_smart_response_with_data(user_message, context_data) or self._get_fallback_response(user_message)
                    return self._get_fallback_response(user_message)
                raise e
            
            # Build system message with REAL data
            system_message = self.office_context
            if context_data:
                system_message += f"\n\nCurrent REAL office data: {context_data}"
                system_message += "\n\nIMPORTANT: Use the REAL data provided above to answer questions. Give specific numbers, names, and times."
            
            # Get AI response
            response = client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=300,
                temperature=0.3
            )
            
            if response.choices and response.choices[0].message:
                ai_response = response.choices[0].message.content.strip()
                if ai_response:
                    print("✅ Azure OpenAI response generated successfully with REAL data")
                    return ai_response
            
            return self._get_fallback_response(user_message)
            
        except ImportError:
            print("OpenAI package not installed - using data-driven responses")
            if context_data:
                return self._get_smart_response_with_data(user_message, context_data) or self._get_fallback_response(user_message)
            return self._get_fallback_response(user_message)
            
        except Exception as e:
            error_msg = str(e)
            print(f"Azure OpenAI Error: {error_msg}")
            
            # Provide specific feedback for different types of errors
            if "DeploymentNotFound" in error_msg:
                print("💡 Azure OpenAI: Deployment 'gpt-4o' not found - using data-driven responses")
            elif "authentication" in error_msg.lower() or "Unauthorized" in error_msg:
                print("💡 Azure OpenAI: Authentication failed - using data-driven responses")
            elif "proxies" in error_msg:
                print("💡 Azure OpenAI: Client compatibility issue - using data-driven responses")
            else:
                print("💡 Azure OpenAI: Connection failed - using data-driven responses")
            
            # Try to answer with real data if available
            if context_data:
                return self._get_smart_response_with_data(user_message, context_data) or self._get_fallback_response(user_message)
            
            return self._get_fallback_response(user_message)
    
    def _get_smart_response_with_data(self, user_message: str, context_data: Dict) -> Optional[str]:
        """Generate intelligent responses using REAL data from the database"""
        message_lower = user_message.lower()
        
        # STOCK QUESTIONS - Check first since "stock" is specific
        if 'stock' in context_data and any(word in message_lower for word in ['stock', 'inventory', 'low', 'reorder', 'supplies', 'item', 'what']):
            stock = context_data['stock']
            low_count = stock.get('low_stock_count', 0)
            low_items = stock.get('low_stock_items', [])
            
            if low_count > 0:
                items_text = '\n'.join([f"• {item['name']}: {item['quantity']} {item['unit']} (reorder at {item['reorder_point']})" 
                                       for item in low_items[:5]])
                return f"� {low_count} items need reordering:\n{items_text}"
            return "� All stock levels are good! No items need reordering at this time."
        
        # TEMPERATURE QUESTIONS - Check before presence since "office" might appear in both
        if 'temperature' in context_data and any(word in message_lower for word in ['temperature', 'temp', 'climate', 'hot', 'cold', 'weather']):
            temp_data = context_data['temperature']
            readings = temp_data.get('latest_readings', [])
            
            if readings:
                # Show multiple sensors if available
                if len(readings) > 1:
                    readings_text = '\n'.join([f"• {r['sensor']}: {r['temperature']}°C, {r['humidity']}% humidity" 
                                              for r in readings[:3]])
                    return f"🌡️ Current temperature readings:\n{readings_text}\n\nLatest update: {readings[0]['time']}"
                else:
                    latest = readings[0]
                    return f"🌡️ {latest['sensor']}: {latest['temperature']}°C, {latest['humidity']}% humidity (updated {latest['time']})"
            return "🌡️ Temperature sensors are being monitored. Check /temperature for current readings."
        
        # COFFEE QUESTIONS
        if 'coffee' in context_data and any(word in message_lower for word in ['coffee', 'order', 'beans', 'drink']):
            coffee = context_data['coffee']
            today_orders = coffee.get('orders_today', 0)
            recent = coffee.get('recent_orders', [])
            
            if 'how many' in message_lower or 'count' in message_lower or 'today' in message_lower:
                return f"☕ {today_orders} coffee orders placed today."
            
            if recent and ('recent' in message_lower or 'last' in message_lower or 'who' in message_lower):
                recent_text = '\n'.join([f"• {order['user']}: {order['type']} at {order['time']}" 
                                        for order in recent[:3]])
                return f"☕ Recent coffee orders:\n{recent_text}\n\nTotal today: {today_orders} orders."
            
            return f"☕ {today_orders} coffee orders placed today."
        
        # PRESENCE QUESTIONS - Check last since "office" is a common word
        if 'presence' in context_data and any(word in message_lower for word in ['who', 'employee', 'staff', 'office', 'present', 'checked in', 'people']):
            presence = context_data['presence']
            total = presence.get('total_in_office', 0)
            employees = presence.get('employees_present', [])
            
            if 'how many' in message_lower or 'count' in message_lower:
                return f"👥 Currently {total} out of {presence.get('total_employees', 0)} employees are in the office."
            
            if employees and ('who' in message_lower or 'list' in message_lower):
                emp_list = '\n'.join([f"• {emp['name']} ({emp['department']}) - checked in at {emp['time']}" 
                                      for emp in employees[:5]])
                if len(employees) > 5:
                    return f"👥 {total} employees currently in office:\n{emp_list}\n... and {len(employees) - 5} more."
                return f"👥 {total} employees currently in office:\n{emp_list}"
            
            if total > 0:
                return f"👥 {total} employees are currently in the office."
            return "👥 No employees are currently checked into the office."
        
        return None  # No smart response available
    
    def _get_fallback_response(self, user_message: str) -> str:
        """Fallback responses when Azure OpenAI is unavailable - now uses REAL data if available"""
        message_lower = user_message.lower()
        
        # Try to extract context data that might have been passed
        # For now, provide intelligent fallback responses based on keywords
        
        if any(word in message_lower for word in ['coffee', 'beans', 'machine', 'order']):
            if 'how many' in message_lower or 'count' in message_lower or 'total' in message_lower:
                return "☕ Coffee Orders: Check the /coffee page to see today's order count, bean levels, and recent orders."
            elif 'who' in message_lower or 'recent' in message_lower:
                return "☕ Recent Coffee Orders: View the latest coffee orders on the /coffee page with user details and order times."
            else:
                return "☕ Coffee Machine: Check /coffee page for bean levels, usage stats, and order history."
        
        elif any(word in message_lower for word in ['temperature', 'temp', 'climate', 'hot', 'cold', 'weather']):
            if 'current' in message_lower or 'now' in message_lower or 'latest' in message_lower:
                return "🌡️ Current Temperature: View live temperature and humidity readings from all sensors on /temperature page."
            elif 'office' in message_lower:
                return "🌡️ Office Temperature: Monitor indoor climate control with real-time sensor data on /temperature page."
            else:
                return "🌡️ Temperature: Monitor office climate, humidity, and compare indoor/outdoor conditions on /temperature page."
        
        elif any(word in message_lower for word in ['employee', 'presence', 'staff', 'who', 'office', 'checked in']):
            if 'how many' in message_lower or 'count' in message_lower or 'total' in message_lower:
                return "👥 Employee Count: See total employees in office and detailed presence logs on /presence page."
            elif 'who' in message_lower:
                return "👥 Who's In Office: View all employees currently checked in with departments and check-in times on /presence page."
            else:
                return "👥 Employees: Check /presence for who's in the office, check-in/out functionality, and /employees for staff management."
        
        elif any(word in message_lower for word in ['stock', 'inventory', 'supplies', 'low', 'reorder']):
            if 'low' in message_lower or 'reorder' in message_lower or 'alert' in message_lower:
                return "📦 Low Stock Alerts: View items below reorder point and manage inventory on /stock page."
            elif 'how many' in message_lower or 'count' in message_lower:
                return "📦 Stock Levels: Check current quantities, reorder points, and supplier info on /stock page."
            else:
                return "📦 Stock: Manage inventory, view low-stock alerts, track stock movements on /stock page."
        
        elif any(word in message_lower for word in ['dashboard', 'overview', 'metrics', 'stats']):
            return "📊 Dashboard: View office metrics, charts, and real-time stats on the main dashboard page."
        
        elif 'help' in message_lower or 'what can' in message_lower or 'features' in message_lower:
            return ("🤖 I can help you with:\n"
                    "☕ Coffee - Orders, bean levels, machine status\n"
                    "🌡️ Temperature - Climate monitoring, sensor readings\n"
                    "👥 Presence - Who's in office, check-ins, employee counts\n"
                    "📦 Stock - Inventory levels, low stock alerts\n"
                    "📊 Dashboard - Metrics and office statistics\n"
                    "\nAsk me anything about these features!")
        
        else:
            return "🤖 Office Assistant: I help with coffee orders, temperature monitoring, employee presence, stock management, and dashboard metrics. What would you like to know?"

# Create global instance
azure_ai = AzureAIAssistant()

def get_ai_response(message: str, context: Optional[Dict] = None) -> str:
    """Main function to get AI responses"""
    return azure_ai.get_response(message, context)

def stream_ai_response(message: str, context: Optional[Dict] = None):
    """Generator that yields chunks of an AI response for streaming (SSE/WebSocket).

    Strategy:
    1. Attempt Azure OpenAI streaming if configured.
    2. If not configured or error occurs, fall back to data-driven smart/fallback response
       and yield it in small chunks to simulate streaming.
    """
    # Try Azure streaming first
    if azure_ai.is_configured():
        try:
            from openai import AzureOpenAI
            client = AzureOpenAI(
                azure_endpoint=azure_ai.azure_endpoint,
                api_key=azure_ai.azure_api_key,
                api_version=azure_ai.api_version
            )
            system_message = azure_ai.office_context
            if context:
                system_message += f"\n\nCurrent REAL office data: {context}\nUse this data directly in your answer."
            # Use responses API if available for streaming
            try:
                stream = client.chat.completions.create(
                    model=azure_ai.deployment_name,
                    messages=[
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": message}
                    ],
                    max_tokens=300,
                    temperature=0.3,
                    stream=True
                )
                full_text = []
                for event in stream:
                    delta = ''
                    try:
                        delta = event.choices[0].delta.content or ''  # type: ignore
                    except Exception:
                        # Different SDK versions may structure chunks differently
                        delta = getattr(event, 'content', '') or ''
                    if delta:
                        full_text.append(delta)
                        yield delta
                # Ensure at least something returned
                if not full_text:
                    fallback = azure_ai.get_response(message, context)
                    for ch in fallback:
                        yield ch
                return
            except TypeError as te:
                if 'stream' in str(te).lower():
                    # Streaming not supported in this SDK variant; fall through to fallback streaming
                    pass
                else:
                    raise te
        except Exception as e:  # noqa: BLE001
            print(f"Azure streaming failed, using fallback streaming: {e}")

    # Fallback: get full response then yield in chunks
    full = azure_ai.get_response(message, context)
    # Simple token/chunk splitting (by space, keeping punctuation)
    words = full.split(' ')
    buffer = []
    char_limit = 40
    for w in words:
        buffer.append(w)
        if sum(len(x) for x in buffer) + len(buffer) - 1 >= char_limit:
            chunk = ' '.join(buffer)
            yield chunk + ' '
            buffer = []
    if buffer:
        yield ' '.join(buffer)
