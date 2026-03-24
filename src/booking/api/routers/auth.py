from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response

from booking.api.deps import (
    get_confirm_password_reset_use_case,
    get_jwt_service,
    get_login_user_use_case,
    get_refresh_access_token_use_case,
    get_register_user_use_case,
    get_request_password_reset_use_case,
    get_settings,
)
from booking.api.limiter import limiter
from booking.api.schemas.auth_schemas import (
    LoginRequest,
    PasswordResetConfirmBody,
    PasswordResetRequestBody,
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
    UserPublic,
)
from booking.application.dtos.auth_dtos import (
    ConfirmPasswordResetDTO,
    LoginUserDTO,
    RegisterUserDTO,
    RequestPasswordResetDTO,
)
from booking.application.use_cases.confirm_password_reset import (
    ConfirmPasswordResetUseCase,
)
from booking.application.use_cases.login_user import LoginUserUseCase
from booking.application.use_cases.refresh_access_token import RefreshAccessTokenUseCase
from booking.application.use_cases.register_user import RegisterUserUseCase
from booking.application.use_cases.request_password_reset import (
    RequestPasswordResetUseCase,
)
from booking.domain.exceptions.auth_errors import AuthenticationError
from booking.infrastructure.config.settings import Settings
from booking.infrastructure.security.jwt_service import JwtService

router = APIRouter(prefix="/auth", tags=["auth"])


def _set_refresh_cookie(response: Response, token: str, settings: Settings) -> None:
    response.set_cookie(
        key=settings.refresh_token_cookie_name,
        value=token,
        httponly=True,
        max_age=settings.jwt_refresh_token_expire_days * 86400,
        secure=settings.refresh_token_cookie_secure,
        samesite="lax",
        path="/",
    )


def _clear_refresh_cookie(response: Response, settings: Settings) -> None:
    response.delete_cookie(
        key=settings.refresh_token_cookie_name,
        path="/",
        samesite="lax",
    )


def _get_refresh_cookie(request: Request, settings: Settings) -> str | None:
    return request.cookies.get(settings.refresh_token_cookie_name)


@router.post("/register", response_model=RegisterResponse)
@limiter.limit("10/minute")
async def register(
    request: Request,
    body: RegisterRequest,
    response: Response,
    use_case: Annotated[RegisterUserUseCase, Depends(get_register_user_use_case)],
    jwt_service: Annotated[JwtService, Depends(get_jwt_service)],
    app_settings: Annotated[Settings, Depends(get_settings)],
) -> RegisterResponse:
    user = await use_case.execute(
        RegisterUserDTO(
            email=body.email,
            password=body.password,
            full_name=body.full_name,
        )
    )
    access = jwt_service.create_access_token(str(user.id))
    refresh = jwt_service.create_refresh_token(str(user.id))
    _set_refresh_cookie(response, refresh, app_settings)
    return RegisterResponse(
        user=UserPublic(
            id=str(user.id),
            email=str(user.email),
            full_name=user.full_name,
            is_admin=user.is_admin,
        ),
        access_token=access,
        token_type="bearer",
    )


@router.post("/login", response_model=TokenResponse)
@limiter.limit("10/minute")
async def login(
    request: Request,
    body: LoginRequest,
    response: Response,
    use_case: Annotated[LoginUserUseCase, Depends(get_login_user_use_case)],
    jwt_service: Annotated[JwtService, Depends(get_jwt_service)],
    app_settings: Annotated[Settings, Depends(get_settings)],
) -> TokenResponse:
    user = await use_case.execute(
        LoginUserDTO(email=body.email, password=body.password),
    )
    access = jwt_service.create_access_token(str(user.id))
    refresh = jwt_service.create_refresh_token(str(user.id))
    _set_refresh_cookie(response, refresh, app_settings)
    return TokenResponse(access_token=access)


@router.post("/refresh", response_model=TokenResponse)
@limiter.limit("10/minute")
async def refresh_token(
    request: Request,
    use_case: Annotated[
        RefreshAccessTokenUseCase, Depends(get_refresh_access_token_use_case)
    ],
    app_settings: Annotated[Settings, Depends(get_settings)],
) -> TokenResponse:
    cookie = _get_refresh_cookie(request, app_settings)
    if cookie is None:
        raise AuthenticationError("Missing refresh token")
    access, _user = await use_case.execute(cookie)
    return TokenResponse(access_token=access)


@router.delete("/logout")
async def logout(
    response: Response,
    app_settings: Annotated[Settings, Depends(get_settings)],
) -> dict[str, str]:
    _clear_refresh_cookie(response, app_settings)
    return {"detail": "Logged out"}


@router.post("/password-reset/request")
@limiter.limit("10/minute")
async def password_reset_request(
    request: Request,
    body: PasswordResetRequestBody,
    use_case: Annotated[
        RequestPasswordResetUseCase, Depends(get_request_password_reset_use_case)
    ],
) -> dict[str, str]:
    await use_case.execute(RequestPasswordResetDTO(email=body.email))
    return {"detail": "If the email exists, instructions will be sent"}


@router.post("/password-reset/confirm")
@limiter.limit("10/minute")
async def password_reset_confirm(
    request: Request,
    body: PasswordResetConfirmBody,
    use_case: Annotated[
        ConfirmPasswordResetUseCase, Depends(get_confirm_password_reset_use_case)
    ],
) -> dict[str, str]:
    await use_case.execute(
        ConfirmPasswordResetDTO(token=body.token, new_password=body.new_password),
    )
    return {"detail": "Password has been reset"}
