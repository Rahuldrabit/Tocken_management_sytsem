import React, { useCallback, useEffect, useMemo, useState, createContext, useContext } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { jwtDecode } from 'jwt-decode';
import './index.css';
import './ticket-ui.css';
import AdminDashboard from './AdminDashboard';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

// User Role Context for RBAC
const UserContext = createContext(null);

const useUserRole = () => {
  const context = useContext(UserContext);
  if (!context) {
    throw new Error('useUserRole must be used within UserProvider');
  }
  return context;
};

const UserProvider = ({ children, token }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!token) {
      setUser(null);
      setLoading(false);
      return;
    }

    const fetchUser = async () => {
      try {
        const res = await axios.get(`${API_URL}/user/me/`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setUser(res.data);
      } catch (err) {
        console.error('Failed to fetch user info:', err);
        setUser(null);
      } finally {
        setLoading(false);
      }
    };

    fetchUser();
  }, [token]);

  const isStaff = user?.is_staff || false;
  const isAdmin = user?.is_superuser || false;
  const isCustomer = !isStaff && !isAdmin;

  return (
    <UserContext.Provider value={{ user, loading, isStaff, isAdmin, isCustomer }}>
      {children}
    </UserContext.Provider>
  );
};

const LoginScreen = ({ onLogin }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const submitAuth = async (e) => {
    e.preventDefault();
    try {
      const res = await axios.post(`${API_URL}/token/`, { username, password });
      localStorage.setItem('access_token', res.data.access);
      localStorage.setItem('refresh_token', res.data.refresh);
      onLogin(res.data.access);
    } catch {
      alert("Invalid credentials. Ensure backend is running and user exists.");
    }
  };

  return (
    <div className="glass-panel" style={{ width: '100%', maxWidth: '400px', margin: '0 auto' }}>
      <h2 style={{ textAlign: 'center', color: 'var(--accent-color)' }}>Authentication</h2>
      <form onSubmit={submitAuth} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        <input 
          className="glass-input" 
          placeholder="Username" 
          value={username} onChange={e => setUsername(e.target.value)} required 
        />
        <input 
          className="glass-input" 
          type="password"
          placeholder="Password" 
          value={password} onChange={e => setPassword(e.target.value)} required 
        />
        <button type="submit" className="glass-button">Login</button>
      </form>
    </div>
  );
};

const Toast = ({ toast, onClose }) => {
  if (!toast) return null;

  return (
    <div className={`toast ${toast.type}`} role="status" aria-live="polite">
      <span>{toast.message}</span>
      <button className="toast-close" onClick={onClose} aria-label="Close notification">x</button>
    </div>
  );
};

const TicketSkeleton = () => {
  return (
    <div className="skeleton-wrap">
      <div className="skeleton-line w-65" />
      <div className="skeleton-line w-90" />
      <div className="skeleton-line w-45" />
      <div className="skeleton-line w-80" />
    </div>
  );
};

const TicketDetailModal = ({ ticket, onClose, statuses, priorities, token, isStaff, isAdmin, onStatusChange, onAddComment }) => {
  const [newStatus, setNewStatus] = useState(ticket?.status?.id || '');
  const [commentText, setCommentText] = useState('');
  const [comments, setComments] = useState([]);
  const [loadingComments, setLoadingComments] = useState(true);

  useEffect(() => {
    if (!ticket) return;

    const fetchComments = async () => {
      try {
        const res = await axios.get(`${API_URL}/comments/?ticket=${ticket.id}`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        const allComments = Array.isArray(res.data?.results) ? res.data.results : res.data || [];
        // Filter by ticket_id in case backend query param doesn't work
        const ticketComments = allComments.filter(c => c.ticket === ticket.id);
        setComments(ticketComments);
      } catch (err) {
        console.error('Failed to load comments:', err);
        setComments([]);
      } finally {
        setLoadingComments(false);
      }
    };

    fetchComments();
  }, [ticket, token]);

  const handleStatusUpdate = async () => {
    if (!newStatus || !ticket) return;
    try {
      await axios.patch(`${API_URL}/tickets/${ticket.id}/`, {
        status_id: parseInt(newStatus)
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      onStatusChange();
    } catch (err) {
      console.error('Failed to update status:', err);
      alert('Could not update status');
    }
  };

  const handleAddComment = async (e) => {
    e.preventDefault();
    if (!commentText.trim() || !ticket) return;

    try {
      await axios.post(`${API_URL}/comments/`, {
        ticket: ticket.id,
        comment_text: commentText
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setCommentText('');
      onAddComment();
      // Refresh comments
      const res = await axios.get(`${API_URL}/comments/?ticket=${ticket.id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      const allComments = Array.isArray(res.data?.results) ? res.data.results : res.data || [];
      const ticketComments = allComments.filter(c => c.ticket === ticket.id);
      setComments(ticketComments);
    } catch (err) {
      console.error('Failed to add comment:', err);
      alert('Could not add comment');
    }
  };

  if (!ticket) return null;

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-card" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3>Ticket #{ticket.id}</h3>
          <button className="glass-button" onClick={onClose}>Close</button>
        </div>

        <div style={{ marginBottom: '1.5rem' }}>
          <p><strong>Title:</strong> {ticket.title}</p>
          <p><strong>Description:</strong> {ticket.description}</p>
          <p><strong>Customer:</strong> {ticket.customer?.username || 'Unknown'}</p>
          <p><strong>Created:</strong> {new Date(ticket.created_at).toLocaleString()}</p>
        </div>

        {/* Status Update Section - Only for Staff/Admin */}
        {(isStaff || isAdmin) && (
          <div style={{ marginBottom: '1.5rem', padding: '1rem', background: 'rgba(52, 211, 153, 0.1)', borderRadius: '0.5rem' }}>
            <h4 style={{ margin: '0 0 0.75rem 0' }}>Update Status</h4>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <select 
                className="glass-input" 
                value={newStatus} 
                onChange={(e) => setNewStatus(e.target.value)}
                style={{ flex: 1 }}
              >
                {statuses.map(status => (
                  <option key={status.id} value={status.id}>{status.name}</option>
                ))}
              </select>
              <button 
                className="glass-button" 
                onClick={handleStatusUpdate}
                style={{ background: 'rgba(52, 211, 153, 0.3)' }}
              >
                Update
              </button>
            </div>
            <p style={{ marginTop: '0.5rem', fontSize: '0.9rem', opacity: 0.7 }}>
              Current: <strong>{ticket.status?.name || 'Unknown'}</strong>
            </p>
          </div>
        )}

        {/* Comments Section */}
        <div style={{ marginBottom: '1.5rem' }}>
          <h4 style={{ margin: '0 0 1rem 0' }}>Comments ({comments.length})</h4>
          
          {loadingComments ? (
            <p style={{ opacity: 0.7 }}>Loading comments...</p>
          ) : (
            <>
              <div style={{ maxHeight: '300px', overflowY: 'auto', marginBottom: '1rem' }}>
                {comments.length === 0 ? (
                  <p style={{ opacity: 0.5 }}>No comments yet.</p>
                ) : (
                  comments.map(comment => (
                    <div 
                      key={comment.id} 
                      style={{ 
                        marginBottom: '1rem', 
                        padding: '0.75rem', 
                        background: 'rgba(255, 255, 255, 0.05)', 
                        borderRadius: '0.25rem',
                        borderLeft: '3px solid var(--accent-color)'
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <strong style={{ color: 'var(--accent-color)' }}>{comment.user?.username || 'Unknown'}</strong>
                        <span style={{ fontSize: '0.85rem', opacity: 0.6 }}>
                          {new Date(comment.created_at).toLocaleString()}
                        </span>
                      </div>
                      <p style={{ margin: '0.5rem 0 0 0' }}>{comment.comment_text}</p>
                    </div>
                  ))
                )}
              </div>

              {/* Add Comment Form - Only for Authenticated Users */}
              <form onSubmit={handleAddComment} style={{ display: 'flex', gap: '0.5rem' }}>
                <textarea 
                  className="glass-input"
                  placeholder="Add a comment..."
                  value={commentText}
                  onChange={(e) => setCommentText(e.target.value)}
                  rows="2"
                  style={{ flex: 1, resize: 'none' }}
                />
                <button 
                  type="submit" 
                  className="glass-button"
                  style={{ alignSelf: 'flex-start', background: 'rgba(52, 211, 153, 0.3)' }}
                >
                  Add
                </button>
              </form>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

const TicketWorkspace = ({ token, onLogout }) => {
  const { user, isStaff, isAdmin, isCustomer } = useUserRole();
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [tickets, setTickets] = useState([]);
  const [statuses, setStatuses] = useState([]);
  const [priorities, setPriorities] = useState([]);
  const [statusFilter, setStatusFilter] = useState('all');
  const [priorityFilter, setPriorityFilter] = useState('all');
  const [search, setSearch] = useState('');
  const [loadingTickets, setLoadingTickets] = useState(true);
  const [selectedTicket, setSelectedTicket] = useState(null);
  const [toast, setToast] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const loadLookup = async () => {
      try {
        const [statusRes, priorityRes] = await Promise.all([
          axios.get(`${API_URL}/statuses/`, { headers: { Authorization: `Bearer ${token}` } }),
          axios.get(`${API_URL}/priorities/`, { headers: { Authorization: `Bearer ${token}` } }),
        ]);
        const statusData = Array.isArray(statusRes.data?.results) ? statusRes.data.results : statusRes.data;
        const priorityData = Array.isArray(priorityRes.data?.results) ? priorityRes.data.results : priorityRes.data;
        setStatuses(statusData || []);
        setPriorities(priorityData || []);
      } catch {
        setStatuses([]);
        setPriorities([]);
      }
    };

    loadLookup();
  }, [token]);

  const fetchTickets = useCallback(async () => {
    setLoadingTickets(true);
    try {
      const res = await axios.get(`${API_URL}/tickets/`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      const data = Array.isArray(res.data?.results) ? res.data.results : res.data;
      setTickets(data || []);
    } catch {
      setToast({ type: 'error', message: 'Unable to load tickets right now.' });
    } finally {
      setLoadingTickets(false);
    }
  }, [token]);

  useEffect(() => {
    fetchTickets();
    const intervalId = setInterval(fetchTickets, 20000);
    return () => clearInterval(intervalId);
  }, [fetchTickets]);

  useEffect(() => {
    if (!toast) return;
    const timeoutId = setTimeout(() => setToast(null), 2600);
    return () => clearTimeout(timeoutId);
  }, [toast]);

  const filteredTickets = useMemo(() => {
    return tickets.filter((ticket) => {
      const matchesStatus = statusFilter === 'all' || String(ticket.status?.id) === statusFilter;
      const matchesPriority = priorityFilter === 'all' || String(ticket.priority?.id) === priorityFilter;
      const query = search.trim().toLowerCase();
      const matchesQuery =
        !query
        || ticket.title?.toLowerCase().includes(query)
        || ticket.description?.toLowerCase().includes(query);

      return matchesStatus && matchesPriority && matchesQuery;
    });
  }, [tickets, statusFilter, priorityFilter, search]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API_URL}/tickets/`, {
        title, 
        description,
        status_id: 1, // e.g. Open
        priority_id: 1 // e.g. Low
      }, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      setToast({ type: 'success', message: 'Ticket submitted successfully.' });
      setTitle('');
      setDescription('');
      fetchTickets();
    } catch {
      setToast({ type: 'error', message: 'Error submitting ticket.' });
    }
  };

  return (
    <div className="workspace-shell">
      <Toast toast={toast} onClose={() => setToast(null)} />
      <TicketDetailModal 
        ticket={selectedTicket} 
        onClose={() => setSelectedTicket(null)}
        statuses={statuses}
        priorities={priorities}
        token={token}
        isStaff={isStaff}
        isAdmin={isAdmin}
        onStatusChange={fetchTickets}
        onAddComment={fetchTickets}
      />
      <div className="glass-panel workspace-container">
        <div style={{ display:'flex', justifyContent: 'space-between', alignItems: 'center', gap: '1rem', flexWrap: 'wrap' }}>
          <h1 style={{ color: 'var(--accent-color)' }}>Nexus Support</h1>
          <div style={{ display: 'flex', gap: '1rem' }}>
            {(isStaff || isAdmin) && (
              <button className="glass-button" onClick={() => navigate('/admin')} style={{background: 'rgba(255,255,255,0.1)', color: 'var(--text-primary)', border: '1px solid var(--glass-border)'}}>
                {isAdmin ? 'Admin' : 'Staff'} Dashboard
              </button>
            )}
            <button className="glass-button" onClick={fetchTickets}>Refresh</button>
            <button className="glass-button" onClick={onLogout} style={{background: 'var(--text-secondary)'}}>Logout</button>
          </div>
        </div>
        <p style={{ opacity: 0.8, marginBottom: '2rem' }}>intelligent ticket routing & resolution</p>

        <div className="workspace-grid">
          <form onSubmit={handleSubmit} className="ticket-form">
            <h3 style={{ marginTop: 0 }}>New Ticket</h3>
            <input className="glass-input" placeholder="Issue Title" value={title} onChange={e => setTitle(e.target.value)} required />
            <textarea className="glass-input" rows="5" placeholder="Description in detail..." value={description} onChange={e => setDescription(e.target.value)} required />
            <button type="submit" className="glass-button">Submit Ticket</button>
          </form>

          <section className="ticket-list-wrap">
            <div className="ticket-filter-row">
              <input
                className="glass-input"
                placeholder="Search title or description"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
              <select className="glass-input" value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
                <option value="all">All status</option>
                {statuses.map((status) => (
                  <option key={status.id} value={String(status.id)}>{status.name}</option>
                ))}
              </select>
              <select className="glass-input" value={priorityFilter} onChange={(e) => setPriorityFilter(e.target.value)}>
                <option value="all">All priority</option>
                {priorities.map((priority) => (
                  <option key={priority.id} value={String(priority.id)}>{priority.name}</option>
                ))}
              </select>
            </div>

            {loadingTickets ? (
              <TicketSkeleton />
            ) : (
              <div className="ticket-list">
                {filteredTickets.length === 0 ? (
                  <p className="muted">No matching tickets found.</p>
                ) : (
                  filteredTickets.map((ticket) => (
                    <button key={ticket.id} className="ticket-item" onClick={() => setSelectedTicket(ticket)}>
                      <div>
                        <p className="ticket-title">#{ticket.id} {ticket.title}</p>
                        <p className="ticket-meta">{ticket.status?.name || 'Unknown'} • {ticket.priority?.name || 'Unknown'}</p>
                      </div>
                      <span className="ticket-date">{new Date(ticket.created_at).toLocaleDateString()}</span>
                    </button>
                  ))
                )}
              </div>
            )}
          </section>
        </div>
      </div>
    </div>
  );
};

// Protected Admin Route - checks role before rendering
const ProtectedAdminRoute = ({ token, onLogout }) => {
  const { isAdmin, isStaff, loading } = useUserRole();

  if (loading) {
    return <div style={{ color: 'white', textAlign: 'center', marginTop: '2rem' }}>Loading...</div>;
  }

  if (!isAdmin && !isStaff) {
    return <Navigate to="/" />;
  }

  return <AdminDashboard token={token} onLogout={onLogout} />;
};

function App() {
  const [token, setToken] = useState(() => {
    const saved = localStorage.getItem('access_token');
    if (saved) {
      try {
        const decoded = jwtDecode(saved);
        if (decoded.exp * 1000 > Date.now()) return saved;
      } catch {
        // ignore decoding errors
      }
    }
    return null;
  });

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setToken(null);
  }

  return (
    <BrowserRouter>
      <UserProvider token={token}>
        <Routes>
          <Route path="/login" element={token ? <Navigate to="/" /> : <LoginScreen onLogin={setToken} />} />
          <Route path="/" element={token ? <TicketWorkspace token={token} onLogout={handleLogout} /> : <Navigate to="/login" />} />
          <Route path="/admin" element={token ? <ProtectedAdminRoute token={token} onLogout={handleLogout} /> : <Navigate to="/login" />} />
        </Routes>
      </UserProvider>
    </BrowserRouter>
  );
}

export default App;
