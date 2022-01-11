
export function refreshToken() {
  const token = localStorage.getItem('refresh_token')

  fetch(`${process.env.REACT_APP_BACK_ADDR}/refresh`, {
    mode: 'cors',
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` }
  }).then(res => res.json())
    .then(function(data) {
      console.log(data)
      localStorage.setItem('access_token', data.access_token)
    })
}