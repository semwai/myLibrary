import { Link } from "react-router-dom"
import { Navbar, Nav as BootNav, Container } from "react-bootstrap"
import { useContext } from "react";
import ThemeContext from "./useDark";
import useToken from "./useToken";
import './nav.css'


export default function Nav() {
  const { dark, setDark } = useContext(ThemeContext);
  const { token, setToken } = useToken();

  const exit = () => {
    let path = `${process.env.REACT_APP_BACK_ADDR}/logout`
    fetch(path, {
      mode: 'cors',
      headers: { 'Authorization': `Bearer ${token}` },
      method: 'POST'
    })
    setToken(null)
    localStorage.clear()
  }

  // https://react-bootstrap.github.io/components/navbar/
  return (
    <Navbar  bg={dark ? "dark" : "light"} variant={dark ? "dark" : "light"}>
      <Container>

        <Navbar.Collapse id="basic-navbar-nav" className="navs justify-content-start">
          <BootNav>
            <Navbar.Text><Link className="navs" to="/">Home</Link></Navbar.Text>
            <Navbar.Text><Link className="navs" to="/books">Books</Link></Navbar.Text>
            <Navbar.Text
              style={{ font_size: 2 + 'em' }}
              onClick={() => { setDark(!dark) }}>
              Change theme {dark ? '🌚' : '🌝'}
            </Navbar.Text>
          </BootNav>
        </Navbar.Collapse>

        <Navbar.Collapse id="basic-navbar-nav" className="navs justify-content-end">
          <BootNav>
            <Navbar.Text><Link className="navs" to="#" onClick={exit}> Exit</Link></Navbar.Text>
          </BootNav>
        </Navbar.Collapse>
        <Navbar.Toggle aria-controls="basic-navbar-nav" />
      </Container>
    </Navbar>)
}