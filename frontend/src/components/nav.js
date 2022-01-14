import { Link } from "react-router-dom"
import { Navbar, Nav as BootNav, Container } from "react-bootstrap"
import { useContext } from "react";
import ThemeContext from "./useDark";
import './nav.css'


export default function Nav() {
  const {dark, setDark } = useContext(ThemeContext);
  // https://react-bootstrap.github.io/components/navbar/
  return (
    <Navbar bg="light" expand="lg">
      <Container>
        <Navbar.Brand href="#">MyLibrary</Navbar.Brand>
        <Navbar.Toggle aria-controls="basic-navbar-nav" />
        <Navbar.Collapse id="basic-navbar-nav">
          <BootNav >
            <Link className="navs" to="/">Home</Link>
            <Link className="navs" to="/books">Books</Link> 
            <Link className="navs" to="#" onClick={ () => { setDark(!dark) }}>{dark?'dark':'light'} mode</Link> 
            
          </BootNav>
        </Navbar.Collapse>
      </Container>
    </Navbar>)
}