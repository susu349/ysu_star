import request from './request'

export function getContestList(params) {
  return request({
    url: '/api/v1/contest/list',
    method: 'get',
    params
  })
}

export function getContestDetail(contestId) {
  return request({
    url: `/api/v1/contest/${contestId}`,
    method: 'get'
  })
}

export function getRecommendedContests(limit = 10) {
  return request({
    url: '/api/v1/contest/recommend/my',
    method: 'get',
    params: { limit }
  })
}

export function getTeamList(contestId, params) {
  return request({
    url: `/api/v1/contest/${contestId}/teams`,
    method: 'get',
    params
  })
}

export function getTeamDetail(teamId) {
  return request({
    url: `/api/v1/contest/teams/${teamId}`,
    method: 'get'
  })
}

export function createTeam(data) {
  return request({
    url: '/api/v1/contest/teams',
    method: 'post',
    data
  })
}

export function applyToTeam(teamId, message) {
  return request({
    url: `/api/v1/contest/teams/${teamId}/apply`,
    method: 'post',
    data: message ? { message } : {}
  })
}

export function getMyApplications() {
  return request({
    url: '/api/v1/contest/my/applications',
    method: 'get'
  })
}
