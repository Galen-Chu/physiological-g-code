"""Discussion views: CRUD, voting, and nested threaded comments."""
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from api.models import Discussion, Comment, Vote, Notification
from api.serializers.discussion import DiscussionSerializer, CommentSerializer


class DiscussionViewSet(viewsets.ModelViewSet):
    serializer_class = DiscussionSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = Discussion.objects.select_related('author').order_by(
            '-is_pinned', '-last_comment_at', '-created_at'
        )
        discussion_type = self.request.query_params.get('type')
        if discussion_type:
            qs = qs.filter(discussion_type=discussion_type)
        return qs

    def perform_create(self, serializer):
        # slug uniqueness: fallback loop in case of collisions
        from django.utils.text import slugify
        base = slugify(serializer.validated_data.get('title', ''))[:50] or 'discussion'
        slug, i = base, 2
        while Discussion.objects.filter(slug=slug).exists():
            slug = f'{base}-{i}'
            i += 1
        serializer.save(author=self.request.user, slug=slug)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def vote(self, request, pk=None):
        """POST {vote_type: 'up'|'down'} — one vote per user, re-voting updates."""
        discussion = self.get_object()
        vote_type = request.data.get('vote_type')
        if vote_type not in ('up', 'down'):
            return Response({'error': "vote_type must be 'up' or 'down'"},
                            status=status.HTTP_400_BAD_REQUEST)

        ct = ContentType.objects.get_for_model(Discussion)
        vote, created = Vote.objects.update_or_create(
            user=request.user, content_type=ct, object_id=discussion.id,
            defaults={'vote_type': vote_type},
        )

        score = sum(
            1 if v.vote_type == 'up' else -1
            for v in Vote.objects.filter(content_type=ct, object_id=discussion.id)
        )
        discussion.vote_score = score
        discussion.save(update_fields=['vote_score'])
        return Response({'vote_type': vote_type, 'created': created, 'vote_score': score})

    @action(detail=True, methods=['get', 'post'], permission_classes=[IsAuthenticatedOrReadOnly])
    def comments(self, request, pk=None):
        """List a discussion's comments (flat, threaded via `parent`) or post one."""
        discussion = self.get_object()
        ct = ContentType.objects.get_for_model(Discussion)
        qs = (Comment.objects.filter(content_type=ct, object_id=discussion.id)
              .filter(is_removed=False)
              .select_related('author')
              .order_by('created_at'))

        if request.method == 'GET':
            serializer = CommentSerializer(qs, many=True)
            discussion.view_count += 1
            discussion.save(update_fields=['view_count'])
            return Response({'count': qs.count(), 'comments': serializer.data})

        # POST — create a comment (optionally a reply via `parent`)
        serializer = CommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        parent = serializer.validated_data.get('parent')
        if parent is not None:
            if parent.content_type_id != ct.id or parent.object_id != discussion.id:
                return Response({'error': 'parent comment belongs to another discussion'},
                                status=status.HTTP_400_BAD_REQUEST)

        comment = Comment.objects.create(
            content_type=ct, object_id=discussion.id,
            author=request.user, parent=parent,
            content=serializer.validated_data['content'],
        )

        # Denormalized counters + a notification for the discussion author
        discussion.comment_count = qs.count()
        discussion.last_comment_at = comment.created_at
        discussion.last_comment_by = request.user
        discussion.participant_count = qs.values('author').distinct().count()
        discussion.save(update_fields=['comment_count', 'last_comment_at',
                                       'last_comment_by', 'participant_count'])

        if discussion.author_id != request.user.id:
            Notification.objects.create(
                recipient=discussion.author, actor=request.user,
                notification_type='comment',
                content_type=ct, object_id=discussion.id,
                title=f'{request.user.username} commented on your discussion',
                message=comment.content[:200],
                url=f'/discussions/{discussion.slug}',
            )

        profile = getattr(request.user, 'profile', None)
        if profile:
            profile.comments_posted += 1
            profile.save(update_fields=['comments_posted'])

        return Response(CommentSerializer(comment).data, status=status.HTTP_201_CREATED)


class CommentViewSet(viewsets.GenericViewSet):
    """Retrieve / edit / delete a comment, and vote on it."""

    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Comment.objects.select_related('author')

    def retrieve(self, request, *args, **kwargs):
        return Response(CommentSerializer(self.get_object()).data)

    def partial_update(self, request, *args, **kwargs):
        comment = self.get_object()
        if comment.author_id != request.user.id:
            return Response({'error': 'not the comment author'},
                            status=status.HTTP_403_FORBIDDEN)
        serializer = CommentSerializer(comment, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(edited_at=timezone.now())
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        comment = self.get_object()
        if comment.author_id != request.user.id:
            return Response({'error': 'not the comment author'},
                            status=status.HTTP_403_FORBIDDEN)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def vote(self, request, pk=None):
        comment = self.get_object()
        vote_type = request.data.get('vote_type')
        if vote_type not in ('up', 'down'):
            return Response({'error': "vote_type must be 'up' or 'down'"},
                            status=status.HTTP_400_BAD_REQUEST)

        ct = ContentType.objects.get_for_model(Comment)
        Vote.objects.update_or_create(
            user=request.user, content_type=ct, object_id=comment.id,
            defaults={'vote_type': vote_type},
        )
        ups = Vote.objects.filter(content_type=ct, object_id=comment.id, vote_type='up').count()
        downs = Vote.objects.filter(content_type=ct, object_id=comment.id, vote_type='down').count()
        comment.upvotes = ups
        comment.downvotes = downs
        comment.vote_score = ups - downs
        comment.save(update_fields=['upvotes', 'downvotes', 'vote_score'])
        return Response({'vote_type': vote_type, 'vote_score': comment.vote_score})
