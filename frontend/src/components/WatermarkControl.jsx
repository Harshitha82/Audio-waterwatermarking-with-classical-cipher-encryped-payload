
import React, { useState } from 'react';
import axios from 'axios';
import WaveformViewer from './WaveformViewer';

const API_BASE = 'http://localhost:8000';

const WatermarkControl = () => {
    const [tab, setTab] = useState('embed');
    const [file, setFile] = useState(null);
    const [message, setMessage] = useState('');
    const [pfKey, setPfKey] = useState('');
    const [rfKey, setRfKey] = useState(2);
    const [bits, setBits] = useState(1);

    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [extractResult, setExtractResult] = useState(null);
    const [error, setError] = useState(null);

    const [originalAudioUrl, setOriginalAudioUrl] = useState(null);
    const [watermarkedAudioUrl, setWatermarkedAudioUrl] = useState(null);

    // Suggested bits
    const [suggestedBits, setSuggestedBits] = useState(null);

    const handleFileChange = (e) => {
        if (e.target.files[0]) {
            setFile(e.target.files[0]);
            setOriginalAudioUrl(URL.createObjectURL(e.target.files[0]));
            setResult(null);
            setWatermarkedAudioUrl(null);

            // Get Suggestion
            axios.get(`${API_BASE}/suggest?size=${e.target.files[0].size}`)
                .then(res => setSuggestedBits(res.data.recommended_bits))
                .catch(err => console.error(err));
        }
    };

    const handleEmbed = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        try {
            // 1. Upload
            const formData = new FormData();
            formData.append('file', file);
            const uploadRes = await axios.post(`${API_BASE}/upload`, formData);
            const fileId = uploadRes.data.file_id;

            // 2. Embed
            const embedForm = new FormData();
            embedForm.append('file_id', fileId);
            embedForm.append('message', message);
            embedForm.append('playfair_key', pfKey);
            embedForm.append('railfence_key', rfKey);
            embedForm.append('bits_per_sample', bits);

            const embedRes = await axios.post(`${API_BASE}/embed`, embedForm);
            setResult(embedRes.data);
            setWatermarkedAudioUrl(`${API_BASE}/download/${embedRes.data.output_file}`);
        } catch (err) {
            setError(err.response?.data?.detail || err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleExtract = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        setExtractResult(null);
        try {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('playfair_key', pfKey);
            formData.append('railfence_key', rfKey);
            formData.append('bits_per_sample', bits);

            const res = await axios.post(`${API_BASE}/extract`, formData);
            if (res.data.success) {
                setExtractResult(res.data);
            } else {
                setError(res.data.error || "Extraction failed");
            }
        } catch (err) {
            setError(err.response?.data?.detail || err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div>
            <div className="glass-panel">
                <div className="tabs">
                    <div
                        className={`tab ${tab === 'embed' ? 'active' : ''}`}
                        onClick={() => setTab('embed')}
                    >
                        Embed Watermark
                    </div>
                    <div
                        className={`tab ${tab === 'extract' ? 'active' : ''}`}
                        onClick={() => setTab('extract')}
                    >
                        Extract Message
                    </div>
                </div>

                <form onSubmit={tab === 'embed' ? handleEmbed : handleExtract}>
                    <div>
                        <label>Audio File (WAV)</label>
                        <input type="file" accept=".wav" onChange={handleFileChange} required />
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                        <div>
                            <label>Playfair Key (Keyword)</label>
                            <input
                                type="text"
                                value={pfKey}
                                onChange={e => setPfKey(e.target.value)}
                                placeholder="SECRET"
                                required
                            />
                        </div>
                        <div>
                            <label>Rail Fence Key (Depth)</label>
                            <input
                                type="number"
                                value={rfKey}
                                onChange={e => setRfKey(e.target.value)}
                                min="2"
                                required
                            />
                        </div>
                    </div>

                    <div>
                        <label>
                            Bit Depth (LSB)
                            {suggestedBits && tab === 'embed' && (
                                <span className="success-msg" style={{ marginLeft: '10px' }}>
                                    (Recommended: {suggestedBits})
                                </span>
                            )}
                        </label>
                        <select
                            value={bits}
                            onChange={e => setBits(parseInt(e.target.value))}
                        >
                            {[1, 2, 3, 4, 5, 6, 7, 8].map(n => (
                                <option key={n} value={n}>{n} bit{n > 1 ? 's' : ''}</option>
                            ))}
                        </select>
                    </div>

                    {tab === 'embed' && (
                        <div>
                            <label>Secret Message</label>
                            <textarea
                                value={message}
                                onChange={e => setMessage(e.target.value)}
                                rows="3"
                                placeholder="Enter message to hide..."
                                required
                            />
                        </div>
                    )}

                    <button type="submit" className="primary-btn" disabled={loading}>
                        {loading ? 'Processing...' : (tab === 'embed' ? 'Encrypt & Embed' : 'Extract & Decrypt')}
                    </button>

                    {error && <div className="error-msg">{error}</div>}
                </form>
            </div>

            {/* Results */}
            {result && tab === 'embed' && (
                <div style={{ marginTop: '2rem' }}>
                    <div className="glass-panel">
                        <h2>Embedding Successful</h2>
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem', marginTop: '1rem' }}>
                            <div className="metric-card">
                                <div className="metric-value">{result.snr.toFixed(2)} dB</div>
                                <div className="metric-label">Signal-to-Noise Ratio</div>
                            </div>
                            <div className="metric-card">
                                <div className="metric-value">{result.bits_embedded}</div>
                                <div className="metric-label">Bits Embedded</div>
                            </div>
                            <div className="metric-card">
                                <div className="metric-value" style={{ fontSize: '0.8rem', overflow: 'hidden' }} title={result.encrypted_message}>
                                    {result.encrypted_message.substring(0, 10)}...
                                </div>
                                <div className="metric-label">Ciphertext Preview</div>
                            </div>
                        </div>
                    </div>

                    <WaveformViewer title="Watermarked Audio" url={watermarkedAudioUrl} />

                    {originalAudioUrl && (
                        <WaveformViewer title="Original Audio" url={originalAudioUrl} />
                    )}
                </div>
            )}

            {extractResult && tab === 'extract' && (
                <div className="glass-panel" style={{ marginTop: '2rem' }}>
                    <h2>Extraction Result</h2>
                    <div style={{ marginTop: '1rem' }}>
                        <label>Decrypted Message:</label>
                        <div style={{
                            background: 'rgba(0,0,0,0.3)',
                            padding: '1rem',
                            borderRadius: '0.5rem',
                            fontFamily: 'monospace',
                            fontSize: '1.2rem',
                            color: '#4ade80'
                        }}>
                            {extractResult.decrypted_message}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default WatermarkControl;
