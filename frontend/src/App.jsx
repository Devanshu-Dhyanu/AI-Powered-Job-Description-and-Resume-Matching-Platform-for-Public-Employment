import { useEffect, useState } from 'react';

const sampleProfile = `I am a Java and Python developer with experience building web applications. I know React, MySQL, and REST APIs. I completed a project where I built a real-time chat application using Java and React with MySQL database.`;

function App() {
  const [candidateText, setCandidateText] = useState(sampleProfile);
  const [matches, setMatches] = useState([]);
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(false);
  const [parsedProfile, setParsedProfile] = useState(null);
  const [resumeFileName, setResumeFileName] = useState('');

  useEffect(() => {
    fetchDashboard();
  }, []);

  const fetchDashboard = async () => {
    const response = await fetch('http://localhost:8000/api/dashboard');
    const data = await response.json();
    setDashboard(data);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    const response = await fetch('http://localhost:8000/api/match', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ candidate_text: candidateText }),
    });
    const data = await response.json();
    setMatches(data.matches);
    if (data.matches.length > 0) {
      setParsedProfile(data.matches[0].parsed_profile);
    }
    setLoading(false);
  };

  const handleResumeUpload = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);
    setLoading(true);
    setResumeFileName(file.name);

    const response = await fetch('http://localhost:8000/api/resume/upload', {
      method: 'POST',
      body: formData,
    });
    const data = await response.json();

    if (data.extracted_text) {
      setCandidateText(data.extracted_text);
    }
    if (data.parsed_profile) {
      setParsedProfile(data.parsed_profile);
    }
    if (data.matches) {
      setMatches(data.matches);
    }
    setLoading(false);
  };

  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">Public Employment</p>
          <h1>AI Job Recommendation System</h1>
        </div>
      </header>

      <main className="content-grid">
        <section className="panel form-panel">
          <h2>Resume / Candidate Profile</h2>
          <form onSubmit={handleSubmit}>
            <div className="upload-row">
              <label className="file-upload">
                <input type="file" accept=".txt,.pdf,.docx" onChange={handleResumeUpload} />
                <span>Upload Resume</span>
              </label>
              {resumeFileName && <span className="file-name">{resumeFileName}</span>}
            </div>
            <textarea
              value={candidateText}
              onChange={(event) => setCandidateText(event.target.value)}
              rows={10}
              placeholder="Describe your skills, projects, experience, and role preference..."
            />
            <button type="submit" disabled={loading}>
              {loading ? 'Matching...' : 'Find Best Jobs'}
            </button>
          </form>
        </section>

        <section className="panel stats-panel">
          <h2>Employment Office Dashboard</h2>
          {dashboard ? (
            <>
              <div className="stat-grid">
                <div><span>Total Job Seekers</span><strong>{dashboard.total_job_seekers.toLocaleString()}</strong></div>
                <div><span>Active Jobs</span><strong>{dashboard.active_jobs.toLocaleString()}</strong></div>
                <div><span>Applications</span><strong>{dashboard.applications.toLocaleString()}</strong></div>
                <div><span>Avg Match Score</span><strong>{dashboard.average_match_score}%</strong></div>
              </div>

              <div className="chart-block">
                <h3>Top Skills</h3>
                {Object.entries(dashboard.top_skills).map(([skill, value]) => (
                  <div key={skill} className="bar-row">
                    <label>{skill}</label>
                    <div className="bar-track">
                      <div className="bar-fill" style={{ width: `${value}%` }} />
                    </div>
                    <span>{value}%</span>
                  </div>
                ))}
              </div>
            </>
          ) : (
            <p>Loading dashboard...</p>
          )}
        </section>
      </main>

      {parsedProfile && (
        <section className="panel extracted-panel">
          <h2>Extracted Candidate Profile</h2>
          <div className="profile-grid">
            <div>
              <h4>Skills</h4>
              <div className="tags">
                {parsedProfile.skills.map((skill) => <span key={skill} className="tag success">{skill}</span>)}
              </div>
            </div>
            <div>
              <h4>Experience</h4>
              <div className="tags">
                {parsedProfile.experience.length ? parsedProfile.experience.map((item) => <span key={item} className="tag neutral">{item}</span>) : <span className="muted">No explicit experience field</span>}
              </div>
            </div>
            <div>
              <h4>Role Preference</h4>
              <div className="tags">
                {parsedProfile.role.length ? parsedProfile.role.map((item) => <span key={item} className="tag blue">{item}</span>) : <span className="muted">Not specified</span>}
              </div>
            </div>
          </div>
        </section>
      )}

      <section className="panel results-panel">
        <h2>Recommended Jobs</h2>
        {matches.length === 0 ? (
          <p>Submit a profile to see ranked matches.</p>
        ) : (
          <div className="jobs-list">
            {matches.map((job) => (
              <article key={job.job_id} className="job-card">
                <div className="job-header">
                  <div>
                    <h3>{job.title}</h3>
                    <p>{job.company} • {job.location}</p>
                  </div>
                  <div className="score-pill">{job.match_score}%</div>
                </div>

                <div className="metric-row">
                  <span>Skill Match</span>
                  <strong>{job.skill_match}%</strong>
                </div>
                <div className="metric-row">
                  <span>Semantic Similarity</span>
                  <strong>{job.semantic_similarity}%</strong>
                </div>
                <div className="metric-row">
                  <span>Experience Match</span>
                  <strong>{job.experience_score}%</strong>
                </div>
                <div className="metric-row">
                  <span>Role Match</span>
                  <strong>{job.role_match_score}%</strong>
                </div>

                <div className="skill-box">
                  <h4>Matched Skills</h4>
                  <div className="tags">
                    {job.matched_skills.length ? job.matched_skills.map((skill) => (
                      <span key={skill} className="tag success">{skill}</span>
                    )) : <span className="muted">None</span>}
                  </div>
                </div>

                <div className="skill-box">
                  <h4>Missing Skills</h4>
                  <div className="tags">
                    {job.missing_skills.length ? job.missing_skills.map((skill) => (
                      <span key={skill} className="tag warning">{skill}</span>
                    )) : <span className="muted">No major gaps</span>}
                  </div>
                </div>
              </article>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

export default App;
