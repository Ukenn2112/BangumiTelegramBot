from model.page_model import DoEditCollectionTypeRequest
from utils.api import user_collection_get, collection_post, user_data_get


def do(request: DoEditCollectionTypeRequest, tg_id: int) -> DoEditCollectionTypeRequest:
    subject_id = request.subject_id
    collection_type = request.collection_type
    access_token = user_data_get(tg_id).get('access_token')
    rating = str(user_collection_get(None, subject_id, access_token).get('rating'))
    if collection_type == 'wish':  # 想看
        collection_post(None, subject_id, collection_type, rating, access_token)
        request.callback_text = "已将收藏更改为想看"
    if collection_type == 'collect':  # 看过
        collection_post(None, subject_id, collection_type, rating, access_token)
        request.callback_text = "已将收藏更改为看过"
    if collection_type == 'do':  # 在看
        collection_post(None, subject_id, collection_type, rating, access_token)
        request.callback_text = "已将收藏更改为在看"
    if collection_type == 'on_hold':  # 搁置
        collection_post(None, subject_id, collection_type, rating, access_token)
        request.callback_text = "已将收藏更改为搁置"
    if collection_type == 'dropped':  # 抛弃
        collection_post(None, subject_id, collection_type, rating, access_token)
        request.callback_text = "已将收藏更改为抛弃"
    return request
