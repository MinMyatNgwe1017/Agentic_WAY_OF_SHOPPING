import { useState } from 'react'
import './App.css'
import Login from './components/Login'
import SignUp from './components/SignUp'
import BUTTON from '@mui/material/Button'

function App() {
  const [isLogin, setIsLogin] = useState(true)

  return (
    <div>
      {isLogin ? <Login /> : <SignUp />}

      <BUTTON onClick={() => setIsLogin(!isLogin)} style={{ marginTop: '20px' }} >
        {isLogin ? "Don't have an account? Create one" : 'Already have an account? Login'}
      </BUTTON>
    </div>
  )
}

export default App
