import React, { useState, useEffect, useContext } from 'react';
import { useParams } from 'react-router-dom';
import { Container, Row, Col } from 'react-bootstrap';
import useToken from '../useToken';
import Loader from '../loader';
import ThemeContext from '../useDark';
import './book.css'

function getPage(token, setPageUrl, setPage, setWait, book, page) {

  let path = `${process.env.REACT_APP_BACK_ADDR}/page/${book}`
  if (page !== undefined) {
    console.log(page)
    if (page < 0)
      return
    path += `?page=${page}`
  }
  setWait(true)
  fetch(path, {
    mode: 'cors',
    headers: { 'Authorization': `Bearer ${token}` }
  })
    .then(function (response) {
      if (response.status === 404)
        throw new Error(response.statusText);
      const page = parseInt(response.headers.get('page'))
      setPage(page)
      return response.blob()
    })
    .then(function (blob) {
      var objectURL = URL.createObjectURL(blob)
      setPageUrl(objectURL)
      setWait(false)
      window.scrollTo({
        top: 0,
        behavior: "instant"
      });
    })
    .catch(err => setWait(false))
}

function getBookInfo(token, setbookMeta, book) {
  let path = `${process.env.REACT_APP_BACK_ADDR}/book_info/${book}`
  fetch(path, {
    mode: 'cors',
    headers: { 'Authorization': `Bearer ${token}`, 'page': '' }
  })
    .then(res => res.json())
    .then(function (json) {
      setbookMeta(json)
      document.title = json.name + (json.author === null ? '' : ' - ') + (json?.author || '')
    })
}

export default function Book() {

  const { token } = useToken()
  const [pageUrl, setPageUrl] = useState('#')
  const [page, setPage] = useState(undefined)
  const [bookMeta, setbookMeta] = useState(undefined)
  const [wait, setWait] = useState(true)
  const book_id = useParams().id
  const theme = useContext(ThemeContext);
  useEffect(() => {
    getPage(token, setPageUrl, setPage, setWait, book_id)
    getBookInfo(token, setbookMeta, book_id)
  }, [])

  const loadPage = (p) => getPage(token, setPageUrl, setPage, setWait, book_id, p)

  if (wait)
    return <Loader />

  const buttonThemeClass = theme.dark ? 'button-center-dark' : 'button-center-light'

  const controlPane = <Container fluid className={theme.dark ? 'dark-bottom' : ''}>
    <Row>
      {page > 0 ?
        <Col className={'element-center ' + buttonThemeClass} onClick={() => { loadPage(page - 1) }}>
          Back
        </Col>
        : <Col></Col>
      }
      <Col className='element-center' onClick=
        {e => {
          const new_page = prompt('page') - 1
          loadPage(new_page)
        }} >
        {page + 1} of {bookMeta?.pages}
      </Col>
      {page + 1 < bookMeta?.pages ?
        <Col className={'element-center ' + buttonThemeClass} onClick={() => { loadPage(page + 1) }}>
          Next
        </Col>
        : <Col></Col>
      }
    </Row>
  </Container>

  return (
    <div>
      { controlPane }
      <img width='100%' src={pageUrl} alt={'page ' + page} className={theme.dark ? 'invert' : ''} />
      { controlPane }
    </div>
  )
}