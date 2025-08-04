"""Authentication service for GitHub OAuth."""

import secrets
import httpx
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from cryptography.fernet import Fernet
from sqlalchemy.orm import Session
from app.core.config.settings import settings
from app.models.user import User, GitHubOAuthConfig
from app.models.oauth_state import OAuthState


class AuthService:
    """Authentication service for handling GitHub OAuth."""
    
    def __init__(self):
        # 使用配置的secret_key生成加密密钥
        key = Fernet.generate_key()
        self.cipher = Fernet(key)
    
    def encrypt_token(self, token: str) -> str:
        """加密GitHub access token."""
        return self.cipher.encrypt(token.encode()).decode()
    
    def decrypt_token(self, encrypted_token: str) -> str:
        """解密GitHub access token."""
        return self.cipher.decrypt(encrypted_token.encode()).decode()
    
    def generate_state_token(self) -> str:
        """生成OAuth state token防止CSRF攻击."""
        return secrets.token_urlsafe(32)
    
    def save_state_token(self, db: Session, state: str) -> OAuthState:
        """保存state token到数据库."""
        # 设置过期时间为10分钟
        expires_at = datetime.utcnow() + timedelta(minutes=10)
        
        oauth_state = OAuthState(
            state=state,
            expires_at=expires_at
        )
        
        db.add(oauth_state)
        db.commit()
        db.refresh(oauth_state)
        return oauth_state
    
    def validate_state_token(self, db: Session, state: str) -> bool:
        """验证state token."""
        oauth_state = db.query(OAuthState).filter(
            OAuthState.state == state
        ).first()
        
        if not oauth_state:
            return False
        
        if oauth_state.is_expired():
            # 删除过期的state
            db.delete(oauth_state)
            db.commit()
            return False
        
        # 验证成功后删除state
        db.delete(oauth_state)
        db.commit()
        return True
    
    def get_github_oauth_url(self, state: str) -> str:
        """生成GitHub OAuth授权URL."""
        if not settings.github_client_id:
            raise ValueError("GitHub Client ID not configured")
            
        scopes = [
            "read:user",
            "read:email", 
            "repo",
            "read:org"
        ]
        
        params = {
            "client_id": settings.github_client_id,
            "redirect_uri": settings.github_redirect_uri,
            "scope": " ".join(scopes),
            "state": state
        }
        
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"https://github.com/login/oauth/authorize?{query_string}"
    
    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """用授权码交换access token."""
        if not settings.github_client_id or not settings.github_client_secret:
            raise ValueError("GitHub OAuth not configured")
        
        data = {
            "client_id": settings.github_client_id,
            "client_secret": settings.github_client_secret,
            "code": code,
            "redirect_uri": settings.github_redirect_uri
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://github.com/login/oauth/access_token",
                data=data,
                headers={"Accept": "application/json"},
                timeout=30
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to exchange code: {response.text}")
            
            result = response.json()
            
            if "error" in result:
                raise Exception(f"OAuth error: {result['error_description']}")
            
            return result
    
    async def get_github_user_info(self, access_token: str) -> Dict[str, Any]:
        """获取GitHub用户信息."""
        headers = {
            "Authorization": f"token {access_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.github.com/user",
                headers=headers,
                timeout=30
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to get user info: {response.text}")
            
            return response.json()
    
    def save_github_config(
        self, 
        db: Session, 
        user_id: int, 
        github_user_info: Dict[str, Any],
        token_data: Dict[str, Any]
    ) -> GitHubOAuthConfig:
        """保存GitHub OAuth配置到数据库."""
        # 加密access token
        encrypted_token = self.encrypt_token(token_data["access_token"])
        
        # 计算过期时间
        expires_at = None
        if "expires_in" in token_data:
            expires_at = datetime.utcnow() + timedelta(seconds=token_data["expires_in"])
        
        # 创建或更新配置
        config = db.query(GitHubOAuthConfig).filter(
            GitHubOAuthConfig.user_id == user_id
        ).first()
        
        if config:
            # 更新现有配置
            config.github_user_id = github_user_info["id"]
            config.github_username = github_user_info["login"]
            config.access_token = encrypted_token
            config.token_type = token_data.get("token_type", "bearer")
            config.scope = token_data.get("scope", "")
            config.expires_at = expires_at
            config.updated_at = datetime.utcnow()
        else:
            # 创建新配置
            config = GitHubOAuthConfig(
                user_id=user_id,
                github_user_id=github_user_info["id"],
                github_username=github_user_info["login"],
                access_token=encrypted_token,
                token_type=token_data.get("token_type", "bearer"),
                scope=token_data.get("scope", ""),
                expires_at=expires_at
            )
            db.add(config)
        
        db.commit()
        db.refresh(config)
        return config
    
    def get_user_github_config(self, db: Session, user_id: int) -> Optional[GitHubOAuthConfig]:
        """获取用户的GitHub配置."""
        return db.query(GitHubOAuthConfig).filter(
            GitHubOAuthConfig.user_id == user_id
        ).first()
    
    def delete_github_config(self, db: Session, user_id: int) -> bool:
        """删除用户的GitHub配置."""
        config = db.query(GitHubOAuthConfig).filter(
            GitHubOAuthConfig.user_id == user_id
        ).first()
        
        if config:
            db.delete(config)
            db.commit()
            return True
        
        return False
    
    def is_token_expired(self, config: GitHubOAuthConfig) -> bool:
        """检查token是否过期."""
        if not config.expires_at:
            return False
        
        return datetime.utcnow() > config.expires_at


# 全局认证服务实例
auth_service = AuthService() 