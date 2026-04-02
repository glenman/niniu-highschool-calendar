# 🚀 快速使用指南

## 立即测试（推荐）

### 方法1：简化测试页面（最简单）

**访问地址**：
```
https://glenman.github.io/insuremo-demo/simple-test.html
```

**使用步骤**：
1. 打开页面
2. 点击"🚀 开始完整测试"按钮
3. 等待加载方案（自动进行）
4. 点击任意方案卡片
5. 点击"下一步：计算保费"
6. 查看测试结果

**特点**：
- ✅ 一键测试完整流程
- ✅ 实时日志显示
- ✅ 自动处理所有步骤
- ✅ 无需填写表单

---

### 方法2：完整投保流程

**访问地址**：
```
https://glenman.github.io/insuremo-demo/
```

**使用步骤**：

#### 第1步：填写投保信息
- 生效日期：明天
- 失效日期：一周后
- 旅行类型：选择"多次旅行"
- 行程类型：选择"休闲"
- 投保人信息：填写姓名、性别、出生日期

**提示**：
- 年龄会自动计算
- 邮箱和手机号为选填
- 填写完成后点击"下一步"

#### 第2步：选择保障方案
- 等待方案加载（2-3秒）
- 点击任意方案卡片
- 查看保障内容
- 点击"下一步：计算保费"

**可能的问题**：
- 如果看不到方案，按 F5 刷新页面
- 或访问简化测试页面

#### 第3步：报价确认
- 查看保费详情
- 确认无误后点击"确认报价并投保"

#### 第4步：支付
- 选择支付方式（模拟）
- 点击"确认支付"

#### 第5步：完成
- 查看保单信息
- 保单自动签发

---

### 方法3：调试页面

**访问地址**：
```
https://glenman.github.io/insuremo-demo/debug.html
```

**用途**：
- 自动测试所有API
- 查看详细调试信息
- 诊断连接问题

---

## ⚠️ 常见问题

### 问题1：方案加载失败

**解决方案**：
1. 访问简化测试页面：https://glenman.github.io/insuremo-demo/simple-test.html
2. 或刷新主页面（Ctrl+Shift+R / Cmd+Shift+R）
3. 或清除浏览器缓存后重试

### 问题2：看不到方案卡片

**解决方案**：
1. 等待3-5秒
2. 按 F12 查看控制台是否有错误
3. 访问调试页面检查API连接

### 问题3：CORS错误

**说明**：API已配置CORS，不应该出现此错误
**解决方案**：
- 清除浏览器缓存
- 使用无痕/隐私模式
- 尝试其他浏览器

---

## 📊 测试结果

### API状态（已验证）
- ✅ 产品列表API：正常
- ✅ 方案列表API：正常
- ✅ 保费计算API：正常
- ✅ CORS配置：已允许所有来源

### 可用方案
1. **Travel Classic** - 经典方案
2. **Travel Gold** - 黄金方案
3. **Travel Platinum** - 白金方案

### 测试数据
- 产品ID：375604942
- 产品代码：TRVL01
- 货币：EUR

---

## 🎯 推荐流程

**最简单的方式**：
```
1. 访问 https://glenman.github.io/insuremo-demo/simple-test.html
2. 点击"开始完整测试"
3. 等待方案加载
4. 选择一个方案
5. 点击下一步
6. 查看结果
```

**完整体验**：
```
1. 访问 https://glenman.github.io/insuremo-demo/
2. 填写表单（必填项标*）
3. 提交表单
4. 选择方案
5. 确认报价
6. 模拟支付
7. 获取保单
```

---

## 🔗 快速链接

- 🏠 **主页**：https://glenman.github.io/insuremo-demo/
- 🧪 **简化测试**：https://glenman.github.io/insuremo-demo/simple-test.html
- 🔧 **调试页面**：https://glenman.github.io/insuremo-demo/debug.html
- 📊 **API测试**：https://glenman.github.io/insuremo-demo/test-api.html
- 📖 **GitHub**：https://github.com/glenman/insuremo-demo

---

## 💡 提示

- ✅ 所有页面都支持PC和移动端
- ✅ 无需安装任何插件
- ✅ API已配置CORS，支持跨域
- ✅ 使用HTTPS安全连接
- ✅ 测试数据已预设，可直接使用

---

**更新时间**：2026-03-25 18:40
**维护者**：小龙虾 🦞
