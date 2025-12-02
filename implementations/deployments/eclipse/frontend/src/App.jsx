import { useState, useEffect, useRef } from 'react'
import './App.css'

function App() {
  const [author, setAuthor] = useState('')
  const [videos, setVideos] = useState([])
  const [loading, setLoading] = useState(false)
  const [selectedVideos, setSelectedVideos] = useState(new Set())
  const [downloading, setDownloading] = useState(false)
  const [progress, setProgress] = useState(null)
  const [stats, setStats] = useState(null)
  const [limit, setLimit] = useState(20)
  const [previewVideo, setPreviewVideo] = useState(null)
  const [completedDownloads, setCompletedDownloads] = useState({}) // Map of video URL to download URL
  const [failedDownloads, setFailedDownloads] = useState(new Set()) // Set of failed video URLs
  const wsRef = useRef(null)

  // Environment variables for API URLs
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
  // Derive WebSocket URL from API URL (http -> ws, https -> wss)
  const WS_URL = API_URL.replace(/^http/, 'ws').replace(/\/$/, '') + '/ws/download';

  const fetchVideos = async (searchLimit) => {
    setLoading(true)
    try {
      const response = await fetch(`${API_URL}/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ author, limit: searchLimit })
      })
      const data = await response.json()
      if (data.videos) {
        setVideos(data.videos)
        setStats(data.stats)
      }
    } catch (error) {
      console.error("Search failed", error)
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = async (e) => {
    e.preventDefault()
    if (!author) return

    setVideos([])
    setStats(null)
    setSelectedVideos(new Set())
    setLimit(20)
    await fetchVideos(20)
  }

  const handleLoadMore = () => {
    const newLimit = limit + 20
    setLimit(newLimit)
    fetchVideos(newLimit)
  }

  const toggleSelection = (url) => {
    const newSelection = new Set(selectedVideos)
    if (newSelection.has(url)) {
      newSelection.delete(url)
    } else {
      newSelection.add(url)
    }
    setSelectedVideos(newSelection)
  }

  const selectAll = () => {
    if (selectedVideos.size === videos.length) {
      setSelectedVideos(new Set())
    } else {
      setSelectedVideos(new Set(videos.map(v => v.url)))
    }
  }

  const startDownload = () => {
    if (selectedVideos.size === 0) return

    setDownloading(true)
    setProgress({ current: 0, total: selectedVideos.size, status: 'Starting...' })

    wsRef.current = new WebSocket(WS_URL)

    wsRef.current.onopen = () => {
      wsRef.current.send(JSON.stringify({
        author: author,
        urls: Array.from(selectedVideos)
      }))
    }

    wsRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data)
      if (data.type === 'progress') {
        setProgress({
          current: data.current_index,
          total: data.total,
          status: data.status === 'downloading' ? 'Downloading...' : 'Finished',
          video: data.video_url
        })

        if (data.status === 'finished') {
          if (data.download_url) {
            setCompletedDownloads(prev => ({
              ...prev,
              [data.video_url]: `${API_URL}${data.download_url}`
            }))
          } else {
            setFailedDownloads(prev => {
              const newSet = new Set(prev)
              newSet.add(data.video_url)
              return newSet
            })
          }
        }
      } else if (data.type === 'complete') {
        setDownloading(false)
        wsRef.current.close()
        alert('All downloads complete!')
      } else if (data.type === 'cancelled') {
        setDownloading(false)
        wsRef.current.close()
        alert('Download stopped by user.')
        setProgress(null)
      }
    }
  }

  const handleStop = () => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send('stop')
    }
  }



  const openPreview = (e, url) => {
    e.stopPropagation()
    let videoId = null
    if (url.includes('v=')) {
      videoId = url.split('v=')[1].split('&')[0]
    } else if (url.includes('youtu.be/')) {
      videoId = url.split('youtu.be/')[1]
    }

    if (videoId) {
      setPreviewVideo(videoId)
    } else {
      window.open(url, '_blank')
    }
  }

  const closePreview = () => {
    setPreviewVideo(null)
  }

  return (
    <div className="app-container">
      {!stats ? (
        <div className="landing-hero">
          <div className="landing-content">
            <img src="/eclipse_logo.png" alt="Eclipse" className="app-logo" />
            <h1>Unlimited Archiving. Your Favorite Authors.</h1>
            <p>Save videos forever. Watch anywhere. Cancel anytime.</p>
            <form onSubmit={handleSearch} className="search-form">
              <input
                type="text"
                placeholder="Enter creator name or channel URL..."
                value={author}
                onChange={(e) => setAuthor(e.target.value)}
              />
              <button type="submit" disabled={loading} className="primary-btn">
                {loading ? 'SEARCHING...' : 'ARCHIVE >'}
              </button>
            </form>
          </div>
        </div>
      ) : (
        <>
          <div className="hero-section" style={{
            backgroundImage: videos.length > 0 ? `linear-gradient(to bottom, rgba(0,0,0,0.3), #141414), url(${videos[0].thumbnail})` : 'none'
          }}>
            <div className="hero-overlay"></div>
            <div className="hero-content">
              <h1>{stats.author_name}</h1>
              <div className="hero-stats">
                <span>{stats.video_count} Videos</span>
                <span className="dot">•</span>
                <span>{stats.total_views.toLocaleString()} Total Views</span>
              </div>
              <div className="hero-actions">
                <button onClick={selectAll} className="hero-btn secondary">
                  {selectedVideos.size === videos.length ? 'Deselect All' : 'Select All'}
                </button>
                <button
                  onClick={startDownload}
                  disabled={selectedVideos.size === 0 || downloading}
                  className="hero-btn primary"
                >
                  {downloading ? 'Downloading...' : `Download Selected (${selectedVideos.size})`}
                </button>
                {downloading && (
                  <button onClick={handleStop} className="hero-btn danger">Stop</button>
                )}
              </div>
            </div>
          </div>

          <div className="content-section">
            {downloading && progress && (
              <div className="progress-bar-container">
                <div className="progress-info">
                  <span>{progress.status} ({progress.current}/{progress.total})</span>
                </div>
                <div className="progress-track">
                  <div
                    className="progress-fill"
                    style={{ width: `${(progress.current / progress.total) * 100}%` }}
                  ></div>
                </div>
              </div>
            )}

            <div className="masonry-grid">
              {videos.map((video) => (
                <div
                  key={video.id}
                  className={`video-card ${selectedVideos.has(video.url) ? 'selected' : ''}`}
                  onClick={() => toggleSelection(video.url)}
                >
                  <div className="thumbnail">
                    {video.thumbnail ? (
                      <img src={video.thumbnail} alt={video.title} referrerPolicy="no-referrer" />
                    ) : (
                      <div className="placeholder"></div>
                    )}
                    <div className="overlay">
                      <button
                        className="play-btn"
                        onClick={(e) => openPreview(e, video.url)}
                      >
                        <svg viewBox="4 4 16 16" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                          <path d="M8 5V19L19 12L8 5Z" />
                        </svg>
                      </button>
                      <div className="checkbox-ring">
                        {selectedVideos.has(video.url) && <div className="checkbox-fill"></div>}
                      </div>
                    </div>
                    <span className="duration-badge">
                      {(() => {
                        const seconds = video.duration
                        if (!seconds) return '0:00'
                        const h = Math.floor(seconds / 3600)
                        const m = Math.floor((seconds % 3600) / 60)
                        const s = seconds % 60
                        if (h > 0) {
                          return `${h}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
                        }
                        return `${m}:${s.toString().padStart(2, '0')}`
                      })()}
                    </span>
                  </div>
                  <div className="info">
                    <h3>{video.title}</h3>
                    <div className="meta">
                      <span>{video.view_count ? `${(video.view_count / 1000).toFixed(1)}K views` : 'N/A'}</span>
                    </div>
                    {completedDownloads[video.url] && (
                      <a
                        href={completedDownloads[video.url]}
                        download
                        className="save-btn"
                        onClick={(e) => e.stopPropagation()}
                        target="_blank"
                        rel="noopener noreferrer"
                        style={{
                          display: 'block',
                          marginTop: '0.5rem',
                          padding: '0.5rem',
                          background: '#E50914',
                          color: 'white',
                          textAlign: 'center',
                          borderRadius: '4px',
                          textDecoration: 'none',
                          fontWeight: 'bold',
                          fontSize: '0.9rem'
                        }}
                      >
                        Save to Device
                      </a>
                    )}
                    {failedDownloads.has(video.url) && (
                      <div style={{
                        marginTop: '0.5rem',
                        padding: '0.5rem',
                        background: 'rgba(229, 9, 20, 0.2)',
                        border: '1px solid #E50914',
                        color: '#ff6b6b',
                        textAlign: 'center',
                        borderRadius: '4px',
                        fontSize: '0.9rem'
                      }}>
                        Download Failed
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>

            <div className="load-more-container">
              <button
                onClick={handleLoadMore}
                disabled={loading}
                className="secondary-btn load-more-btn"
              >
                {loading ? 'Loading...' : 'Show More'}
              </button>
            </div>
          </div>
        </>
      )}

      {previewVideo && (
        <div className="modal-overlay" onClick={closePreview}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <button className="close-btn" onClick={closePreview}>×</button>
            <div className="video-wrapper">
              <iframe
                src={`https://www.youtube.com/embed/${previewVideo}?autoplay=1`}
                title="YouTube video player"
                frameBorder="0"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
              ></iframe>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default App
