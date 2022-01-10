import { BrowserRouter, Route, Routes } from 'react-router-dom';
import './App.css';
import Book from './components/pages/book';
import Index from './components/pages/Index';
import Login from './components/login';
import useToken from './components/useToken';
 

function App() {
  const { token, setToken } = useToken();

  if(!token) {
    return <Login setToken={setToken} />
  }

  return (
    <div className="wrapper">
      <h1>Application</h1>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Index />}>
          </Route>
          <Route path="/book" element={<Book />}>
          </Route>
        </Routes>
      </BrowserRouter>
    </div>
  );
}


export default App;
