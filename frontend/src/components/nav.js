import { Link } from "react-router-dom"
import { Navbar, Nav as BootNav, Container } from "react-bootstrap"
import { useContext } from "react";
import ThemeContext from "./useDark";
import './nav.css'


export default function Nav() {
  const { dark, setDark } = useContext(ThemeContext);
  // https://react-bootstrap.github.io/components/navbar/
  return (
    <Navbar bg="light" expand="lg" bg={dark ? "dark" : "light"} variant={dark ? "dark" : "light"}>
      <Container>
        <Navbar.Brand href="#">MyLibrary</Navbar.Brand>
        <Navbar.Toggle aria-controls="basic-navbar-nav" />
        <Navbar.Collapse id="basic-navbar-nav">
          <BootNav >
            <Navbar.Text><Link className="navs" to="/">Home</Link></Navbar.Text>
            <Navbar.Text><Link className="navs" to="/books">Books</Link></Navbar.Text>
            <Navbar.Text
              style={{font_size: 2 + 'em'}}
              className="navs justify-content-end"
              onClick={() => { setDark(!dark) }}>
              Change theme {dark ? '🌚' : '🌝'}
            </Navbar.Text>
          </BootNav>
        </Navbar.Collapse>
      </Container>
    </Navbar>)
}