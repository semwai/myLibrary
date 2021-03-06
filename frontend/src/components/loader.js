import { Spinner } from 'react-bootstrap'
import './loader.css'

export default function Loader() {
  return (
    <div className='loader'>
      <Spinner animation="border" role="status" variant="danger">
        <span className="visually-hidden">Loading...</span>
      </Spinner>
    </div>)
}