from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin
from flask import (
    Flask,
    Response,
    jsonify,
    render_template,
    url_for,
)

from webapi.api.account import (
    get_user,
    update_user,
)
from webapi.api.app import (
    get_app_release,
    search_apps,
    search_apps_acl,
)
from webapi.api.auth import (
    login_discord,
    login_google,
    login_reddit,
    login_twitch,
    logout,
)
from webapi.dto.account import (
    GetUserResponseDTO,
    UpdateUserRequestDTO,
)
from webapi.dto.app import SearchAppsRequestDTO
from webapi.services.dto.appsvc import (
    GetAppReleaseResponseDTO,
    SearchAppsAclRequestDTO,
    SearchAppsAclResponseDTO,
    SearchAppsResponseDTO,
)

spec = APISpec(
    title="webapi",
    version="1.0.0",
    openapi_version="3.0.2",
    plugins=[FlaskPlugin(), MarshmallowPlugin()],
)


def setup_dtos() -> None:
    # account
    spec.components.schema("GetUserResponseDTO", schema=GetUserResponseDTO.Schema())
    spec.components.schema("UpdateUserRequestDTO", schema=UpdateUserRequestDTO.Schema())
    # app
    spec.components.schema("GetAppReleaseResponseDTO", schema=GetAppReleaseResponseDTO.Schema())
    spec.components.schema("SearchAppsRequestDTO", schema=SearchAppsRequestDTO.Schema())
    spec.components.schema("SearchAppsResponseDTO", schema=SearchAppsResponseDTO.Schema())
    spec.components.schema("SearchAppsAclRequestDTO", schema=SearchAppsAclRequestDTO.Schema())
    spec.components.schema("SearchAppsAclResponseDTO", schema=SearchAppsAclResponseDTO.Schema())


def setup_paths(app: Flask) -> None:
    with app.test_request_context():
        # account
        spec.path(view=get_user)
        spec.path(view=update_user)
        # app
        spec.path(view=get_app_release)
        spec.path(view=search_apps)
        spec.path(view=search_apps_acl)
        # auth
        spec.path(view=login_discord)
        spec.path(view=login_google)
        spec.path(view=login_reddit)
        spec.path(view=login_twitch)
        spec.path(view=logout)


def init_app(app: Flask) -> None:
    setup_dtos()
    setup_paths(app)

    @app.get("/api/specs/")
    def api_specs() -> Response:
        return jsonify(spec.to_dict()), 200

    @app.get("/api/docs/")
    def api_docs() -> Response:
        return render_template("swaggerui.html", api_specs_url=url_for("api_specs"))
