# 问题排查指南

## 加载产品方案失败的解决方案

如果您在使用投保平台时遇到"加载产品方案失败"的错误，请按照以下步骤进行排查：

### 🔍 第一步：检查 API 连接

1. **访问测试页面**
   ```
   https://glenman.github.io/insuremo-demo/test-api.html
   ```
   
2. **查看测试结果**
   - ✅ 绿色 = API 正常
   - ❌ 红色 = API 失败

### 🚨 常见问题及解决方案

#### 问题 1: CORS 跨域错误

**错误信息**：
```
Access to fetch at 'https://portal-gw.insuremo.com/...' from origin 'https://glenman.github.io' 
has been blocked by CORS policy
```

**原因**：浏览器的 CORS 策略阻止了跨域请求

**解决方案**：
- **方案 A**：联系 InsureMO 技术支持，将 `https://glenman.github.io` 添加到 CORS 白名单
- **方案 B**：使用浏览器插件临时禁用 CORS（仅用于测试）
  - Chrome: [CORS Unblock](https://chrome.google.com/webstore/detail/cors-unblock/)
  - Firefox: [CORS Everywhere](https://addons.mozilla.org/en-US/firefox/addon/cors-everywhere/)
- **方案 C**：部署到支持 CORS 的服务器，或使用后端代理

#### 问题 2: 网络连接失败

**错误信息**：
```
Failed to fetch
NetworkError when attempting to fetch resource
```

**原因**：无法连接到 InsureMO API 服务器

**排查步骤**：
1. 检查网络连接是否正常
2. 尝试访问 `https://portal-gw.insuremo.com/platform/api-orchestration-test/v1/flow/EUDemoProductList`
3. 检查防火墙是否阻止了请求
4. 尝试使用 VPN 或切换网络

#### 问题 3: 认证失败

**错误信息**：
```
HTTP 401: Unauthorized
HTTP 403: Forbidden
```

**原因**：Auth Token 无效或已过期

**解决方案**：
1. 检查 `config.js` 中的 `AUTH_TOKEN` 是否正确
2. 联系 InsureMO 获取新的 Token
3. 确认 Token 格式正确（应以 `Bearer` 开头）

#### 问题 4: API 返回错误

**错误信息**：
```
HTTP 500: Internal Server Error
API call failed
```

**原因**：InsureMO API 服务端错误

**解决方案**：
1. 检查 InsureMO 服务状态
2. 联系 InsureMO 技术支持
3. 查看 API 文档确认参数格式

### 🛠️ 本地调试

如果您想在本地调试，请按照以下步骤：

1. **克隆项目**
   ```bash
   git clone https://github.com/glenman/insuremo-demo.git
   cd insuremo-demo
   ```

2. **启动本地服务器**（必须使用 HTTP 服务器，不能直接打开文件）
   ```bash
   # 使用 Python
   python -m http.server 8000
   
   # 或使用 Node.js
   npx serve
   ```

3. **访问测试页面**
   ```
   http://localhost:8000/test-api.html
   ```

4. **查看浏览器控制台**
   - Chrome: F12 → Console 标签
   - Firefox: F12 → 控制台 标签
   - 查看详细的错误信息和网络请求

### 📊 API 测试工具

推荐使用以下工具测试 API：

1. **Postman** - 图形化 API 测试工具
   - 导入请求：`GET https://portal-gw.insuremo.com/platform/api-orchestration-test/v1/flow/EUDemoProductList`
   - 添加 Header: `Authorization: Bearer MOATbWg4aRISAep86MorzeBulKla18sq`

2. **curl** - 命令行工具
   ```bash
   curl -X GET \
     'https://portal-gw.insuremo.com/platform/api-orchestration-test/v1/flow/EUDemoPlanList?productId=375604942' \
     -H 'Authorization: Bearer MOATbWg4aRISAep86MorzeBulKla18sq'
   ```

3. **浏览器开发者工具**
   - F12 → Network 标签
   - 查看请求详情和响应

### 📞 获取帮助

如果以上方法都无法解决问题，请：

1. **收集信息**
   - 错误信息截图
   - 浏览器控制台日志
   - API 测试页面结果

2. **联系支持**
   - GitHub Issues: https://github.com/glenman/insuremo-demo/issues
   - InsureMO 技术支持

### ✅ 临时解决方案

如果急需使用，可以：

1. **使用测试模式**
   - 在 `config.js` 中添加模拟数据
   - 跳过 API 调用，直接显示示例方案

2. **部署到 InsureMO 环境**
   - 如果 InsureMO 提供了托管环境
   - 将项目部署到同一域名下，避免 CORS

---

**更新时间**: 2026-03-25
**维护者**: 小龙虾 🦞
