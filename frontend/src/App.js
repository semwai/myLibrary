import { BrowserRouter, Route, Routes } from 'react-router-dom';
import { useState } from 'react';
import './App.css';
import Book from './components/pages/book';
import Books from './components/pages/books';
import Index from './components/pages/Index';
import Login from './components/login';
import useToken from './components/useToken';
import Nav from './components/nav';
import ThemeContext from './components/useDark';


function App() {
  const { token, setToken } = useToken();
  const [dark, setDarkTheme] = useState(false)
  if (!token) {
    return <Login setToken={setToken} />
  }

  const themeInit = localStorage.getItem('dark') === 'true'
  document.body.style.backgroundColor = themeInit  ? 'black' : ''

  return (
    <ThemeContext.Provider value={
      {
        dark: themeInit,
        setDark: (value) => { 
          localStorage.setItem('dark', value)
          setDarkTheme(value)
          document.body.style.backgroundColor = value  ? 'black' : ''
        }
      }}>
      <BrowserRouter>
        <div>
          <Nav />
          <Routes>
            <Route path="/" element={<Index />}>
            </Route>
            <Route path="/book/:id" element={<Book />}>
            </Route>
            <Route path="/books" element={<Books />}>
            </Route>
          </Routes>
        </div>
      </BrowserRouter>
    </ThemeContext.Provider>
  );
}


export default App;
