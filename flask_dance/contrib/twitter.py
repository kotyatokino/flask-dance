from flask import g
from werkzeug.local import LocalProxy

from flask_dance.consumer import OAuth1ConsumerBlueprint
from flask_dance.consumer import OAuth2ConsumerBlueprint
from flask_dance.consumer.requests import OAuth2Session

__maintainer__ = "David Baumgold <david@davidbaumgold.com>"


def make_twitter_blueprint(
    api_key=None,
    api_secret=None,
    *,
    redirect_url=None,
    redirect_to=None,
    login_url=None,
    authorized_url=None,
    session_class=None,
    storage=None,
    rule_kwargs=None,
):
    """
    Make a blueprint for authenticating with Twitter using OAuth 1. This requires
    an API key and API secret from Twitter. You should either pass them to
    this constructor, or make sure that your Flask application config defines
    them, using the variables :envvar:`TWITTER_OAUTH_CLIENT_KEY` and
    :envvar:`TWITTER_OAUTH_CLIENT_SECRET`.

    Args:
        api_key (str): The API key for your Twitter application
        api_secret (str): The API secret for your Twitter application
        redirect_url (str): the URL to redirect to after the authentication
            dance is complete
        redirect_to (str): if ``redirect_url`` is not defined, the name of the
            view to redirect to after the authentication dance is complete.
            The actual URL will be determined by :func:`flask.url_for`
        login_url (str, optional): the URL path for the ``login`` view.
            Defaults to ``/twitter``
        authorized_url (str, optional): the URL path for the ``authorized`` view.
            Defaults to ``/twitter/authorized``.
        session_class (class, optional): The class to use for creating a
            Requests session. Defaults to
            :class:`~flask_dance.consumer.requests.OAuth1Session`.
        storage: A token storage class, or an instance of a token storage
                class, to use for this blueprint. Defaults to
                :class:`~flask_dance.consumer.storage.session.SessionStorage`.
        rule_kwargs (dict, optional): Additional arguments that should be passed when adding
            the login and authorized routes. Defaults to ``None``.

    :rtype: :class:`~flask_dance.consumer.OAuth1ConsumerBlueprint`
    :returns: A :doc:`blueprint <flask:blueprints>` to attach to your Flask app.
    """
    twitter_bp = OAuth1ConsumerBlueprint(
        "twitter",
        __name__,
        client_key=api_key,
        client_secret=api_secret,
        base_url="https://api.twitter.com/",
        request_token_url="https://api.twitter.com/oauth/request_token",
        access_token_url="https://api.twitter.com/oauth/access_token",
        authorization_url="https://api.twitter.com/oauth/authorize",
        redirect_url=redirect_url,
        redirect_to=redirect_to,
        login_url=login_url,
        authorized_url=authorized_url,
        session_class=session_class,
        storage=storage,
        rule_kwargs=rule_kwargs,
    )
    twitter_bp.from_config["client_key"] = "TWITTER_OAUTH_CLIENT_KEY"
    twitter_bp.from_config["client_secret"] = "TWITTER_OAUTH_CLIENT_SECRET"

    @twitter_bp.before_app_request
    def set_applocal_session():
        g.flask_dance_twitter = twitter_bp.session

    return twitter_bp


twitter = LocalProxy(lambda: g.flask_dance_twitter)


def make_twitter2_blueprint(
    api_key=None,
    api_secret=None,
    *,
    scope=None,
    redirect_url=None,
    redirect_to=None,
    login_url=None,
    authorized_url=None,
    session_class=None,
    storage=None,
    rule_kwargs=None,
):
    from authlib.common.security import generate_token
    from authlib.oauth2.rfc7636 import create_s256_code_challenge
    strToken = generate_token(128)
    strChallenge = create_s256_code_challenge(strToken)

    twitter2_bp = OAuth2ConsumerBlueprint(
        "twitter2",
        __name__,
        client_id=api_key,
        client_secret=api_secret,
        scope=scope,
        base_url="https://api.twitter.com/",
        authorization_url="https://twitter.com/i/oauth2/authorize",
        token_url="https://api.twitter.com/2/oauth2/token",
        token_url_params={"code_verifier":strToken},
        redirect_url=redirect_url,
        redirect_to=redirect_to,
        login_url=login_url,
        authorized_url=authorized_url,
        session_class=session_class,
        storage=storage,
        rule_kwargs=rule_kwargs,
        authorization_url_params={"code_challenge":strChallenge,
                                  "code_challenge_method":"S256"},
        
    )

    twitter2_bp.from_config["client_id"] = "TWITTER2_OAUTH_CLIENT_ID"
    twitter2_bp.from_config["client_secret"] = "TWITTER2_OAUTH_CLIENT_SECRET"

    @twitter2_bp.before_app_request
    def set_applocal_session():
        g.flask_dance_twitter2 = twitter2_bp.session

    return twitter2_bp


twitter2 = LocalProxy(lambda: g.flask_dance_twitter2)
