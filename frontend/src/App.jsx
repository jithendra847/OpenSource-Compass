import { useEffect, useMemo, useState } from 'react'
import {
  Compass, Search, Bookmark, TrendingUp, Settings,
  Bell, Plus, X, ChevronDown, ArrowUpRight,
  Sparkles, Code2, SlidersHorizontal, Menu,
  LayoutDashboard, ExternalLink, Clock,
  CheckCircle2, Circle, Target, Zap, BookOpen,
  Filter, RefreshCw, Sun, Moon, Command,
  AlertCircle, Loader2, ArrowRight, Brain,
  Layers, Activity, ChevronRight, Star,
  PanelRightClose, Lightbulb, ListChecks,
  Check, CircleDot, Globe, Terminal
} from 'lucide-react'

import './App.css'

const DEFAULT_API = 'http://127.0.0.1:8000'

const INITIAL_SKILLS = ['Python', 'JavaScript', 'React', 'FastAPI']

const LANGUAGES = [
  'All languages', 'Python', 'JavaScript', 'TypeScript',
  'Java', 'C++', 'Go', 'Rust', 'C#'
]

const NAV_ITEMS = [
  { id: 'discover', label: 'Discover', icon: Compass },
  { id: 'saved', label: 'Saved issues', icon: Bookmark },
  { id: 'growth', label: 'Skill growth', icon: TrendingUp },
  { id: 'settings', label: 'Settings', icon: Settings }
]

const DEMO_ISSUES = [
  {
    id: 101,
    title: 'Improve API error handling and validation',
    repository: 'fastapi / fastapi',
    language: 'Python',
    difficulty: 'Beginner',
    match_percentage: 92,
    fit_score: 92,
    hybrid_score: 0.92,
    matched_skills: ['Python', 'FastAPI'],
    missing_skills: ['Pytest'],
    labels: ['good first issue', 'enhancement'],
    body: 'Improve error handling and request validation across API endpoints.',
    summary: 'Improve the consistency of API error responses and validation.',
    html_url: 'https://github.com/tiangolo/fastapi/issues',
    created_at: 'Recently opened'
  },
  {
    id: 102,
    title: 'Add reusable components to the documentation',
    repository: 'facebook / react',
    language: 'JavaScript',
    difficulty: 'Beginner',
    match_percentage: 86,
    fit_score: 86,
    hybrid_score: 0.86,
    matched_skills: ['JavaScript', 'React'],
    missing_skills: ['TypeScript'],
    labels: ['documentation', 'help wanted'],
    body: 'Improve documentation with practical reusable component examples.',
    summary: 'Add examples explaining reusable React component patterns.',
    html_url: 'https://github.com/facebook/react/issues',
    created_at: 'Recently opened'
  },
  {
    id: 103,
    title: 'Improve frontend loading states',
    repository: 'vercel / next.js',
    language: 'JavaScript',
    difficulty: 'Intermediate',
    match_percentage: 78,
    fit_score: 78,
    hybrid_score: 0.78,
    matched_skills: ['JavaScript', 'React'],
    missing_skills: ['Next.js', 'TypeScript'],
    labels: ['enhancement'],
    body: 'Improve loading and error states in frontend components.',
    summary: 'Enhance loading state handling and user feedback.',
    html_url: 'https://github.com/vercel/next.js/issues',
    created_at: 'Recently opened'
  }
]

const readStorage = (key, fallback) => {
  try {
    const value = localStorage.getItem(key)
    return value ? JSON.parse(value) : fallback
  } catch {
    return fallback
  }
}

function normalizeIssue(issue, index = 0) {
  const repoUrl = issue.repository_url || ''
  const repository = issue.repository ||
    issue.repo_name ||
    issue.repository_name ||
    repoUrl.split('/').slice(-2).join(' / ') ||
    'GitHub repository'

  const rawScore =
    issue.match_percentage ??
    issue.match_score ??
    issue.fit_score ??
    issue.hybrid_score ??
    0

  const score = Number(rawScore)
  const percentage = score <= 1 && score > 0
    ? Math.round(score * 100)
    : Math.round(score)

  return {
    ...issue,
    id: issue.id ?? issue.number ?? index,
    title: issue.title || 'Untitled issue',
    repository,
    language: issue.language || 'Other',
    difficulty: issue.difficulty || issue.complexity || 'Unclassified',
    match_percentage: Math.min(100, Math.max(0, percentage)),
    matched_skills: issue.matched_skills || issue.matched || [],
    missing_skills: issue.missing_skills || issue.missing || [],
    labels: Array.isArray(issue.labels)
      ? issue.labels.map(label =>
          typeof label === 'string' ? label : label.name
        )
      : [],
    body: issue.body || '',
    summary: issue.summary || issue.explanation || '',
    html_url: issue.html_url || issue.url || '#',
    created_at: issue.created_at || ''
  }
}

function App() {
  const [activePage, setActivePage] = useState('discover')
  const [skills, setSkills] = useState(() =>
    readStorage('osc-skills', INITIAL_SKILLS)
  )
  const [savedIssues, setSavedIssues] = useState(() =>
    readStorage('osc-saved-issues', [])
  )
  const [pipeline, setPipeline] = useState(() =>
    readStorage('osc-pipeline', {})
  )
  const [issues, setIssues] = useState([])
  const [selectedIssue, setSelectedIssue] = useState(null)
  const [analysis, setAnalysis] = useState(null)

  const [search, setSearch] = useState('')
  const [skillInput, setSkillInput] = useState('')
  const [language, setLanguage] = useState('All languages')
  const [label, setLabel] = useState('')
  const [difficulty, setDifficulty] = useState('All levels')
  const [sortBy, setSortBy] = useState('match')
  const [resultCount, setResultCount] = useState(20)

  const [loading, setLoading] = useState(false)
  const [analyzing, setAnalyzing] = useState(false)
  const [error, setError] = useState('')
  const [hasSearched, setHasSearched] = useState(false)
  const [mobileMenu, setMobileMenu] = useState(false)
  const [darkMode, setDarkMode] = useState(() =>
    readStorage('osc-dark-mode', false)
  )
  const [showFilters, setShowFilters] = useState(false)
  const [apiUrl, setApiUrl] = useState(() =>
    localStorage.getItem('osc-api-url') || DEFAULT_API
  )
  const [notifications, setNotifications] = useState(true)

  useEffect(() => {
    localStorage.setItem('osc-skills', JSON.stringify(skills))
  }, [skills])

  useEffect(() => {
    localStorage.setItem('osc-saved-issues', JSON.stringify(savedIssues))
  }, [savedIssues])

  useEffect(() => {
    localStorage.setItem('osc-pipeline', JSON.stringify(pipeline))
  }, [pipeline])

  useEffect(() => {
    localStorage.setItem('osc-dark-mode', JSON.stringify(darkMode))
    document.documentElement.dataset.theme = darkMode ? 'dark' : 'light'
  }, [darkMode])

  const fetchRecommendations = async () => {
    if (!skills.length) {
      setError('Add at least one skill before discovering issues.')
      return
    }

    setLoading(true)
    setError('')
    setHasSearched(true)

    try {
      const response = await fetch(`${apiUrl.replace(/\/$/, '')}/recommendations`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          skills,
          language: language === 'All languages' ? 'python' : language.toLowerCase(),
          label: label || null,
          count: Number(resultCount),
          min_score: 1
        })
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || data.message || 'Could not fetch recommendations.')
      }

      const results = Array.isArray(data)
        ? data
        : data.recommendations || data.issues || data.results || []

      setIssues(results.map(normalizeIssue))
    } catch (err) {
      setError(err.message || 'Something went wrong while fetching issues.')
      setIssues([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchRecommendations()
    // Initial discovery only. Filters are applied when the user searches.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const addSkill = () => {
    const value = skillInput.trim()
    if (!value) return

    const exists = skills.some(
      skill => skill.toLowerCase() === value.toLowerCase()
    )

    if (!exists) setSkills(previous => [...previous, value])
    setSkillInput('')
  }

  const removeSkill = (skill) => {
    setSkills(previous => previous.filter(item => item !== skill))
  }

  const toggleSave = (issue) => {
    const exists = savedIssues.some(item => item.id === issue.id)

    setSavedIssues(previous =>
      exists
        ? previous.filter(item => item.id !== issue.id)
        : [...previous, issue]
    )
  }

  const isSaved = (issue) =>
    savedIssues.some(item => item.id === issue.id)

  const updatePipeline = (issueId, status) => {
    setPipeline(previous => ({
      ...previous,
      [issueId]: status
    }))
  }

  const openAnalysis = async (issue) => {
  console.log('Repository:', issue.repository)
  console.log('Issue number:', issue.issue_number)
  console.log('Full issue:', issue)
    setSelectedIssue(issue)
    setAnalysis(null)
    setAnalyzing(true)

    try {
      const response = await fetch(`${apiUrl.replace(/\/$/, '')}/analyze-issue`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
        title: issue.title,
        body: issue.body || '',
        labels: issue.labels || [],
        user_skills: skills,
        repository: issue.repository,
        issue_number: issue.issue_number
      })
})
        

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || data.message || 'Analysis failed.')
      }

      setAnalysis(data)
    } catch (err) {
      setAnalysis({
        error: err.message,
        summary: issue.summary || issue.body || 'No summary available.',
        matched_skills: issue.matched_skills,
        missing_skills: issue.missing_skills,
        preparation_steps: []
      })
    } finally {
      setAnalyzing(false)
    }
  }

  const visibleIssues = useMemo(() => {
    let result = activePage === 'saved' ? savedIssues : issues

    const query = search.toLowerCase().trim()

    if (query) {
      result = result.filter(issue =>
        `${issue.title} ${issue.repository} ${issue.language} ${issue.labels?.join(' ')}`
          .toLowerCase()
          .includes(query)
      )
    }

    if (difficulty !== 'All levels') {
      result = result.filter(issue =>
        issue.difficulty?.toLowerCase() === difficulty.toLowerCase()
      )
    }

    if (activePage === 'saved') {
      return [...result]
    }

    return [...result].sort((a, b) => {
      if (sortBy === 'match') {
        return b.match_percentage - a.match_percentage
      }
      if (sortBy === 'title') {
        return a.title.localeCompare(b.title)
      }
      return 0
    })
  }, [issues, savedIssues, activePage, search, difficulty, sortBy])

  const stats = useMemo(() => ({
    discovered: issues.length,
    saved: savedIssues.length,
    beginner: issues.filter(i =>
      i.difficulty?.toLowerCase() === 'beginner'
    ).length,
    average: issues.length
      ? Math.round(
          issues.reduce((sum, issue) => sum + issue.match_percentage, 0) /
          issues.length
        )
      : 0
  }), [issues, savedIssues])

  const pageTitle = {
    discover: 'Find your next contribution.',
    saved: 'Your contribution shortlist.',
    growth: 'Grow through contribution.',
    settings: 'Make Compass yours.'
  }[activePage]

  const pageSubtitle = {
    discover: 'Meaningful open-source issues, matched to what you know.',
    saved: 'Keep track of the issues worth your time.',
    growth: 'Turn real-world issues into a practical learning path.',
    settings: 'Configure your workspace and preferences.'
  }[activePage]

  return (
    <div className={`app-shell ${darkMode ? 'dark' : ''}`}>

      {mobileMenu && (
        <button
          className="mobile-overlay"
          onClick={() => setMobileMenu(false)}
          aria-label="Close navigation"
        />
      )}

      <aside className={`sidebar ${mobileMenu ? 'sidebar-open' : ''}`}>
        <div className="brand">
          <div className="brand-mark">
            <Compass size={25} strokeWidth={1.8} />
          </div>
          <div>
            <div className="brand-name">OpenSource</div>
            <div className="brand-subtitle">COMPASS</div>
          </div>
          <button
            className="icon-button mobile-close"
            onClick={() => setMobileMenu(false)}
          >
            <X size={19} />
          </button>
        </div>

        <div className="workspace-label">WORKSPACE</div>

        <nav className="nav-list">
          {NAV_ITEMS.map(item => {
            const Icon = item.icon
            return (
              <button
                key={item.id}
                className={`nav-item ${activePage === item.id ? 'active' : ''}`}
                onClick={() => {
                  setActivePage(item.id)
                  setMobileMenu(false)
                  setSelectedIssue(null)
                }}
              >
                <Icon size={19} />
                <span>{item.label}</span>
                {item.id === 'saved' && savedIssues.length > 0 && (
                  <span className="nav-count">{savedIssues.length}</span>
                )}
              </button>
            )
          })}
        </nav>

        <div className="sidebar-bottom">
          <div className="sidebar-tip">
            <div className="tip-icon"><Lightbulb size={17} /></div>
            <div className="tip-title">Small steps. Real impact.</div>
            <p>Every contribution makes the open-source ecosystem stronger.</p>
          </div>

          <div className="profile">
            <div className="avatar">JD</div>
            <div className="profile-info">
              <strong>Developer workspace</strong>
              <span>Personal account</span>
            </div>
            <button
              className="icon-button"
              onClick={() => setActivePage('settings')}
              aria-label="Workspace settings"
            >
              <Settings size={17} />
            </button>
          </div>
        </div>
      </aside>

      <main className="main-area">
        <header className="topbar">
          <div className="topbar-left">
            <button
              className="icon-button mobile-menu-button"
              onClick={() => setMobileMenu(true)}
              aria-label="Open navigation"
            >
              <Menu size={21} />
            </button>
            <div className="breadcrumb">
              <span>Workspace</span>
              <ChevronRight size={14} />
              <strong>{NAV_ITEMS.find(i => i.id === activePage)?.label}</strong>
            </div>
          </div>

          <div className="topbar-actions">
            <div className="connection-status">
              <span className="status-dot" />
              <span>Compass workspace</span>
            </div>
            <button
              className="icon-button"
              onClick={() => setDarkMode(!darkMode)}
              aria-label="Toggle theme"
              title="Toggle theme"
            >
              {darkMode ? <Sun size={18} /> : <Moon size={18} />}
            </button>
            <button
              className="icon-button notification-button"
              onClick={() => setNotifications(!notifications)}
              title="Toggle notifications"
            >
              <Bell size={18} />
              {notifications && <span className="notification-dot" />}
            </button>
          </div>
        </header>

        <div className="page-content">
          <section className="page-heading">
            <div>
              <div className="eyebrow">
                <Sparkles size={14} />
                YOUR OPEN-SOURCE JOURNEY
              </div>
              <h1>{pageTitle}</h1>
              <p>{pageSubtitle}</p>
            </div>
            {activePage === 'discover' && (
              <button
                className="primary-button"
                onClick={fetchRecommendations}
                disabled={loading}
              >
                {loading
                  ? <Loader2 className="spin" size={17} />
                  : <RefreshCw size={16} />}
                Refresh issues
              </button>
            )}
          </section>

          {activePage === 'discover' && (
            <>
              <section className="stats-grid">
                <StatCard
                  icon={Layers}
                  label="Issues discovered"
                  value={stats.discovered}
                  detail="Matching your profile"
                />
                <StatCard
                  icon={Bookmark}
                  label="Saved issues"
                  value={stats.saved}
                  detail="In your shortlist"
                />
                <StatCard
                  icon={Target}
                  label="Beginner friendly"
                  value={stats.beginner}
                  detail="Potential starting points"
                />
                <StatCard
                  icon={TrendingUp}
                  label="Average skill match"
                  value={`${stats.average}%`}
                  detail="Across discovered issues"
                />
              </section>

              <section className="discovery-panel">
                <div className="section-heading">
                  <div>
                    <h2>Build your developer profile</h2>
                    <p>Tell Compass what you already know.</p>
                  </div>
                  <span className="section-icon"><Code2 size={19} /></span>
                </div>

                <div className="skill-input-row">
                  <div className="skill-input-wrap">
                    <Plus size={17} />
                    <input
                      value={skillInput}
                      onChange={e => setSkillInput(e.target.value)}
                      onKeyDown={e => e.key === 'Enter' && addSkill()}
                      placeholder="Add a skill (e.g. Python, React, SQL)"
                    />
                  </div>
                  <button className="secondary-button" onClick={addSkill}>
                    Add skill
                  </button>
                </div>

                <div className="skill-list">
                  {skills.map(skill => (
                    <span className="skill-chip" key={skill}>
                      <Check size={13} />
                      {skill}
                      <button
                        onClick={() => removeSkill(skill)}
                        aria-label={`Remove ${skill}`}
                      >
                        <X size={13} />
                      </button>
                    </span>
                  ))}
                  {!skills.length && (
                    <span className="empty-inline">No skills added yet.</span>
                  )}
                </div>
              </section>

              <section className="filter-section">
                <div className="filter-main">
                  <div className="search-box">
                    <Search size={18} />
                    <input
                      value={search}
                      onChange={e => setSearch(e.target.value)}
                      placeholder="Search issues, repositories, technologies..."
                    />
                    <kbd>⌘ K</kbd>
                  </div>

                  <button
                    className={`filter-button ${showFilters ? 'selected' : ''}`}
                    onClick={() => setShowFilters(!showFilters)}
                  >
                    <SlidersHorizontal size={17} />
                    Filters
                    <ChevronDown size={15} />
                  </button>
                </div>

                {showFilters && (
                  <div className="filter-options">
                    <label>
                      <span>Language</span>
                      <select
                        value={language}
                        onChange={e => setLanguage(e.target.value)}
                      >
                        {LANGUAGES.map(item => (
                          <option key={item}>{item}</option>
                        ))}
                      </select>
                    </label>

                    <label>
                      <span>Issue label</span>
                      <select
                        value={label}
                        onChange={e => setLabel(e.target.value)}
                      >
                        <option value="">Any label</option>
                        <option value="good first issue">Good first issue</option>
                        <option value="help wanted">Help wanted</option>
                        <option value="bug">Bug</option>
                        <option value="documentation">Documentation</option>
                      </select>
                    </label>

                    <label>
                      <span>Difficulty</span>
                      <select
                        value={difficulty}
                        onChange={e => setDifficulty(e.target.value)}
                      >
                        <option>All levels</option>
                        <option>Beginner</option>
                        <option>Intermediate</option>
                        <option>Advanced</option>
                      </select>
                    </label>

                    <label>
                      <span>Results</span>
                      <select
                        value={resultCount}
                        onChange={e => setResultCount(Number(e.target.value))}
                      >
                        <option value={10}>10 issues</option>
                        <option value={20}>20 issues</option>
                        <option value={30}>30 issues</option>
                        <option value={50}>50 issues</option>
                      </select>
                    </label>

                    <button
                      className="primary-button filter-apply"
                      onClick={() => {
                        setShowFilters(false)
                        fetchRecommendations()
                      }}
                    >
                      Apply filters <ArrowRight size={15} />
                    </button>
                  </div>
                )}
              </section>

              <section className="results-section">
                <div className="results-header">
                  <div>
                    <h2>Recommended for you</h2>
                    <p>
                      {visibleIssues.length} opportunities based on your skills
                    </p>
                  </div>
                  <label className="sort-control">
                    <span>Sort by</span>
                    <select
                      value={sortBy}
                      onChange={e => setSortBy(e.target.value)}
                    >
                      <option value="match">Best match</option>
                      <option value="title">Title</option>
                    </select>
                  </label>
                </div>

                {error && (
                  <div className="error-banner">
                    <AlertCircle size={18} />
                    <span>{error}</span>
                    <button onClick={fetchRecommendations}>Retry</button>
                  </div>
                )}

                {loading ? (
                  <div className="loading-state">
                    <div className="loading-icon">
                      <Compass size={29} className="spin" />
                    </div>
                    <h3>Finding your next contribution</h3>
                    <p>Matching GitHub issues against your developer profile...</p>
                  </div>
                ) : visibleIssues.length ? (
                  <div className="issues-grid">
                    {visibleIssues.map(issue => (
                      <IssueCard
                        key={issue.id}
                        issue={issue}
                        saved={isSaved(issue)}
                        onSave={() => toggleSave(issue)}
                        onAnalyze={() => openAnalysis(issue)}
                      />
                    ))}
                  </div>
                ) : (
                  <EmptyState
                    icon={Search}
                    title={hasSearched ? 'No matching issues found' : 'Ready to explore?'}
                    description={
                      hasSearched
                        ? 'Try changing your search or filters, or add more skills.'
                        : 'Search for opportunities that match your skills.'
                    }
                    action="Discover issues"
                    onAction={() => {
                      setSearch('')
                      setDifficulty('All levels')
                      fetchRecommendations()
                    }}
                  />
                )}
              </section>
            </>
          )}

          {activePage === 'saved' && (
            <section className="results-section standalone-section">
              <div className="results-header">
                <div>
                  <h2>Your saved opportunities</h2>
                  <p>{savedIssues.length} issues in your shortlist</p>
                </div>
              </div>

              <div className="search-box saved-search">
                <Search size={18} />
                <input
                  value={search}
                  onChange={e => setSearch(e.target.value)}
                  placeholder="Search your saved issues..."
                />
              </div>

              {visibleIssues.length ? (
                <div className="issues-grid">
                  {visibleIssues.map(issue => (
                    <IssueCard
                      key={issue.id}
                      issue={issue}
                      saved
                      onSave={() => toggleSave(issue)}
                      onAnalyze={() => openAnalysis(issue)}
                      pipeline={pipeline[issue.id] || 'Saved'}
                      onPipelineChange={status =>
                        updatePipeline(issue.id, status)
                      }
                    />
                  ))}
                </div>
              ) : (
                <EmptyState
                  icon={Bookmark}
                  title="Your shortlist is waiting"
                  description="Save interesting issues from Discover to build your contribution shortlist."
                  action="Explore issues"
                  onAction={() => {
                    setActivePage('discover')
                    setSearch('')
                  }}
                />
              )}
            </section>
          )}

          {activePage === 'growth' && (
            <SkillGrowth
              skills={skills}
              issues={issues}
              savedIssues={savedIssues}
              pipeline={pipeline}
              onDiscover={() => setActivePage('discover')}
            />
          )}

          {activePage === 'settings' && (
            <SettingsPage
              apiUrl={apiUrl}
              setApiUrl={setApiUrl}
              darkMode={darkMode}
              setDarkMode={setDarkMode}
              notifications={notifications}
              setNotifications={setNotifications}
              skills={skills}
              setSkills={setSkills}
              onSave={() => {
                localStorage.setItem('osc-api-url', apiUrl)
                alert('Settings saved successfully.')
              }}
            />
          )}
        </div>

        <footer className="app-footer">
          <div><Compass size={15} /> OpenSource Compass</div>
          <span>Navigate open source. One issue at a time.</span>
          <span>Built for contributors <span className="footer-heart">♥</span></span>
        </footer>
      </main>

      {selectedIssue && (
        <div className="drawer-backdrop" onClick={() => setSelectedIssue(null)}>
          <aside className="analysis-drawer" onClick={e => e.stopPropagation()}>
            <div className="drawer-header">
              <div className="drawer-title">
                <span className="drawer-icon"><Brain size={19} /></span>
                <div>
                  <strong>Issue intelligence</strong>
                  <span>AI-assisted analysis</span>
                </div>
              </div>
              <button
                className="icon-button"
                onClick={() => setSelectedIssue(null)}
              >
                <X size={20} />
              </button>
            </div>

            <div className="drawer-content">
              <div className="drawer-eyebrow">ANALYZING OPPORTUNITY</div>
              <h2>{selectedIssue.title}</h2>
              <a
                href={selectedIssue.html_url}
                target="_blank"
                rel="noreferrer"
                className="repo-link"
              >
                <Code2 size={15} />
                {selectedIssue.repository}
                <ExternalLink size={13} />
              </a>

              <div className="drawer-score">
                <div className="score-circle">
                  <strong>{selectedIssue.match_percentage}%</strong>
                  <span>Match</span>
                </div>
                <div>
                  <strong>Your skill compatibility</strong>
                  <p>Based on your developer profile and issue requirements.</p>
                </div>
              </div>

              {analyzing ? (
                <div className="analysis-loading">
                  <Loader2 size={25} className="spin" />
                  <strong>Analyzing this issue...</strong>
                  <p>Examining requirements, skills and preparation steps.</p>
                </div>
              ) : (
                <>
                  {analysis?.error && (
                    <div className="error-banner">
                      <AlertCircle size={16} />
                      AI analysis unavailable. Showing available issue information.
                    </div>
                  )}

                  <AnalysisSection
                    icon={Sparkles}
                    title="Issue overview"
                  >
                    <p>{analysis?.summary || selectedIssue.summary || selectedIssue.body || 'No issue description available.'}</p>
                  </AnalysisSection>

                  <AnalysisSection
                    icon={CheckCircle2}
                    title="Skills you already have"
                  >
                    <div className="drawer-tags">
                      {(analysis?.matched_skills || selectedIssue.matched_skills || [])
                        .map((skill, i) => (
                          <span className="success-tag" key={i}>
                            <Check size={12} /> {skill}
                          </span>
                        ))}
                      {!((analysis?.matched_skills || selectedIssue.matched_skills || []).length) &&
                        <span className="muted-text">No matched skills returned.</span>}
                    </div>
                  </AnalysisSection>

                  <AnalysisSection
                    icon={Target}
                    title="Skills to strengthen"
                  >
                    <div className="drawer-tags">
                      {(analysis?.missing_skills || selectedIssue.missing_skills || [])
                        .map((skill, i) => (
                          <span className="warning-tag" key={i}>{skill}</span>
                        ))}
                      {!((analysis?.missing_skills || selectedIssue.missing_skills || []).length) &&
                        <span className="muted-text">No skill gaps identified.</span>}
                    </div>
                  </AnalysisSection>

                  <AnalysisSection
                    icon={ListChecks}
                    title="Preparation roadmap"
                  >
                    <PreparationSteps analysis={analysis} issue={selectedIssue} />
                  </AnalysisSection>
                  <RepositoryContributionGuide
                    analysis={analysis?.repository_analysis}
                  />

                  <div className="drawer-actions">
                    <button
                      className="primary-button"
                      onClick={() => toggleSave(selectedIssue)}
                    >
                      <Bookmark size={16} />
                      {isSaved(selectedIssue) ? 'Remove from saved' : 'Save this issue'}
                    </button>
                    <a
                      className="secondary-button"
                      href={selectedIssue.html_url}
                      target="_blank"
                      rel="noreferrer"
                    >
                      Open on GitHub <ArrowUpRight size={15} />
                    </a>
                  </div>
                </>
              )}
            </div>
          </aside>
        </div>
      )}
    </div>
  )
}

function StatCard({ icon: Icon, label, value, detail }) {
  return (
    <div className="stat-card">
      <div className="stat-top">
        <span>{label}</span>
        <div className="stat-icon"><Icon size={18} /></div>
      </div>
      <strong className="stat-value">{value}</strong>
      <span className="stat-detail">{detail}</span>
    </div>
  )
}

function IssueCard({
  issue, saved, onSave, onAnalyze,
  pipeline, onPipelineChange
}) {
  const difficultyClass = issue.difficulty?.toLowerCase() || 'unknown'

  return (
    <article className="issue-card">
      <div className="issue-card-top">
        <div className="repository-label">
          <Code2 size={15} />
          {issue.repository}
        </div>
        <button
          className={`save-button ${saved ? 'is-saved' : ''}`}
          onClick={onSave}
          title={saved ? 'Remove bookmark' : 'Save issue'}
        >
          <Bookmark size={18} fill={saved ? 'currentColor' : 'none'} />
        </button>
      </div>

      <h3>{issue.title}</h3>

      <div className="issue-meta">
        <span className={`difficulty-badge ${difficultyClass}`}>
          <span className="badge-dot" />
          {issue.difficulty}
        </span>
        <span className="language-badge">
          <Code2 size={13} /> {issue.language}
        </span>
      </div>

      <p className="issue-summary">
        {issue.summary || issue.body || 'Explore this GitHub issue to understand its requirements.'}
      </p>

      <div className="match-block">
        <div className="match-label">
          <span>Skill compatibility</span>
          <strong>{issue.match_percentage}%</strong>
        </div>
        <div className="match-track">
          <div
            className="match-fill"
            style={{ width: `${issue.match_percentage}%` }}
          />
        </div>
      </div>

      <div className="issue-skills">
        <span className="skills-heading">MATCHED SKILLS</span>
        <div className="drawer-tags">
          {(issue.matched_skills || []).slice(0, 4).map((skill, i) => (
            <span className="success-tag" key={i}>{skill}</span>
          ))}
          {!issue.matched_skills?.length && (
            <span className="muted-text">No skill details</span>
          )}
        </div>
      </div>

      {issue.missing_skills?.length > 0 && (
        <div className="missing-skills">
          <span>TO EXPLORE</span>
          {issue.missing_skills.slice(0, 3).join(' · ')}
        </div>
      )}

      {issue.labels?.length > 0 && (
        <div className="issue-labels">
          {issue.labels.slice(0, 3).map((item, i) => (
            <span key={i}>{item}</span>
          ))}
        </div>
      )}

      <div className="issue-card-footer">
        {pipeline && (
          <select
            className="pipeline-select"
            value={pipeline}
            onChange={e => onPipelineChange(e.target.value)}
          >
            <option>Saved</option>
            <option>Preparing</option>
            <option>Ready</option>
            <option>Attempted</option>
          </select>
        )}
        <button className="analyze-button" onClick={onAnalyze}>
          Analyze issue <ArrowUpRight size={15} />
        </button>
      </div>
    </article>
  )
}

function EmptyState({ icon: Icon, title, description, action, onAction }) {
  return (
    <div className="empty-state">
      <div className="empty-icon"><Icon size={28} /></div>
      <h3>{title}</h3>
      <p>{description}</p>
      <button className="secondary-button" onClick={onAction}>
        {action} <ArrowRight size={15} />
      </button>
    </div>
  )
}

function AnalysisSection({ icon: Icon, title, children }) {
  return (
    <section className="analysis-section">
      <h3><Icon size={17} /> {title}</h3>
      {children}
    </section>
  )
}

function PreparationSteps({ analysis, issue }) {
  const steps =
    analysis?.preparation_steps ||
    analysis?.roadmap ||
    analysis?.steps ||
    analysis?.recommendations ||
    []

  if (Array.isArray(steps) && steps.length) {
    return (
      <ol className="preparation-list">
        {steps.map((step, index) => (
          <li key={index}>
            <span className="step-number">{index + 1}</span>
            <span>{typeof step === 'string' ? step : step.title || step.description || JSON.stringify(step)}</span>
          </li>
        ))}
      </ol>
    )
  }

  return (
    <ol className="preparation-list">
      <li><span className="step-number">1</span><span>Read the complete issue description and understand the expected outcome.</span></li>
      <li><span className="step-number">2</span><span>Explore the repository structure and locate the relevant files.</span></li>
      <li><span className="step-number">3</span><span>Review existing tests and reproduce the reported behavior.</span></li>
      <li><span className="step-number">4</span><span>Implement a focused solution and run the relevant tests.</span></li>
      <li><span className="step-number">5</span><span>Submit a pull request following the repository contribution guidelines.</span></li>
    </ol>
  )
}


function RepositoryContributionGuide({ analysis }) {
  if (!analysis) return null

  return (
    <div className="repository-guide">
      <div className="repository-guide-heading">
        <span className="repository-guide-label">
          REPOSITORY INTELLIGENCE
        </span>
        <h3>Contribution guide</h3>
        <p>
          Understand the codebase, investigate the issue,
          and plan your implementation.
        </p>
      </div>

      {analysis.repository_summary && (
        <AnalysisSection
          icon={BookOpen}
          title="Repository overview"
        >
          <p>{analysis.repository_summary}</p>
        </AnalysisSection>
      )}

      {analysis.issue_interpretation && (
        <AnalysisSection
          icon={Lightbulb}
          title="What this issue means"
        >
          <p>{analysis.issue_interpretation}</p>
        </AnalysisSection>
      )}

      {analysis.relevant_files?.length > 0 && (
        <AnalysisSection
          icon={Code2}
          title="Relevant source files"
        >
          <div className="repository-files">
            {analysis.relevant_files.map((file, index) => (
              <div className="repository-file" key={`${file.path}-${index}`}>
                <div className="repository-file-path">
                  <Code2 size={14} />
                  <code>{file.path}</code>
                </div>

                <p>{file.purpose}</p>

                {file.evidence && (
                  <pre className="repository-evidence">
                    <code>{file.evidence}</code>
                  </pre>
                )}
              </div>
            ))}
          </div>
        </AnalysisSection>
      )}

      {analysis.investigation_notes?.length > 0 && (
        <AnalysisSection
          icon={Search}
          title="Investigation findings"
        >
          <ul className="repository-bullet-list">
            {analysis.investigation_notes.map((note, index) => (
              <li key={index}>{note}</li>
            ))}
          </ul>
        </AnalysisSection>
      )}

      {analysis.implementation_steps?.length > 0 && (
        <AnalysisSection
          icon={ListChecks}
          title="Implementation plan"
        >
          <ol className="preparation-list">
            {analysis.implementation_steps.map((step, index) => (
              <li key={index}>
                <span className="step-number">
                  {step.step ?? index + 1}
                </span>

                <div className="repository-step-content">
                  {step.file_path && (
                    <code className="repository-step-path">
                      {step.file_path}
                    </code>
                  )}

                  <p>{step.instruction}</p>

                  {step.reason && (
                    <span className="repository-step-reason">
                      Why: {step.reason}
                    </span>
                  )}
                </div>
              </li>
            ))}
          </ol>
        </AnalysisSection>
      )}

      {analysis.testing_strategy?.length > 0 && (
        <AnalysisSection
          icon={Terminal}
          title="Testing strategy"
        >
          <ul className="repository-bullet-list">
            {analysis.testing_strategy.map((test, index) => (
              <li key={index}>{test}</li>
            ))}
          </ul>
        </AnalysisSection>
      )}

      {analysis.uncertainty_notes?.length > 0 && (
        <AnalysisSection
          icon={AlertCircle}
          title="Things to verify"
        >
          <ul className="repository-bullet-list">
            {analysis.uncertainty_notes.map((note, index) => (
              <li key={index}>{note}</li>
            ))}
          </ul>
        </AnalysisSection>
      )}
    </div>
  )
}


function SkillGrowth({ skills, issues, savedIssues, pipeline, onDiscover }) {
  const stages = ['Saved', 'Preparing', 'Ready', 'Attempted']

  const stageCounts = stages.map(stage => ({
    name: stage,
    count: savedIssues.filter(
      issue => (pipeline[issue.id] || 'Saved') === stage
    ).length
  }))

  const gaps = [...new Set(
    issues.flatMap(issue => issue.missing_skills || [])
  )]

  return (
    <div className="growth-page">
      <section className="growth-hero">
        <div>
          <div className="eyebrow"><TrendingUp size={14} /> CONTRIBUTOR DEVELOPMENT</div>
          <h2>Your progress starts with practice.</h2>
          <p>Build experience by working on real issues, not just tutorials.</p>
        </div>
        <div className="growth-illustration"><Target size={48} /></div>
      </section>

      <div className="growth-grid">
        <div className="growth-card">
          <span className="card-overline">YOUR CURRENT TOOLKIT</span>
          <strong className="growth-number">{skills.length}</strong>
          <p>Skills in your developer profile</p>
          <div className="skill-list growth-skills">
            {skills.map(skill => (
              <span className="skill-chip" key={skill}>{skill}</span>
            ))}
          </div>
        </div>

        <div className="growth-card">
          <span className="card-overline">CONTRIBUTION PIPELINE</span>
          <strong className="growth-number">{savedIssues.length}</strong>
          <p>Issues you're tracking</p>
          <div className="pipeline-stages">
            {stageCounts.map(stage => (
              <div className="pipeline-stage" key={stage.name}>
                <span>{stage.name}</span>
                <strong>{stage.count}</strong>
              </div>
            ))}
          </div>
        </div>
      </div>

      <section className="growth-card gap-card">
        <div className="section-heading">
          <div>
            <h2>Skills worth exploring</h2>
            <p>Skills appearing in the issues recommended to you.</p>
          </div>
          <Lightbulb size={20} />
        </div>
        <div className="skill-list">
          {gaps.length ? gaps.map(skill => (
            <span className="warning-tag" key={skill}>{skill}</span>
          )) : <p className="muted-text">Discover issues to identify new learning opportunities.</p>}
        </div>
      </section>

      <button className="primary-button" onClick={onDiscover}>
        Find opportunities <ArrowRight size={16} />
      </button>
    </div>
  )
}

function SettingsPage({
  apiUrl, setApiUrl, darkMode, setDarkMode,
  notifications, setNotifications, skills, setSkills, onSave
}) {
  const [newSkill, setNewSkill] = useState('')

  return (
    <div className="settings-page">
      <section className="settings-card">
        <div className="section-heading">
          <div>
            <h2>Backend connection</h2>
            <p>Connect Compass to your local FastAPI service.</p>
          </div>
          <Terminal size={20} />
        </div>

        <label className="settings-field">
          <span>API base URL</span>
          <input
            value={apiUrl}
            onChange={e => setApiUrl(e.target.value)}
            placeholder="http://127.0.0.1:8000"
          />
        </label>
        <p className="field-hint">Default: http://127.0.0.1:8000</p>
      </section>

      <section className="settings-card">
        <div className="section-heading">
          <div>
            <h2>Appearance</h2>
            <p>Choose the workspace appearance.</p>
          </div>
          <Sun size={20} />
        </div>
        <div className="setting-row">
          <div>
            <strong>Dark mode</strong>
            <p>Use a darker interface for your workspace.</p>
          </div>
          <button
            className={`toggle ${darkMode ? 'toggle-on' : ''}`}
            onClick={() => setDarkMode(!darkMode)}
            aria-label="Toggle dark mode"
          >
            <span />
          </button>
        </div>
      </section>

      <section className="settings-card">
        <div className="section-heading">
          <div>
            <h2>Notifications</h2>
            <p>Control workspace notification indicators.</p>
          </div>
          <Bell size={20} />
        </div>
        <div className="setting-row">
          <div>
            <strong>Enable notifications</strong>
            <p>Show notification indicators in the workspace.</p>
          </div>
          <button
            className={`toggle ${notifications ? 'toggle-on' : ''}`}
            onClick={() => setNotifications(!notifications)}
            aria-label="Toggle notifications"
          >
            <span />
          </button>
        </div>
      </section>

      <section className="settings-card">
        <div className="section-heading">
          <div>
            <h2>Developer profile</h2>
            <p>Manage the skills used by the recommendation engine.</p>
          </div>
          <Code2 size={20} />
        </div>

        <div className="skill-input-row">
          <div className="skill-input-wrap">
            <Plus size={17} />
            <input
              value={newSkill}
              onChange={e => setNewSkill(e.target.value)}
              onKeyDown={e => {
                if (e.key === 'Enter' && newSkill.trim()) {
                  setSkills(previous => [...new Set([...previous, newSkill.trim()])])
                  setNewSkill('')
                }
              }}
              placeholder="Add a skill"
            />
          </div>
          <button
            className="secondary-button"
            onClick={() => {
              if (!newSkill.trim()) return
              setSkills(previous => [...new Set([...previous, newSkill.trim()])])
              setNewSkill('')
            }}
          >
            Add
          </button>
        </div>

        <div className="skill-list">
          {skills.map(skill => (
            <span className="skill-chip" key={skill}>
              {skill}
              <button onClick={() => setSkills(previous =>
                previous.filter(item => item !== skill)
              )}>
                <X size={13} />
              </button>
            </span>
          ))}
        </div>
      </section>

      <div className="settings-save">
        <button className="primary-button" onClick={onSave}>
          <Check size={16} /> Save settings
        </button>
      </div>
    </div>
  )
}

export default App
