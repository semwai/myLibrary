import { Link } from "react-router-dom"
import { Navbar, Nav as BootNav, Container, NavDropdown } from "react-bootstrap"

export default function Nav() {
  // https://react-bootstrap.github.io/components/navbar/
  return (
    <Navbar bg="light" expand="lg">
      <Container>
        <Navbar.Brand href="#home">MyLibrary</Navbar.Brand>
        <Navbar.Toggle aria-controls="basic-navbar-nav" />
        <Navbar.Collapse id="basic-navbar-nav">
          <BootNav className="me-auto">
            <BootNav.Link href="#"><Link to="/">Home</Link></BootNav.Link>
            <BootNav.Link href="#"><Link to="/book">Book</Link></BootNav.Link>
            <BootNav.Link href="#"><Link to="/books">Books</Link></BootNav.Link>
          </BootNav>
        </Navbar.Collapse>
      </Container>
    </Navbar>)
}