import request from './request'

export function login(data) {
  return request({
    url: '/api/v1/auth/login',
    method: 'post',
    data
  })
}

export function register(data) {
  return request({
    url: '/api/v1/auth/register',
    method: 'post',
    data
  })
}

export function refreshToken(refreshToken) {
  return request({
    url: '/api/v1/auth/refresh',
    method: 'post',
    data: { refresh_token: refreshToken }
  })
}

export function getCurrentUser() {
  return request({
    url: '/api/v1/auth/me',
    method: 'get'
  })
}

export function updateCurrentUser(data) {
  return request({
    url: '/api/v1/auth/me',
    method: 'put',
    data
  })
}

export function changePassword(data) {
  return request({
    url: '/api/v1/auth/change-password',
    method: 'post',
    data
  })
}

export function logout() {
  return request({
    url: '/api/v1/auth/logout',
    method: 'post'
  })
}
