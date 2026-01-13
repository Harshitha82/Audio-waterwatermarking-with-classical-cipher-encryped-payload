
import React from 'react'
import WatermarkControl from './components/WatermarkControl'

function App() {
  return (
    <div className="App">
      <header style={{ marginBottom: '3rem', textAlign: 'center' }}>
        <h1 style={{
          background: 'linear-gradient(to right, #60a5fa, #c084fc)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          fontSize: '3rem',
          marginBottom: '0.5rem'
        }}>
          EchoCrypt
        </h1>
        <p style={{ color: '#94a3b8' }}>
          Secure Audio Watermarking with Multi-Layer Encryption
        </p>
      </header>

      <main>
        <WatermarkControl />
      </main>
    </div>
  )
}

export default App
