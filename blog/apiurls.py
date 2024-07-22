from rest_framework.routers import DefaultRouter
from . import views, api

router = DefaultRouter()
router.register('blogs/categories', api.CategoryPublicViewSet, basename='category_public_blog')
router.register('blogs/tags', api.TagPublicViewSet, basename='tag_public_blog')
router.register('blogs/posts', api.PostPublicViewSet, basename='post_public_blog')
router.register('blogs/category', api.CategoryViewSet, basename='category_blog')
router.register('blogs/tag', api.TagViewSet, basename='tag_blog')
router.register('blogs/post', api.PostViewSet, basename='post_blog')
router.register('blogs/comment', api.CommentViewSet, basename='comment_blog')
router.register('blogs/action', api.ActionViewSet, basename='action_blog')