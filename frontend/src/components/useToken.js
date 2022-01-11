import { useState } from 'react';

export default function useToken() {
  const getToken = () => {
    return localStorage.getItem('access_token')
  };

  const [token, setToken] = useState(getToken());

  const saveToken = userToken => {
    localStorage.setItem('access_token', userToken.access_token)
    localStorage.setItem('refresh_token', userToken.refresh_token)
    setToken(userToken.access_token)
  };

  return {
    setToken: saveToken,
    token
  }
}