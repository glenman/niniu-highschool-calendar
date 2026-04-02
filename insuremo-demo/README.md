# 全球旅行险投保出单平台

<div align="center">

✈️ **InsureMO Travel Insurance Platform**

一个现代化的全球旅行险在线投保平台，支持 PC 端和移动端

[在线演示](#) | [API 文档](./docs/AI_API_CONSUMER_GUIDE.md) | [测试报告](./API_TEST_REPORT.md)

</div>

---

## 📋 项目简介

这是一个基于 InsureMO P2C API 开发的全球旅行险投保出单平台，实现了从填写投保信息到保单签发的完整流程。

### ✨ 主要特性

- 🎯 **完整投保流程** - 5步完成投保出单
  1. 填写投保信息
  2. 选择保障方案
  3. 报价确认
  4. 支付投保
  5. 保单签发

- 📱 **响应式设计** - 完美支持 PC 端和移动端
- 🎨 **现代化 UI** - 使用现代化设计语言，用户体验优秀
- ⚡ **实时校验** - 前端字段校验，提供即时反馈
- 🔒 **安全可靠** - 使用 Bearer Token 认证，数据传输加密

---

## 🚀 快速开始

### 在线访问

直接访问 GitHub Pages 部署的在线版本：

```
https://glenman.github.io/insuremo-demo/
```

### 本地运行

1. **克隆项目**

```bash
git clone https://github.com/glenman/insuremo-demo.git
cd insuremo-demo
```

2. **直接打开**

由于是纯前端项目，直接在浏览器中打开 `index.html` 即可：

```bash
open index.html
```

或者使用简单的 HTTP 服务器：

```bash
# 使用 Python
python -m http.server 8000

# 或使用 Node.js
npx serve
```

3. **访问应用**

打开浏览器访问 `http://localhost:8000`

---

## 📖 使用指南

### 投保流程

#### 第 1 步：填写投保信息

填写以下必填信息：

- **保障期间**
  - 生效日期
  - 失效日期
  - 旅行类型（单次/多次）
  - 行程类型（商务/休闲/留学）

- **投保人信息**
  - 姓名
  - 性别
  - 出生日期
  - 年龄（自动计算）
  - 电子邮箱（选填）
  - 手机号码（选填）
  - 证件号码（选填）
  - 证件类型（选填）

#### 第 2 步：选择保障方案

系统会自动加载可用的保障方案，包括：

- **Travel Classic** - 经典方案
- **Travel Gold** - 黄金方案
- **Travel Platinum** - 白金方案

每个方案显示：
- 保障内容
- 保额
- 保费

#### 第 3 步：报价确认

查看详细的报价信息：
- 保费明细
- 税费
- 总保费
- 保障内容详情

#### 第 4 步：支付投保

选择支付方式：
- 信用卡
- 支付宝
- 微信支付

#### 第 5 步：完成出单

支付成功后，系统自动签发保单，显示：
- 保单号码
- 投保单号
- 保单详情
- 下载保单（开发中）

---

## 🛠️ 技术栈

### 前端

- **HTML5** - 语义化标签
- **CSS3** - 响应式设计，Flexbox/Grid 布局
- **JavaScript (ES6+)** - 原生 JS，无框架依赖
- **Google Fonts** - Inter 字体

### API

- **InsureMO P2C API** - 保险产品 API 平台
- **RESTful API** - 标准 REST 接口
- **Bearer Token** - 认证机制

### 功能特性

- 📱 响应式设计（Mobile-first）
- ✅ 实时表单校验
- 🎨 动画效果
- 🔔 Toast 通知
- ⏳ Loading 状态
- 📊 进度指示器

---

## 📁 项目结构

```
insuremo-demo/
├── index.html              # 主页面
├── styles.css              # 样式文件
├── app.js                  # 主应用逻辑
├── api.js                  # API 封装
├── config.js               # 配置文件
├── README.md               # 项目说明
├── API_TEST_REPORT.md      # API 测试报告
└── docs/
    └── AI_API_CONSUMER_GUIDE.md  # API 使用指南
```

---

## 🔧 配置说明

### API 配置

在 `config.js` 中配置 API 信息：

```javascript
const CONFIG = {
    BASE_URL: 'https://portal-gw.insuremo.com/platform/api-orchestration-test',
    AUTH_TOKEN: 'YOUR_AUTH_TOKEN',
    PRODUCT: {
        CODE: 'TRVL01',
        ID: 375604942,
        NAME: 'Travel Insurance'
    }
};
```

### 产品信息

- **产品代码**: TRVL01
- **产品 ID**: 375604942
- **产品名称**: Travel Insurance [BizOps Asset]

---

## 📊 API 端点

### 公共 API

| API | 方法 | 说明 |
|-----|------|------|
| `/v1/flow/EUDemoProductList` | GET | 获取产品列表 |
| `/v1/flow/EUDemoPolicySchema` | GET | 获取表单 Schema |
| `/v1/flow/EUDemoPlanList` | GET | 获取方案列表 |

### 旅行险 API

| API | 方法 | 说明 |
|-----|------|------|
| `/v1/flow/EUDemoTRVL01Calculate` | POST | 计算保费 |
| `/v1/flow/EUDemoTRVL01SaveProposal` | POST | 保存提案 |
| `/v1/flow/EUDemoTRVL01BindProposal` | POST | 绑定提案 |
| `/v1/flow/EUDemoTRVL01PaymentCallback` | POST | 支付回调 |
| `/v1/flow/EUDemoTRVL01Policy` | GET | 获取保单 |

---

## ✅ 测试报告

详细的 API 测试报告请查看 [API_TEST_REPORT.md](./API_TEST_REPORT.md)

### 测试结果

- ✅ 产品列表 API
- ✅ Schema 获取 API
- ✅ 方案列表 API
- ✅ 保费计算 API
- ✅ 完整投保流程

---

## 🎯 核心功能

### 表单校验

- **必填字段校验** - 所有必填字段标记 `*` 号
- **格式校验** - 邮箱、手机号格式验证
- **逻辑校验** - 日期范围、年龄范围验证
- **实时反馈** - 输入时即时校验

### 数据流程

```
用户输入 → 前端校验 → API 调用 → 数据处理 → 界面渲染
```

### 状态管理

使用全局状态管理整个投保流程：

```javascript
{
    currentStep: 1-5,
    formData: {},
    selectedPlan: {},
    calculationResult: {},
    proposalNo: '',
    policyNo: ''
}
```

---

## 🌐 浏览器支持

- ✅ Chrome (推荐)
- ✅ Firefox
- ✅ Safari
- ✅ Edge
- ⚠️ IE (不支持)

---

## 📝 开发说明

### 代码规范

- 使用 ES6+ 语法
- 函数式编程风格
- 清晰的注释
- 统一的命名规范

### 扩展开发

#### 添加新的保险产品

1. 在 `config.js` 中添加产品配置
2. 在 `api.js` 中添加对应的 API 方法
3. 在 `app.js` 中实现业务逻辑

#### 自定义样式

修改 `styles.css` 中的 CSS 变量：

```css
:root {
    --primary-color: #2563eb;
    --secondary-color: #64748b;
    --success-color: #10b981;
    --error-color: #ef4444;
}
```

---

## 🔐 安全说明

- ⚠️ **Auth Token** 在生产环境中应从后端获取
- ⚠️ **HTTPS** 生产环境必须使用 HTTPS
- ⚠️ **敏感数据** 不应在前端存储敏感信息

---

## 📄 License

MIT License

---

## 👥 作者

- **开发者**: 小龙虾 🦞
- **API 提供商**: InsureMO
- **创建日期**: 2026-03-25

---

## 🙏 致谢

感谢 InsureMO 提供的 P2C API 平台，使得保险产品的在线投保变得简单高效。

---

<div align="center">

**Made with ❤️ by 小龙虾**

</div>
