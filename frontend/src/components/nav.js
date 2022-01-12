import { Link } from "react-router-dom"
import { Navbar, Nav as BootNav, Container } from "react-bootstrap"
import './nav.css'

export default function Nav() {
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
          </BootNav>
        </Navbar.Collapse>
      </Container>
    </Navbar>)
}