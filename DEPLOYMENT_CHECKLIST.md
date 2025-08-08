# Inspector 部署检查清单

## 服务器准备 ✅

- [ ] 服务器操作系统: Ubuntu 20.04+ 或 CentOS 8+
- [ ] 内存: 最少 2GB RAM
- [ ] 存储: 最少 10GB 可用空间
- [ ] 网络: 开放端口 80 和 443

## 软件安装 ✅

- [ ] Docker 20.10+ 已安装
- [ ] Docker Compose 2.0+ 已安装
- [ ] Git 已安装

## 域名配置 ✅

- [ ] 域名 `brianchiu.top` 指向服务器 IP
- [ ] 域名 `www.brianchiu.top` 指向服务器 IP
- [ ] DNS 解析已生效 (使用 `nslookup` 验证)

## SSL 证书 ✅

- [ ] 安装 certbot: `sudo apt-get install certbot`
- [ ] 获取 SSL 证书: `sudo certbot certonly --standalone -d brianchiu.top -d www.brianchiu.top`
- [ ] 创建 ssl 目录: `mkdir -p ssl`
- [ ] 复制证书文件:
  ```bash
  sudo cp /etc/letsencrypt/live/brianchiu.top/fullchain.pem ssl/brianchiu.top.crt
  sudo cp /etc/letsencrypt/live/brianchiu.top/privkey.pem ssl/brianchiu.top.key
  sudo chown $USER:$USER ssl/*
  chmod 600 ssl/*
  ```

## 环境配置 ✅

- [ ] 复制环境变量文件: `cp config/env.example .env`
- [ ] 编辑 `.env` 文件，设置以下变量:
  - [ ] `DB_PASSWORD` - 数据库密码
  - [ ] `OPENAI_API_KEY` - OpenAI API 密钥
  - [ ] `OPENAI_MODEL` - OpenAI 模型 (如 gpt-4)
  - [ ] `GITHUB_TOKEN` - GitHub 令牌 (可选)
  - [ ] `LINKEDIN_USERNAME` - LinkedIn 用户名 (可选)
  - [ ] `LINKEDIN_PASSWORD` - LinkedIn 密码 (可选)
  - [ ] `SMTP_HOST` - 邮件服务器 (可选)
  - [ ] `SMTP_PORT` - 邮件端口 (可选)
  - [ ] `SMTP_USER` - 邮件用户名 (可选)
  - [ ] `SMTP_PASSWORD` - 邮件密码 (可选)

## 代码部署 ✅

- [ ] 克隆代码: `git clone https://github.com/bugmaker2/Inspector.git`
- [ ] 进入项目目录: `cd Inspector`
- [ ] 给部署脚本执行权限: `chmod +x deploy.sh`
- [ ] 给 SSL 续期脚本执行权限: `chmod +x renew_ssl.sh`

## 启动服务 ✅

- [ ] 启动所有服务: `./deploy.sh start`
- [ ] 检查服务状态: `./deploy.sh status`
- [ ] 查看服务日志: `./deploy.sh logs`

## 验证部署 ✅

- [ ] 健康检查: `curl https://brianchiu.top/health`
- [ ] 前端访问: `curl -I https://brianchiu.top`
- [ ] 浏览器访问: 打开 `https://brianchiu.top`
- [ ] 检查 SSL 证书: 浏览器显示安全连接
- [ ] 测试 API 功能: 访问各个页面和功能

## 监控和维护 ✅

- [ ] 设置 SSL 证书自动续期:
  ```bash
  # 编辑 crontab
  crontab -e
  
  # 添加以下行 (每天凌晨 2 点检查续期)
  0 2 * * * /path/to/your/inspector/renew_ssl.sh
  ```
- [ ] 更新 `renew_ssl.sh` 中的 `PROJECT_DIR` 路径
- [ ] 设置数据库备份: `./deploy.sh backup`
- [ ] 配置日志监控
- [ ] 设置系统监控告警

## 安全配置 ✅

- [ ] 配置防火墙只开放必要端口
- [ ] 使用强密码保护数据库和 API 密钥
- [ ] 定期更新系统和依赖包
- [ ] 监控异常访问日志
- [ ] 配置备份策略

## 性能优化 ✅

- [ ] 配置 nginx 缓存策略
- [ ] 启用 gzip 压缩
- [ ] 优化数据库查询
- [ ] 配置静态资源缓存
- [ ] 监控资源使用情况

## 故障排除 ✅

- [ ] 了解常见问题解决方案
- [ ] 准备回滚方案
- [ ] 记录部署日志
- [ ] 设置监控告警
- [ ] 准备技术支持联系方式

## 部署完成 ✅

- [ ] 所有服务正常运行
- [ ] 域名可以正常访问
- [ ] SSL 证书有效
- [ ] 功能测试通过
- [ ] 性能满足要求
- [ ] 安全配置到位
- [ ] 监控告警设置完成
- [ ] 备份策略实施
- [ ] 文档更新完成

---

## 快速部署命令

```bash
# 1. 服务器准备
sudo apt-get update
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 2. 获取 SSL 证书
sudo apt-get install certbot
sudo certbot certonly --standalone -d brianchiu.top -d www.brianchiu.top

# 3. 部署应用
git clone https://github.com/bugmaker2/Inspector.git
cd Inspector
mkdir -p ssl
sudo cp /etc/letsencrypt/live/brianchiu.top/fullchain.pem ssl/brianchiu.top.crt
sudo cp /etc/letsencrypt/live/brianchiu.top/privkey.pem ssl/brianchiu.top.key
sudo chown $USER:$USER ssl/*
chmod 600 ssl/*
cp config/env.example .env
# 编辑 .env 文件设置环境变量
chmod +x deploy.sh
./deploy.sh start
```

## 验证命令

```bash
# 检查服务状态
./deploy.sh status

# 健康检查
curl https://brianchiu.top/health

# 查看日志
./deploy.sh logs

# 备份数据库
./deploy.sh backup
```
