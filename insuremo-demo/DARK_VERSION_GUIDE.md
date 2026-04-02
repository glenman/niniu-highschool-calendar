# 暗黑版页面重写指南

## 🎨 版本信息

**版本**: Dark Mode v1.0  
**更新时间**: 2026-03-25 22:40  
**Commit**: 464ffac

---

## ✨ 主要特性

### 1. **暗黑模式设计**
- 深色背景渐变（#1a1a2e → #16213e → #0f3460）
- 毛玻璃效果（backdrop-filter）
- 紫色/蓝色渐变强调色
- 平滑动画过渡

### 2. **完全基于API文档重新实现**

**严格遵循API指导说明：**
- ✅ 使用正确的ProductId: 375604942 (TRVL01)
- ✅ 包含所有必需字段: TravelType, TripType, PlanCode
- ✅ 过滤掉有问题的方案: TRVL01PLATINUM
- ✅ 正确的API调用顺序
- ✅ 完整的5步流程

### 3. **核心流程**

```
页面初始化
├─ Step 1: EUDemoProductList (获取产品列表)
└─ 设置默认日期

用户流程
├─ Step 1: 填写信息
│  ├─ 旅行信息 (日期、类型)
│  └─ 投保人信息 (姓名、性别、生日、证件)
│
├─ Step 2: 选择方案
│  └─ EUDemoPlanList (加载可用方案)
│     ├─ Travel Classic (TRVL0120200001) ✅
│     ├─ Travel Gold (TRVL01GOLD) ✅
│     └─ Travel Platinum (TRVL01PLATINUM) ❌ 已过滤
│
├─ Step 3: 确认报价
│  └─ EUDemoTRVL01Calculate (计算保费)
│     ├─ 显示保费详情
│     └─ 显示保障项目
│
├─ Step 4: 支付投保
│  ├─ EUDemoTRVL01SaveProposal (保存提案)
│  ├─ EUDemoTRVL01BindProposal (绑定提案)
│  └─ EUDemoTRVL01PaymentCallback (支付回调)
│
└─ Step 5: 完成
   └─ 显示保单号和详情
```

---

## 🔧 技术实现

### API配置

```javascript
const CONFIG = {
    BASE_URL: 'https://portal-gw.insuremo.com/platform/api-orchestration-test',
    AUTH_TOKEN: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
};

const appState = {
    currentStep: 1,
    productId: 375604942,  // TRVL01
    productCode: 'TRVL01',
    formData: {},
    selectedPlan: null,
    calculationResult: null,
    proposalNo: null,
    policyNo: null
};
```

### 关键代码改进

#### 1. ProductId严格验证

```javascript
const payload = {
    ...appState.formData,
    ProductId: parseInt(appState.productId),  // 强制转换
    ProductCode: 'TRVL01',
    PlanCode: appState.selectedPlan.PlanCode
};

// 验证
if (!payload.ProductId || isNaN(payload.ProductId)) {
    throw new Error('ProductId无效: ' + payload.ProductId);
}
```

#### 2. 过滤有问题的方案

```javascript
plans.Plans.forEach(plan => {
    // 只显示可用的方案（TRVL01PLATINUM有问题）
    if (plan.PlanCode === 'TRVL01PLATINUM') {
        return; // 跳过
    }
    // ...渲染方案卡片
});
```

#### 3. 完整的错误处理

```javascript
async function callAPI(endpoint, method = 'GET', data = null) {
    try {
        const response = await fetch(url, options);
        const result = await response.json();

        if (!result.Success) {
            throw new Error(result.Error?.Message || 'API call failed');
        }

        return result.Data;
    } catch (error) {
        log(`❌ 失败: ${error.message}`, 'error');
        throw error;
    }
}
```

---

## 📋 UI组件

### 1. **进度条**
- 5个步骤指示器
- 当前步骤高亮
- 已完成步骤标记

### 2. **表单**
- 分组显示（旅行信息、投保人信息）
- 必填字段标记
- 输入验证

### 3. **方案卡片**
- 卡片式布局
- Hover效果
- 选中状态

### 4. **保费展示**
- 大字号显示总额
- 分解显示保费和税费
- 渐变背景

### 5. **API日志**
- 实时显示API调用
- 彩色编码（成功/失败/信息）
- 可折叠

---

## 🎯 使用指南

### 访问地址

```
https://glenman.github.io/insuremo-demo/
```

### 测试步骤

1. **填写信息**
   - 选择日期（默认已填）
   - 选择旅行类型和行程类型
   - 填写投保人信息

2. **选择方案**
   - 点击方案卡片选择
   - 查看保障项目

3. **确认报价**
   - 查看保费详情
   - 确认保障项目

4. **支付投保**
   - 选择支付方式
   - 确认支付

5. **完成**
   - 查看保单号
   - 查看保单详情

---

## 🐛 已知问题修复

### ✅ 修复的问题

1. **ProductId丢失问题**
   - 添加严格验证
   - 强制类型转换
   - 确保展开运算符顺序正确

2. **TRVL01PLATINUM方案问题**
   - 已过滤该方案
   - 只显示可用的方案

3. **API调用顺序问题**
   - 完全按照API文档实现
   - 正确的调用顺序

---

## 📝 代码规范

### 命名规范

- **JSON Body Keys**: UpperCamelCase (`ProductId`, `PlanCode`)
- **Query Parameters**: lowerCamelCase (`?productId=375604942`)
- **JavaScript变量**: camelCase (`appState`, `selectedPlan`)

### 注释规范

```javascript
// 步骤说明
// Step 1: 填写信息

// API调用
// GET /v1/flow/EUDemoProductList

// 验证逻辑
// 确保ProductId有效
```

---

## 🔍 调试技巧

### 查看API日志

页面底部有API日志面板，显示：
- 所有API调用
- 请求和响应数据
- 错误信息

### 控制台日志

所有日志同时输出到浏览器控制台：
```javascript
console.log(`[INFO]`, message);
console.log(`[ERROR]`, message);
```

---

## 📚 参考文档

- [API Consumer Guide](./docs/AI_API_CONSUMER_GUIDE.md)
- [Complete Flow Guide](./COMPLETE_FLOW_GUIDE.md)
- [API Test Report](./COMPLETE_TEST_REPORT.md)

---

## 🎉 总结

这个暗黑版页面完全基于API文档重新实现，解决了之前版本的所有问题：

✅ **ProductId正确传递**  
✅ **过滤有问题的方案**  
✅ **完整的API调用流程**  
✅ **暗黑模式UI设计**  
✅ **响应式布局**  
✅ **详细的API日志**

---

*小龙虾 🦞 2026-03-25*
