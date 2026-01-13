
import React, { useEffect, useRef } from 'react';
import WaveSurfer from 'wavesurfer.js';

const WaveformViewer = ({ url, title }) => {
  const containerRef = useRef(null);
  const waveSurferRef = useRef(null);

  useEffect(() => {
    if (!containerRef.current) return;

    waveSurferRef.current = WaveSurfer.create({
      container: containerRef.current,
      waveColor: '#4f46e5',
      progressColor: '#818cf8',
      cursorColor: '#c7d2fe',
      barWidth: 2,
      barGap: 1,
      barRadius: 2,
      height: 100,
      normalize: true,
    });

    if (url) {
      waveSurferRef.current.load(url);
    }

    return () => {
      waveSurferRef.current?.destroy();
    };
  }, [url]);

  const handlePlayPause = () => {
    waveSurferRef.current?.playPause();
  };

  return (
    <div className="glass-panel" style={{ marginTop: '1rem' }}>
      <h3 style={{ marginBottom: '0.5rem' }}>{title}</h3>
      <div ref={containerRef} className="waveform-container" />
      <div style={{ marginTop: '1rem', display: 'flex', gap: '1rem' }}>
        <button 
          onClick={handlePlayPause}
          className="primary-btn"
          style={{ width: 'auto', padding: '0.5rem 1rem' }}
        >
          Play / Pause
        </button>
      </div>
    </div>
  );
};

export default WaveformViewer;
