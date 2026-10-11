class ThreatWebSocket {
  constructor() {
    this.ws = null;
    this.listeners = new Set();
    this.statusListeners = new Set();
    this.isConnected = false;
    this.reconnectTimer = null;
    this.pingInterval = null;
  }

  connect() {
    if (this.ws && (this.ws.readyState === WebSocket.OPEN || this.ws.readyState === WebSocket.CONNECTING)) {
      return;
    }

    const wsUrl = import.meta.env.VITE_WS_URL || 'ws://127.0.0.1:8000/ws/alerts';
    
    try {
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        this.isConnected = true;
        this.notifyStatus(true);
        // Start ping heartbeat
        this.pingInterval = setInterval(() => {
          if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send('ping');
          }
        }, 25000);
      };

      this.ws.onmessage = (event) => {
        try {
          if (event.data === 'pong') return;
          const data = JSON.parse(event.data);
          this.notifyListeners(data);
        } catch (e) {
          console.debug('Raw WebSocket message:', event.data);
        }
      };

      this.ws.onclose = () => {
        this.isConnected = false;
        this.notifyStatus(false);
        this.cleanup();
        this.scheduleReconnect();
      };

      this.ws.onerror = (err) => {
        console.warn('WebSocket connection warning:', err);
        this.ws?.close();
      };
    } catch (err) {
      console.error('Failed to initiate WebSocket:', err);
      this.scheduleReconnect();
    }
  }

  scheduleReconnect() {
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
    this.reconnectTimer = setTimeout(() => {
      this.connect();
    }, 4000);
  }

  cleanup() {
    if (this.pingInterval) clearInterval(this.pingInterval);
  }

  subscribe(callback) {
    this.listeners.add(callback);
    return () => this.listeners.delete(callback);
  }

  subscribeStatus(callback) {
    this.statusListeners.add(callback);
    callback(this.isConnected);
    return () => this.statusListeners.delete(callback);
  }

  notifyListeners(data) {
    for (const cb of this.listeners) {
      try {
        cb(data);
      } catch (e) {
        console.error('Error in WS subscriber callback:', e);
      }
    }
  }

  notifyStatus(status) {
    for (const cb of this.statusListeners) {
      try {
        cb(status);
      } catch (e) {
        console.error('Error in WS status callback:', e);
      }
    }
  }
}

export const wsClient = new ThreatWebSocket();
