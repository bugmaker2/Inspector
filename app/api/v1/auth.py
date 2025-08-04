"""OAuth authentication endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.core.database.database import get_db
from app.services.auth import auth_service
from app.models.user import User, GitHubOAuthConfig

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.get("/github")
async def github_oauth_redirect(request: Request, db: Session = Depends(get_db)):
    """重定向到GitHub OAuth页面."""
    try:
        if not auth_service:
            raise HTTPException(status_code=500, detail="OAuth service not available")
        
        # 生成state token
        state = auth_service.generate_state_token()
        
        # 保存state到数据库
        auth_service.save_state_token(db, state)
        
        # 生成GitHub OAuth URL
        oauth_url = auth_service.get_github_oauth_url(state)
        
        return RedirectResponse(url=oauth_url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OAuth redirect failed: {str(e)}")


@router.get("/github/callback")
async def github_oauth_callback(
    code: str,
    state: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """处理GitHub OAuth回调."""
    try:
        print(f"OAuth回调: code={code[:10]}..., state={state}")
        
        # 验证state token
        if not auth_service.validate_state_token(db, state):
            print("❌ State验证失败")
            frontend_url = "http://localhost:3000/settings?error=Invalid%20or%20expired%20state%20token"
            return RedirectResponse(url=frontend_url, status_code=302)
        
        print("✅ State验证通过")
        
        # 用授权码交换access token
        print("🔄 交换access token...")
        token_data = await auth_service.exchange_code_for_token(code)
        print("✅ Access token获取成功")
        
        # 获取GitHub用户信息
        print("🔄 获取GitHub用户信息...")
        github_user_info = await auth_service.get_github_user_info(
            token_data["access_token"]
        )
        print(f"✅ 用户信息获取成功: {github_user_info.get('login', 'Unknown')}")
        
        # 创建或获取用户
        github_email = github_user_info.get("email")
        if not github_email:
            # 如果GitHub没有提供邮箱，使用用户名生成邮箱
            github_email = f"{github_user_info['login']}@github.com"
            print(f"⚠️  GitHub用户没有公开邮箱，使用生成邮箱: {github_email}")
        
        # 先尝试通过GitHub用户名查找用户
        user = db.query(User).filter(
            User.username == github_user_info["login"]
        ).first()
        
        if not user:
            # 创建新用户
            user = User(
                username=github_user_info["login"],
                email=github_email
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"✅ 创建新用户: {user.username} ({user.email})")
        else:
            print(f"✅ 找到现有用户: {user.username}")
            # 更新用户邮箱（如果之前没有邮箱）
            if not user.email and github_email:
                user.email = github_email
                db.commit()
                print(f"✅ 更新用户邮箱: {user.email}")
        
        # 保存GitHub配置
        auth_service.save_github_config(
            db, user.id, github_user_info, token_data
        )
        print("✅ GitHub配置保存成功")
        
        # 重定向到前端成功页面
        frontend_url = f"http://localhost:3000/settings?github_connected=true&username={github_user_info['login']}"
        print(f"🔄 重定向到: {frontend_url}")
        return RedirectResponse(url=frontend_url, status_code=302)
        
    except Exception as e:
        print(f"❌ OAuth回调错误: {str(e)}")
        # 重定向到前端错误页面
        error_msg = str(e).replace(" ", "%20")
        frontend_url = f"http://localhost:3000/settings?error={error_msg}"
        return RedirectResponse(url=frontend_url, status_code=302)


@router.get("/users/me/github-status")
async def get_github_status(
    request: Request,
    db: Session = Depends(get_db)
):
    """获取当前用户的GitHub连接状态."""
    # TODO: 实现用户认证中间件
    # 目前返回模拟数据
    return {
        "connected": False,
        "github_username": None,
        "connected_at": None
    }


@router.delete("/users/me/github-connection")
async def disconnect_github(
    request: Request,
    db: Session = Depends(get_db)
):
    """断开GitHub连接."""
    # TODO: 实现用户认证中间件
    # 目前返回模拟数据
    return {"message": "GitHub connection removed"}


@router.get("/users/me/github-profile")
async def get_github_profile(
    request: Request,
    db: Session = Depends(get_db)
):
    """获取GitHub用户信息."""
    # TODO: 实现用户认证中间件
    # 目前返回模拟数据
    return {
        "username": None,
        "name": None,
        "email": None,
        "avatar_url": None,
        "public_repos": 0
    } 