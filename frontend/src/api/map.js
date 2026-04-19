import request from './request'

// ============== POI 相关 ==============

export function getPOIList(params) {
  return request({
    url: '/api/v1/map/pois',
    method: 'get',
    params
  })
}

export function getHotPOIs(limit = 10) {
  return request({
    url: '/api/v1/map/pois/hot',
    method: 'get',
    params: { limit }
  })
}

export function getPOIDetail(poiId) {
  return request({
    url: `/api/v1/map/pois/${poiId}`,
    method: 'get'
  })
}

export function createPOI(data) {
  return request({
    url: '/api/v1/map/pois',
    method: 'post',
    data
  })
}

export function updatePOI(poiId, data) {
  return request({
    url: `/api/v1/map/pois/${poiId}`,
    method: 'put',
    data
  })
}

export function deletePOI(poiId) {
  return request({
    url: `/api/v1/map/pois/${poiId}`,
    method: 'delete'
  })
}

// ============== 打卡相关 ==============

export function getCheckInList(params) {
  return request({
    url: '/api/v1/map/check-ins',
    method: 'get',
    params
  })
}

export function getRecentCheckIns(limit = 20) {
  return request({
    url: '/api/v1/map/check-ins/recent',
    method: 'get',
    params: { limit }
  })
}

export function getCheckInDetail(checkInId) {
  return request({
    url: `/api/v1/map/check-ins/${checkInId}`,
    method: 'get'
  })
}

export function createCheckIn(data) {
  return request({
    url: '/api/v1/map/check-ins',
    method: 'post',
    data
  })
}

export function updateCheckIn(checkInId, data) {
  return request({
    url: `/api/v1/map/check-ins/${checkInId}`,
    method: 'put',
    data
  })
}

export function deleteCheckIn(checkInId) {
  return request({
    url: `/api/v1/map/check-ins/${checkInId}`,
    method: 'delete'
  })
}

export function likeCheckIn(checkInId) {
  return request({
    url: `/api/v1/map/check-ins/${checkInId}/like`,
    method: 'post'
  })
}

export function hasLikedCheckIn(checkInId) {
  return request({
    url: `/api/v1/map/check-ins/${checkInId}/has-liked`,
    method: 'get'
  })
}

// ============== POI 评论 ==============

export function getPOIComments(poiId, params) {
  return request({
    url: `/api/v1/map/pois/${poiId}/comments`,
    method: 'get',
    params
  })
}

export function createPOIComment(poiId, data) {
  return request({
    url: `/api/v1/map/pois/${poiId}/comments`,
    method: 'post',
    data
  })
}

export function updatePOIComment(commentId, data) {
  return request({
    url: `/api/v1/map/poi-comments/${commentId}`,
    method: 'put',
    data
  })
}

export function deletePOIComment(commentId) {
  return request({
    url: `/api/v1/map/poi-comments/${commentId}`,
    method: 'delete'
  })
}

// ============== 打卡评论 ==============

export function getCheckInComments(checkInId, params) {
  return request({
    url: `/api/v1/map/check-ins/${checkInId}/comments`,
    method: 'get',
    params
  })
}

export function createCheckInComment(checkInId, data) {
  return request({
    url: `/api/v1/map/check-ins/${checkInId}/comments`,
    method: 'post',
    data
  })
}

export function updateCheckInComment(commentId, data) {
  return request({
    url: `/api/v1/map/check-in-comments/${commentId}`,
    method: 'put',
    data
  })
}

export function deleteCheckInComment(commentId) {
  return request({
    url: `/api/v1/map/check-in-comments/${commentId}`,
    method: 'delete'
  })
}

// ============== 收藏 ==============

export function getFavorites(params) {
  return request({
    url: '/api/v1/map/favorites',
    method: 'get',
    params
  })
}

export function toggleFavorite(data) {
  return request({
    url: '/api/v1/map/favorites/toggle',
    method: 'post',
    data
  })
}

export function hasFavoritedPOI(poiId) {
  return request({
    url: `/api/v1/map/pois/${poiId}/has-favorited`,
    method: 'get'
  })
}

// ============== 话题 ==============

export function getTopicList(params) {
  return request({
    url: '/api/v1/map/topics',
    method: 'get',
    params
  })
}

export function getHotTopics(limit = 10) {
  return request({
    url: '/api/v1/map/topics/hot',
    method: 'get',
    params: { limit }
  })
}

export function getTopicDetail(topicId) {
  return request({
    url: `/api/v1/map/topics/${topicId}`,
    method: 'get'
  })
}

export function createTopic(data) {
  return request({
    url: '/api/v1/map/topics',
    method: 'post',
    data
  })
}

export function updateTopic(topicId, data) {
  return request({
    url: `/api/v1/map/topics/${topicId}`,
    method: 'put',
    data
  })
}

export function deleteTopic(topicId) {
  return request({
    url: `/api/v1/map/topics/${topicId}`,
    method: 'delete'
  })
}

// ============== 统计 ==============

export function getMapStats() {
  return request({
    url: '/api/v1/map/stats',
    method: 'get'
  })
}

// ============== 图片上传 ==============

export function uploadMapImage(file) {
  const formData = new FormData()
  formData.append('file', file)
  return request({
    url: '/api/v1/map/upload-image',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}
