import request from './request'

export function getContestList(params) {
  return request({
    url: '/api/v1/contest/list',
    method: 'get',
    params
  })
}

export function searchContests(params) {
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

export function getContestAttachments(contestId) {
  return request({
    url: `/api/v1/contest/${contestId}/attachments`,
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

// 评论相关
export function getContestComments(contestId, params) {
  return request({
    url: `/api/v1/contest/${contestId}/comments`,
    method: 'get',
    params
  })
}

export function createComment(data) {
  return request({
    url: '/api/v1/contest/comments',
    method: 'post',
    data
  })
}

export function updateComment(commentId, data) {
  return request({
    url: `/api/v1/contest/comments/${commentId}`,
    method: 'put',
    data
  })
}

export function deleteComment(commentId) {
  return request({
    url: `/api/v1/contest/comments/${commentId}`,
    method: 'delete'
  })
}

export function likeComment(commentId) {
  return request({
    url: `/api/v1/contest/comments/${commentId}/like`,
    method: 'post'
  })
}

// 私信相关
export function getConversations() {
  return request({
    url: '/api/v1/contest/messages/conversations',
    method: 'get'
  })
}

export function getMessagesWithUser(userId, params) {
  return request({
    url: `/api/v1/contest/messages/${userId}`,
    method: 'get',
    params
  })
}

export function sendMessage(data) {
  return request({
    url: '/api/v1/contest/messages',
    method: 'post',
    data
  })
}

export function deleteMessage(messageId) {
  return request({
    url: `/api/v1/contest/messages/${messageId}`,
    method: 'delete'
  })
}
