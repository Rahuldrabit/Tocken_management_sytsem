import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const TicketDetailView = ({ ticket, onClose, token, statuses, onStatusChange }) => {
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
        // Filter by ticket_id
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
      onClose();
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
      onStatusChange();
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

  return (
    <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0, 0, 0, 0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }} onClick={onClose}>
      <div style={{ background: 'var(--bg-secondary)', borderRadius: '1rem', padding: '2rem', maxWidth: '600px', width: '90%', maxHeight: '90vh', overflowY: 'auto', color: 'var(--text-primary)' }} onClick={(e) => e.stopPropagation()}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
          <h2 style={{ margin: 0, color: 'var(--accent-color)' }}>Ticket #{ticket.id}</h2>
          <button onClick={onClose} style={{ background: 'none', border: 'none', color: 'var(--text-primary)', fontSize: '1.5rem', cursor: 'pointer' }}>×</button>
        </div>

        <div style={{ marginBottom: '1.5rem' }}>
          <p><strong>Title:</strong> {ticket.title}</p>
          <p><strong>Customer:</strong> {ticket.customer?.username || 'Unknown'}</p>
          <p><strong>Description:</strong> {ticket.description}</p>
          <p><strong>Priority:</strong> <span style={{ color: ticket.priority?.level > 3 ? '#ff6b6b' : '#1dd1a1' }}>{ticket.priority?.name || 'Unknown'}</span></p>
          <p><strong>Created:</strong> {new Date(ticket.created_at).toLocaleString()}</p>
        </div>

        {/* Status Update Section */}
        <div style={{ marginBottom: '1.5rem', padding: '1rem', background: 'rgba(52, 211, 153, 0.1)', borderRadius: '0.5rem' }}>
          <h4 style={{ margin: '0 0 0.75rem 0' }}>Update Status</h4>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <select 
              value={newStatus} 
              onChange={(e) => setNewStatus(e.target.value)}
              style={{ flex: 1, padding: '0.5rem', borderRadius: '0.25rem', background: 'rgba(255, 255, 255, 0.1)', color: 'var(--text-primary)', border: '1px solid var(--glass-border)' }}
            >
              {statuses.map(status => (
                <option key={status.id} value={status.id}>{status.name}</option>
              ))}
            </select>
            <button 
              onClick={handleStatusUpdate}
              style={{ padding: '0.5rem 1rem', borderRadius: '0.25rem', background: 'rgba(52, 211, 153, 0.3)', border: 'none', color: 'var(--text-primary)', cursor: 'pointer' }}
            >
              Update
            </button>
          </div>
          <p style={{ marginTop: '0.5rem', fontSize: '0.9rem', opacity: 0.7 }}>
            Current: <strong>{ticket.status?.name || 'Unknown'}</strong>
          </p>
        </div>

        {/* Comments Section */}
        <div>
          <h4 style={{ margin: '0 0 1rem 0' }}>Comments ({comments.length})</h4>
          
          {loadingComments ? (
            <p style={{ opacity: 0.7 }}>Loading comments...</p>
          ) : (
            <>
              <div style={{ maxHeight: '250px', overflowY: 'auto', marginBottom: '1rem' }}>
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

              {/* Add Comment Form */}
              <form onSubmit={handleAddComment} style={{ display: 'flex', gap: '0.5rem' }}>
                <textarea 
                  placeholder="Add a comment..."
                  value={commentText}
                  onChange={(e) => setCommentText(e.target.value)}
                  rows="2"
                  style={{ flex: 1, padding: '0.5rem', borderRadius: '0.25rem', background: 'rgba(255, 255, 255, 0.1)', color: 'var(--text-primary)', border: '1px solid var(--glass-border)', resize: 'none', fontFamily: 'inherit' }}
                />
                <button 
                  type="submit" 
                  style={{ alignSelf: 'flex-start', padding: '0.5rem 1rem', borderRadius: '0.25rem', background: 'rgba(52, 211, 153, 0.3)', border: 'none', color: 'var(--text-primary)', cursor: 'pointer' }}
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

const AdminDashboard = ({ token, onLogout }) => {
  const [stats, setStats] = useState(null);
  const [tickets, setTickets] = useState([]);
  const [selectedTicket, setSelectedTicket] = useState(null);
  const [statuses, setStatuses] = useState([]);
  const [loadingTickets, setLoadingTickets] = useState(true);
  const [statusFilter, setStatusFilter] = useState('all');
  const [search, setSearch] = useState('');
  const navigate = useNavigate();

  const fetchAllData = async () => {
    try {
      const [statsRes, ticketsRes, statusesRes] = await Promise.all([
        axios.get(`${API_URL}/admin-stats/`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        axios.get(`${API_URL}/tickets/`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        axios.get(`${API_URL}/statuses/`, {
          headers: { Authorization: `Bearer ${token}` }
        })
      ]);

      setStats(statsRes.data);
      const ticketData = Array.isArray(ticketsRes.data?.results) ? ticketsRes.data.results : ticketsRes.data;
      setTickets(ticketData || []);
      const statusData = Array.isArray(statusesRes.data?.results) ? statusesRes.data.results : statusesRes.data;
      setStatuses(statusData || []);
    } catch (err) {
      if(err.response?.status === 403) {
        alert('You do not have Administrator access.');
        navigate('/');
      } else {
        console.error("Failed to load dashboard data", err);
      }
    } finally {
      setLoadingTickets(false);
    }
  };

  useEffect(() => {
    fetchAllData();
  }, [token, navigate]);

  const filteredTickets = tickets.filter(ticket => {
    const matchesStatus = statusFilter === 'all' || String(ticket.status?.id) === statusFilter;
    const matchesSearch = !search.trim() || 
      ticket.title?.toLowerCase().includes(search.toLowerCase()) ||
      ticket.id.toString().includes(search);
    return matchesStatus && matchesSearch;
  });

  if (!stats) return <div style={{ color: 'white', textAlign: 'center', marginTop: '2rem'}}>Loading Admin Dashboard...</div>;

  return (
    <div style={{ padding: '2rem', width: '100%', maxWidth: '1400px', margin: '0 auto', color: 'var(--text-primary)' }}>
      {selectedTicket && (
        <TicketDetailView 
          ticket={selectedTicket} 
          onClose={() => setSelectedTicket(null)}
          token={token}
          statuses={statuses}
          onStatusChange={fetchAllData}
        />
      )}

      <div style={{ display:'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <h1 style={{ color: 'var(--accent-color)' }}>Nexus Staff Console</h1>
        <div style={{ display: 'flex', gap: '1rem'}}>
          <button className="glass-button" onClick={() => navigate('/')}>Support Portal</button>
          <button className="glass-button" onClick={fetchAllData}>Refresh</button>
          <button className="glass-button" onClick={onLogout} style={{background: 'var(--text-secondary)'}}>Logout</button>
        </div>
      </div>

      {/* Metrics Row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1.5rem', marginBottom: '2.5rem' }}>
        <div className="glass-panel" style={{ textAlign: 'center' }}>
          <h3 style={{ margin: 0, opacity: 0.8 }}>Total Tickets</h3>
          <p style={{ fontSize: '2.5rem', fontWeight: 'bold', margin: '0.5rem 0 0 0', color: 'var(--accent-color)' }}>{stats.metrics.total_tickets}</p>
        </div>
        <div className="glass-panel" style={{ textAlign: 'center' }}>
          <h3 style={{ margin: 0, opacity: 0.8 }}>Escalations</h3>
          <p style={{ fontSize: '2.5rem', fontWeight: 'bold', margin: '0.5rem 0 0 0', color: '#ff6b6b' }}>{stats.metrics.escalated_tickets}</p>
        </div>
        <div className="glass-panel" style={{ textAlign: 'center' }}>
          <h3 style={{ margin: 0, opacity: 0.8 }}>Open Tickets</h3>
          <p style={{ fontSize: '2.5rem', fontWeight: 'bold', margin: '0.5rem 0 0 0', color: '#feca57' }}>{stats.metrics.open_tickets}</p>
        </div>
        <div className="glass-panel" style={{ textAlign: 'center' }}>
          <h3 style={{ margin: 0, opacity: 0.8 }}>Resolved</h3>
          <p style={{ fontSize: '2.5rem', fontWeight: 'bold', margin: '0.5rem 0 0 0', color: '#1dd1a1' }}>{stats.metrics.resolved_tickets}</p>
        </div>
      </div>

      {/* Ticket Management Section */}
      <h2 style={{ marginBottom: '1rem' }}>All Tickets ({filteredTickets.length})</h2>
      <div className="glass-panel" style={{ padding: '1.5rem' }}>
        {/* Filter Controls */}
        <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem' }}>
          <input
            type="text"
            placeholder="Search by title or ID..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="glass-input"
            style={{ flex: 1 }}
          />
          <select 
            value={statusFilter} 
            onChange={(e) => setStatusFilter(e.target.value)}
            className="glass-input"
          >
            <option value="all">All Status</option>
            {statuses.map(status => (
              <option key={status.id} value={status.id}>{status.name}</option>
            ))}
          </select>
        </div>

        {/* Tickets List */}
        {loadingTickets ? (
          <p>Loading tickets...</p>
        ) : (
          <div style={{ maxHeight: '600px', overflowY: 'auto' }}>
            {filteredTickets.length === 0 ? (
              <p style={{ opacity: 0.5, textAlign: 'center' }}>No matching tickets found.</p>
            ) : (
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                <thead style={{ position: 'sticky', top: 0, background: 'var(--bg-secondary)' }}>
                  <tr style={{ borderBottom: '1px solid var(--glass-border)' }}>
                    <th style={{ padding: '1rem' }}>ID</th>
                    <th style={{ padding: '1rem' }}>Title</th>
                    <th style={{ padding: '1rem' }}>Customer</th>
                    <th style={{ padding: '1rem' }}>Status</th>
                    <th style={{ padding: '1rem' }}>Priority</th>
                    <th style={{ padding: '1rem' }}>Created</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredTickets.map(ticket => (
                    <tr 
                      key={ticket.id} 
                      onClick={() => setSelectedTicket(ticket)}
                      style={{ 
                        borderBottom: '1px solid rgba(255,255,255,0.05)',
                        cursor: 'pointer',
                        transition: 'background 0.2s',
                        background: 'transparent'
                      }}
                      onMouseOver={(e) => e.currentTarget.style.background = 'rgba(52, 211, 153, 0.05)'}
                      onMouseOut={(e) => e.currentTarget.style.background = 'transparent'}
                    >
                      <td style={{ padding: '1rem', fontWeight: 'bold' }}>#{ticket.id}</td>
                      <td style={{ padding: '1rem', color: 'var(--accent-color)' }}>{ticket.title}</td>
                      <td style={{ padding: '1rem' }}>{ticket.customer?.username || 'Unknown'}</td>
                      <td style={{ padding: '1rem' }}>
                        <span style={{ 
                          background: ticket.status?.id === 1 ? 'rgba(254, 202, 87, 0.2)' : ticket.status?.id === 3 ? 'rgba(29, 209, 161, 0.2)' : 'rgba(255, 107, 107, 0.2)',
                          color: ticket.status?.id === 1 ? '#feca57' : ticket.status?.id === 3 ? '#1dd1a1' : '#ff6b6b',
                          padding: '0.25rem 0.75rem', borderRadius: '1rem', fontSize: '0.85rem', fontWeight: 'bold'
                        }}>
                          {ticket.status?.name || 'Unknown'}
                        </span>
                      </td>
                      <td style={{ padding: '1rem' }}>
                        <span style={{ 
                          background: ticket.priority?.level > 3 ? 'rgba(255, 107, 107, 0.2)' : 'rgba(29, 209, 161, 0.2)', 
                          color: ticket.priority?.level > 3 ? '#ff6b6b' : '#1dd1a1',
                          padding: '0.25rem 0.75rem', borderRadius: '1rem', fontSize: '0.85rem', fontWeight: 'bold'
                        }}>
                          {ticket.priority?.name || 'Standard'}
                        </span>
                      </td>
                      <td style={{ padding: '1rem', fontSize: '0.9rem' }}>{new Date(ticket.created_at).toLocaleDateString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminDashboard;
