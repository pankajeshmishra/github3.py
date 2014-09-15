# -*- coding: utf-8 -*-
"""
github3.events
==============

This module contains the class(es) related to Events

"""
from __future__ import unicode_literals

from .models import GitHubObject


class Event(GitHubObject):

    """The :class:`Event <Event>` object. It structures and handles the data
    returned by via the `Events <http://developer.github.com/v3/events>`_
    section of the GitHub API.

    Two events can be compared like so::

        e1 == e2
        e1 != e2

    And that is equivalent to::

        e1.id == e2.id
        e1.id != e2.id

    """

    def _update_attributes(self, event):
        from .users import User
        from .orgs import Organization
        #: :class:`User <github3.users.User>` object representing the actor.
        self.actor = User(event.get('actor')) if event.get('actor') else None
        #: datetime object representing when the event was created.
        self.created_at = self._strptime(event.get('created_at'))
        #: Unique id of the event
        self.id = event.get('id')
        #: List all possible types of Events
        self.org = None
        if event.get('org'):
            self.org = Organization(event.get('org'))
        #: Event type http://developer.github.com/v3/activity/events/types/
        self.type = event.get('type')
        handler = _payload_handlers.get(self.type, identity)
        #: Dictionary with the payload. Payload structure is defined by type_.
        #  _type: http://developer.github.com/v3/events/types
        self.payload = handler(event.get('payload'))
        #: Return ``tuple(owner, repository_name)``
        self.repo = event.get('repo')
        if self.repo is not None:
            self.repo = tuple(self.repo['name'].split('/'))
        #: Indicates whether the Event is public or not.
        self.public = event.get('public')

    def _repr(self):
        return '<Event [{0}]>'.format(self.type[:-5])

    @staticmethod
    def list_types():
        """List available payload types."""
        return sorted(_payload_handlers.keys())


def _commitcomment(payload):
    from .repos.comment import RepoComment
    if payload.get('comment'):
        payload['comment'] = RepoComment(payload['comment'], None)
    return payload


def _follow(payload):
    from .users import User
    if payload.get('target'):
        payload['target'] = User(payload['target'], None)
    return payload


def _forkev(payload):
    from .repos import Repository
    if payload.get('forkee'):
        payload['forkee'] = Repository(payload['forkee'], None)
    return payload


def _gist(payload):
    from .gists import Gist
    if payload.get('gist'):
        payload['gist'] = Gist(payload['gist'], None)
    return payload


def _issuecomm(payload):
    from .issues import Issue
    from .issues.comment import IssueComment
    if payload.get('issue'):
        payload['issue'] = Issue(payload['issue'], None)
    if payload.get('comment'):
        payload['comment'] = IssueComment(payload['comment'], None)
    return payload


def _issueevent(payload):
    from .issues import Issue
    if payload.get('issue'):
        payload['issue'] = Issue(payload['issue'], None)
    return payload


def _member(payload):
    from .users import User
    if payload.get('member'):
        payload['member'] = User(payload['member'], None)
    return payload


def _pullreqev(payload):
    from .pulls import PullRequest
    if payload.get('pull_request'):
        payload['pull_request'] = PullRequest(payload['pull_request'], None)
    return payload


def _pullreqcomm(payload):
    from .pulls import PullRequest, ReviewComment
    # Transform the Pull Request attribute
    pull = payload.get('pull_request')
    if pull:
        payload['pull_request'] = PullRequest(pull)

    # Transform the Comment attribute
    comment = payload.get('comment')
    if comment:
        payload['comment'] = ReviewComment(comment, None)
    return payload


def _release(payload):
    from .repos.release import Release
    release = payload.get('release')
    if release:
        payload['release'] = Release(release)
    return payload


def _team(payload):
    from .orgs import Team
    from .repos import Repository
    from .users import User
    if payload.get('team'):
        payload['team'] = Team(payload['team'], None)
    if payload.get('repo'):
        payload['repo'] = Repository(payload['repo'], None)
    if payload.get('user'):
        payload['user'] = User(payload['user'], None)
    return payload


def identity(x):
    return x


_payload_handlers = {
    'CommitCommentEvent': _commitcomment,
    'CreateEvent': identity,
    'DeleteEvent': identity,
    'FollowEvent': _follow,
    'ForkEvent': _forkev,
    'ForkApplyEvent': identity,
    'GistEvent': _gist,
    'GollumEvent': identity,
    'IssueCommentEvent': _issuecomm,
    'IssuesEvent': _issueevent,
    'MemberEvent': _member,
    'PublicEvent': lambda x: '',
    'PullRequestEvent': _pullreqev,
    'PullRequestReviewCommentEvent': _pullreqcomm,
    'PushEvent': identity,
    'ReleaseEvent': _release,
    'StatusEvent': identity,
    'TeamAddEvent': _team,
    'WatchEvent': identity,
}
