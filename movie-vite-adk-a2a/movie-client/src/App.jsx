import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import Chat from './Chat'

function App() {
  const [count, setCount] = useState(0)

  return (
    <>
      <h2>Chat with the Movie Chatter</h2>
      <Chat />
    </>
  )
}

export default App
