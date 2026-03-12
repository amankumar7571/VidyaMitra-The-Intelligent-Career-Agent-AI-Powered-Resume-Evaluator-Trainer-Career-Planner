import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { User, BookOpen, GraduationCap, Save, LogOut, UploadCloud, FileText, CheckCircle2, TrendingUp, Cpu, Map as MapIcon, Compass } from 'lucide-react';

export default function Dashboard() {
  const [user, setUser] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({ cgpa: '', interests: '' });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  
  // Profile messages
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  // Resume upload states
  const fileInputRef = useRef(null);
  const [uploadingResume, setUploadingResume] = useState(false);
  const [resumeError, setResumeError] = useState('');
  const [resumeSuccess, setResumeSuccess] = useState('');
  const [parsedTextPreview, setParsedTextPreview] = useState('');
  const [extractedSkills, setExtractedSkills] = useState([]);

  // Prediction stats
  const [predicting, setPredicting] = useState(false);
  const [predictionResult, setPredictionResult] = useState(null);
  
  // Roadmap stats
  const [generatingRoadmap, setGeneratingRoadmap] = useState(false);
  const [roadmap, setRoadmap] = useState(null);

  const navigate = useNavigate();

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        navigate('/login');
        return;
      }
      const response = await axios.get('/api/auth/me', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setUser(response.data);
      setFormData({
        cgpa: response.data.cgpa || '',
        interests: response.data.interests || ''
      });
    } catch (err) {
      if (err.response?.status === 401) {
        localStorage.removeItem('token');
        navigate('/login');
      }
      setError('Failed to load profile');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateProfile = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setSaving(true);
    try {
      const token = localStorage.getItem('token');
      const payload = {
        cgpa: formData.cgpa ? parseFloat(formData.cgpa) : null,
        interests: formData.interests || null,
      };
      const response = await axios.put('/api/profile/update', payload, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setUser(response.data);
      setSuccess('Profile updated successfully!');
      setIsEditing(false);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to update profile');
    } finally {
      setSaving(false);
    }
  };

  const handleResumeUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.name.endsWith('.pdf') && !file.name.endsWith('.docx')) {
      setResumeError('Please upload a PDF or DOCX file.');
      return;
    }

    setResumeError('');
    setResumeSuccess('');
    setUploadingResume(true);
    setParsedTextPreview('');
    setExtractedSkills([]);
    setPredictionResult(null);
    setRoadmap(null);

    const token = localStorage.getItem('token');
    const uploadForm = new FormData();
    uploadForm.append('file', file);

    try {
      const response = await axios.post('/api/resume/upload', uploadForm, {
        headers: { 
          Authorization: `Bearer ${token}`,
          'Content-Type': 'multipart/form-data'
        }
      });
      setResumeSuccess(response.data.message);
      setParsedTextPreview(response.data.parsed_text_preview);
      setExtractedSkills(response.data.extracted_skills || []);
    } catch (err) {
      setResumeError(err.response?.data?.detail || 'Failed to upload resume.');
    } finally {
      setUploadingResume(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const handlePredictCareer = async () => {
    if (extractedSkills.length === 0) return;
    setPredicting(true);
    setRoadmap(null);
    try {
      const token = localStorage.getItem('token');
      // POST the skills to the predictions endpoint
      const response = await axios.post('/api/prediction/predict', extractedSkills, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setPredictionResult(response.data);
    } catch (err) {
      setResumeError(err.response?.data?.detail || 'Failed to predict career.');
    } finally {
      setPredicting(false);
    }
  };

  const handleGenerateRoadmap = async () => {
    if (!predictionResult || extractedSkills.length === 0) return;
    setGeneratingRoadmap(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `/api/roadmap/generate?predicted_role=${encodeURIComponent(predictionResult.top_prediction)}`,
        extractedSkills,
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      setRoadmap(response.data);
    } catch (err) {
      setResumeError(err.response?.data?.detail || 'Failed to generate roadmap.');
    } finally {
      setGeneratingRoadmap(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="w-16 h-16 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 p-8 overflow-y-auto">
      {/* Header */}
      <header className="max-w-6xl mx-auto flex justify-between items-center mb-12">
        <div>
          <h1 className="text-2xl font-bold bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">
            AI Career Guidance
          </h1>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 text-slate-300">
            <User className="w-5 h-5" />
            <span className="font-medium">{user?.name}</span>
          </div>
          <button
            onClick={handleLogout}
            className="p-2 hover:bg-white/10 rounded-full transition-colors text-slate-400 hover:text-white"
            title="Logout"
          >
            <LogOut className="w-5 h-5" />
          </button>
        </div>
      </header>

      <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-8 pb-12">
        
        {/* Profile Management Section */}
        <div className="md:col-span-1 space-y-6">
          <div className="glass-panel p-6">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-semibold flex items-center gap-2">
                <User className="w-5 h-5 text-indigo-400" /> My Profile
              </h2>
              {!isEditing && (
                <button
                  onClick={() => setIsEditing(true)}
                  className="text-sm text-indigo-400 hover:text-indigo-300 transition-colors"
                >
                  Edit
                </button>
              )}
            </div>

            {error && <div className="text-red-400 text-sm mb-4">{error}</div>}
            {success && <div className="text-green-400 text-sm mb-4">{success}</div>}

            {isEditing ? (
              <form onSubmit={handleUpdateProfile} className="space-y-4">
                <div>
                  <label className="block text-sm text-slate-400 mb-1">CGPA (out of 10)</label>
                  <div className="relative">
                    <GraduationCap className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 w-4 h-4" />
                    <input
                      type="number"
                      step="0.01"
                      min="0"
                      max="10"
                      className="input-glass pl-10 py-2 text-sm"
                      value={formData.cgpa}
                      onChange={(e) => setFormData({ ...formData, cgpa: e.target.value })}
                      placeholder="e.g. 8.5"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm text-slate-400 mb-1">Interests</label>
                  <div className="relative">
                    <BookOpen className="absolute left-3 top-3 text-slate-400 w-4 h-4" />
                    <textarea
                      rows="3"
                      className="input-glass pl-10 py-2 text-sm resize-none"
                      value={formData.interests}
                      onChange={(e) => setFormData({ ...formData, interests: e.target.value })}
                      placeholder="e.g. Machine Learning, Web Development"
                    />
                  </div>
                </div>

                <div className="flex gap-2 pt-2">
                  <button
                    type="submit"
                    disabled={saving}
                    className="flex-1 bg-indigo-500 hover:bg-indigo-600 text-white rounded-lg py-2 text-sm flex items-center justify-center gap-2 transition-colors"
                  >
                    <Save className="w-4 h-4" /> {saving ? 'Saving...' : 'Save'}
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setIsEditing(false);
                      setFormData({ cgpa: user.cgpa || '', interests: user.interests || '' });
                      setError('');
                      setSuccess('');
                    }}
                    className="px-4 py-2 bg-slate-800 hover:bg-slate-700 rounded-lg text-sm transition-colors"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            ) : (
              <div className="space-y-4">
                <div>
                  <p className="text-sm text-slate-400">Email</p>
                  <p className="font-medium text-slate-200">{user?.email}</p>
                </div>
                <div>
                  <p className="text-sm text-slate-400">CGPA</p>
                  <p className="font-medium text-slate-200">{user?.cgpa || 'Not set'}</p>
                </div>
                <div>
                  <p className="text-sm text-slate-400">Interests</p>
                  <p className="font-medium text-slate-200">{user?.interests || 'Not set'}</p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Dashboard Main Area */}
        <div className="md:col-span-2 space-y-6">
          <div className="glass-panel p-6">
            <h2 className="text-xl font-semibold mb-2 flex items-center gap-2">
              <FileText className="w-5 h-5 text-purple-400" /> Resume Analysis
            </h2>
            <p className="text-slate-400 text-sm mb-6">Upload your resume to let our AI extract skills and match you to careers.</p>
            
            <div 
              className="border-2 border-dashed border-indigo-500/30 bg-indigo-500/5 hover:bg-indigo-500/10 rounded-xl p-8 text-center transition-all cursor-pointer relative group"
              onClick={() => fileInputRef.current?.click()}
            >
              <input 
                type="file" 
                ref={fileInputRef} 
                onChange={handleResumeUpload} 
                className="hidden" 
                accept=".pdf,.docx" 
              />
              
              <div className="flex flex-col items-center justify-center gap-3">
                {uploadingResume ? (
                  <div className="w-10 h-10 border-4 border-indigo-400 border-t-transparent rounded-full animate-spin"></div>
                ) : (
                  <UploadCloud className="w-12 h-12 text-indigo-400 group-hover:scale-110 transition-transform" />
                )}
                
                <div>
                  <p className="text-slate-200 font-medium">
                    {uploadingResume ? 'Processing document...' : 'Click to Upload Resume'}
                  </p>
                  <p className="text-slate-500 text-sm mt-1">Supports PDF & DOCX</p>
                </div>
              </div>
            </div>

            {resumeError && (
              <div className="mt-4 p-3 bg-red-500/10 border border-red-500/50 rounded-lg text-red-400 text-sm text-center">
                {resumeError}
              </div>
            )}
            
            {resumeSuccess && (
              <div className="mt-4 p-5 bg-black/20 border border-white/5 rounded-xl space-y-4">
                <div className="flex items-center gap-2 text-emerald-400">
                  <CheckCircle2 className="w-5 h-5" />
                  <span className="font-semibold">{resumeSuccess}</span>
                </div>
                
                {extractedSkills.length > 0 && (
                  <div>
                    <h3 className="text-sm text-slate-400 mb-2">Extracted NLP Skills:</h3>
                    <div className="flex flex-wrap gap-2">
                      {extractedSkills.map((skill, idx) => (
                        <span key={idx} className="bg-indigo-500/20 border border-indigo-500/30 text-indigo-300 px-3 py-1 rounded-full text-xs font-medium shadow-sm">
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                <button 
                  onClick={handlePredictCareer}
                  disabled={predicting}
                  className="mt-4 w-full bg-gradient-to-r from-purple-500 to-indigo-600 hover:from-purple-600 hover:to-indigo-700 text-white font-medium py-3 rounded-lg flex items-center justify-center gap-2 transition-all shadow-lg"
                >
                  <Cpu className={`w-5 h-5 ${predicting ? 'animate-pulse' : ''}`} />
                  {predicting ? 'Engine Running Model...' : 'Predict Ideal Career Matches'}
                </button>
              </div>
            )}
          </div>

          {/* Predictions Display UI */}
          {predictionResult && (
            <div className="glass-panel p-6 border border-emerald-500/20 bg-emerald-500/5">
              <h2 className="text-xl font-semibold mb-4 flex items-center gap-2 text-emerald-400">
                <TrendingUp className="w-5 h-5" /> Recommended Career
              </h2>
              
              <div className="bg-black/40 p-5 rounded-xl mb-6 flex flex-col items-center justify-center border border-white/5">
                <p className="text-sm text-slate-400 mb-2 uppercase tracking-wide font-medium">Best Fit</p>
                <p className="text-3xl font-bold bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">
                  {predictionResult.top_prediction}
                </p>
                <div className="mt-3 px-4 py-1.5 bg-emerald-500/20 text-emerald-300 rounded-full text-sm flex items-center gap-2">
                  <span>Confidence: {(predictionResult.confidence_score * 100).toFixed(1)}%</span>
                </div>
              </div>

              <div>
                <h3 className="text-sm font-medium text-slate-400 mb-3">Other Alternatives</h3>
                <div className="space-y-3">
                  {predictionResult.all_probabilities.slice(1, 4).map((prob, idx) => (
                    <div key={idx} className="flex items-center justify-between text-sm bg-black/20 p-3 rounded-lg">
                      <span className="text-slate-300">{prob.role}</span>
                      <span className="text-slate-500">{(prob.probability * 100).toFixed(1)}%</span>
                    </div>
                  ))}
                </div>
              </div>
              
              {!roadmap && (
                <button 
                  onClick={handleGenerateRoadmap}
                  disabled={generatingRoadmap}
                  className="mt-6 w-full bg-emerald-600/80 hover:bg-emerald-500 text-white font-medium py-3 rounded-lg flex items-center justify-center gap-2 transition-all shadow-lg shadow-emerald-900/20"
                >
                  <MapIcon className={`w-5 h-5 ${generatingRoadmap ? 'animate-spin' : ''}`} />
                  {generatingRoadmap ? 'Analyzing Skill Gaps...' : 'Generate Learning Roadmap'}
                </button>
              )}
            </div>
          )}
          
          {/* Learning Roadmap Visualization */}
          {roadmap && (
            <div className="glass-panel p-6 border border-cyan-500/20 bg-cyan-500/5 mt-6">
              <h2 className="text-xl font-semibold mb-4 flex items-center gap-2 text-cyan-400">
                <Compass className="w-5 h-5" /> Your Personal Roadmap
              </h2>
              
              <div className="flex items-center justify-between bg-black/30 p-4 rounded-xl mb-6">
                <span className="text-sm text-slate-400">Match Accuracy</span>
                <span className="text-lg font-bold text-cyan-400">{roadmap.match_percentage}%</span>
              </div>
              
              <div className="space-y-6">
                <div>
                  <h3 className="text-sm font-medium text-slate-300 mb-3 flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" /> Acquired Pipeline
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {roadmap.existing_skills.map((skill, idx) => (
                      <span key={idx} className="bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 px-3 py-1 rounded-full text-xs font-medium">
                        {skill}
                      </span>
                    ))}
                    {roadmap.existing_skills.length === 0 && (
                      <span className="text-sm text-slate-500">No applicable core skills detected.</span>
                    )}
                  </div>
                </div>

                <div>
                  <h3 className="text-sm font-medium text-slate-300 mb-3 flex items-center gap-2">
                    <TrendingUp className="w-4 h-4 text-amber-400" /> Target Pipeline
                  </h3>
                  {roadmap.missing_skills.length === 0 ? (
                    <div className="bg-emerald-500/10 text-emerald-400 p-4 rounded-lg text-sm text-center">
                      Congratulations! You have all the core skills for this role!
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {roadmap.recommended_courses.map((item, idx) => (
                        <div key={idx} className="bg-black/20 border border-amber-500/20 p-4 rounded-xl flex flex-col gap-2">
                          <div className="flex items-center gap-2">
                            <span className="bg-amber-500/20 text-amber-300 px-2 py-0.5 rounded text-xs font-bold uppercase tracking-wide">
                              Skill Gap
                            </span>
                            <span className="font-semibold text-slate-200">{item.skill}</span>
                          </div>
                          <p className="text-sm text-slate-400 pl-2 border-l-2 border-amber-500/30">
                            Course: {item.course}
                          </p>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

        </div>

      </div>
    </div>
  );
}
